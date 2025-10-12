"""Main word processor application."""

import sys
import os
os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
                             QFileDialog, QMessageBox, QSpinBox,
                             QToolBar, QColorDialog, QDoubleSpinBox)
from PyQt5.QtGui import (QFont, QTextCharFormat, QColor, QTextCursor, 
                         QTextListFormat, QTextBlockFormat)
from PyQt5.QtCore import Qt
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

from spell_checker import SpellCheckHighlighter, SpellCheckTextEdit
from font_manager import CustomFontComboBox, FavoriteFontsDialog, FontSettingsManager
from find_replace import FindReplaceDialog


class WordProcessor(QMainWindow):
    """Main word processor application window."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.find_dialog = None
        self.font_manager = FontSettingsManager()
        self.favorite_fonts = self.font_manager.load_favorites()
        self.spell_check_enabled = True
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Word Processor')
        self.setGeometry(100, 100, 1000, 600)
        
        # Create the text editor with spell checking
        self.text_edit = SpellCheckTextEdit()
        self.text_edit.setFontPointSize(12)
        self.setCentralWidget(self.text_edit)
        
        # Set up spell checker
        try:
            self.highlighter = SpellCheckHighlighter(self.text_edit.document())
            self.text_edit.set_spell_checker(self.highlighter)
        except Exception as e:
            print(f"Spell checker initialization failed: {e}")
            QMessageBox.warning(self, 'Spell Check', 
                              'Spell checker could not be initialized.')
            self.highlighter = None
            self.spell_check_enabled = False
        
        # Create menus and toolbars
        self.create_menu_bar()
        self.create_format_toolbar()
        self.create_paragraph_toolbar()
        
        self.show()
    
    def create_format_toolbar(self):
        """Create the text formatting toolbar."""
        toolbar = QToolBar('Format Toolbar')
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Font family selector
        self.font_combo = CustomFontComboBox(self)
        self.font_combo.set_favorites(self.favorite_fonts)
        toolbar.addWidget(self.font_combo)
        
        # Add to favorites button
        fav_btn = QAction('★', self)
        fav_btn.setToolTip('Add current font to favorites')
        fav_btn.triggered.connect(self.add_current_font_to_favorites)
        toolbar.addAction(fav_btn)
        
        # Manage favorites button
        manage_fav_btn = QAction('Manage Favorites', self)
        manage_fav_btn.triggered.connect(self.manage_favorites)
        toolbar.addAction(manage_fav_btn)
        
        # Font size selector
        self.font_size = QSpinBox()
        self.font_size.setValue(12)
        self.font_size.setMinimum(8)
        self.font_size.setMaximum(72)
        self.font_size.valueChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size)
        
        toolbar.addSeparator()
        
        # Bold button
        bold_action = QAction('B', self)
        bold_action.setCheckable(True)
        bold_action.setShortcut('Ctrl+B')
        bold_action.triggered.connect(self.toggle_bold)
        bold_action.setToolTip('Bold (Ctrl+B)')
        toolbar.addAction(bold_action)
        self.bold_action = bold_action
        
        # Italic button
        italic_action = QAction('I', self)
        italic_action.setCheckable(True)
        italic_action.setShortcut('Ctrl+I')
        italic_action.triggered.connect(self.toggle_italic)
        italic_action.setToolTip('Italic (Ctrl+I)')
        toolbar.addAction(italic_action)
        self.italic_action = italic_action
        
        # Underline button
        underline_action = QAction('U', self)
        underline_action.setCheckable(True)
        underline_action.setShortcut('Ctrl+U')
        underline_action.triggered.connect(self.toggle_underline)
        underline_action.setToolTip('Underline (Ctrl+U)')
        toolbar.addAction(underline_action)
        self.underline_action = underline_action
        
        # Strikethrough button
        strikethrough_action = QAction('S', self)
        strikethrough_action.setCheckable(True)
        strikethrough_action.setShortcut('Ctrl+Shift+X')
        strikethrough_action.triggered.connect(self.toggle_strikethrough)
        strikethrough_action.setToolTip('Strikethrough (Ctrl+Shift+X)')
        toolbar.addAction(strikethrough_action)
        self.strikethrough_action = strikethrough_action
        
        toolbar.addSeparator()
        
        # Text color button
        color_action = QAction('Text Color', self)
        color_action.triggered.connect(self.change_text_color)
        toolbar.addAction(color_action)
        
        # Highlight color button
        highlight_action = QAction('Highlight', self)
        highlight_action.triggered.connect(self.change_highlight_color)
        toolbar.addAction(highlight_action)
        
        self.text_edit.cursorPositionChanged.connect(self.update_format_buttons)
    
    def create_paragraph_toolbar(self):
        """Create the paragraph formatting toolbar."""
        toolbar = QToolBar('Paragraph Toolbar')
        toolbar.setMovable(False)
        self.addToolBar(toolbar)
        
        # Alignment buttons
        align_left = QAction('Left', self)
        align_left.setCheckable(True)
        align_left.triggered.connect(lambda: self.set_alignment(Qt.AlignLeft))
        toolbar.addAction(align_left)
        self.align_left_action = align_left
        
        align_center = QAction('Center', self)
        align_center.setCheckable(True)
        align_center.triggered.connect(lambda: self.set_alignment(Qt.AlignCenter))
        toolbar.addAction(align_center)
        self.align_center_action = align_center
        
        align_right = QAction('Right', self)
        align_right.setCheckable(True)
        align_right.triggered.connect(lambda: self.set_alignment(Qt.AlignRight))
        toolbar.addAction(align_right)
        self.align_right_action = align_right
        
        align_justify = QAction('Justify', self)
        align_justify.setCheckable(True)
        align_justify.triggered.connect(lambda: self.set_alignment(Qt.AlignJustify))
        toolbar.addAction(align_justify)
        self.align_justify_action = align_justify
        
        toolbar.addSeparator()
        
        # List buttons
        bullet_action = QAction('Bullets', self)
        bullet_action.triggered.connect(self.toggle_bullet_list)
        toolbar.addAction(bullet_action)
        
        numbered_action = QAction('Numbering', self)
        numbered_action.triggered.connect(self.toggle_numbered_list)
        toolbar.addAction(numbered_action)
        
        toolbar.addSeparator()
        
        # Line spacing
        toolbar.addWidget(QDoubleSpinBox() if False else __import__('PyQt5.QtWidgets', fromlist=['QLabel']).QLabel(' Line Spacing: '))
        self.line_spacing = QDoubleSpinBox()
        self.line_spacing.setValue(1.0)
        self.line_spacing.setMinimum(0.5)
        self.line_spacing.setMaximum(3.0)
        self.line_spacing.setSingleStep(0.1)
        self.line_spacing.valueChanged.connect(self.change_line_spacing)
        toolbar.addWidget(self.line_spacing)
        
        self.text_edit.cursorPositionChanged.connect(self.update_paragraph_buttons)
    
    def create_menu_bar(self):
        """Create the menu bar."""
        menubar = self.menuBar()
        
        # File Menu
        file_menu = menubar.addMenu('File')
        self._add_file_menu_actions(file_menu)
        
        # Edit Menu
        edit_menu = menubar.addMenu('Edit')
        self._add_edit_menu_actions(edit_menu)
        
        # Format Menu
        format_menu = menubar.addMenu('Format')
        self._add_format_menu_actions(format_menu)
        
        # Tools Menu
        tools_menu = menubar.addMenu('Tools')
        self._add_tools_menu_actions(tools_menu)
    
    def _add_file_menu_actions(self, menu):
        """Add actions to File menu."""
        new_action = QAction('New', self)
        new_action.setShortcut('Ctrl+N')
        new_action.triggered.connect(self.new_file)
        menu.addAction(new_action)
        
        open_action = QAction('Open', self)
        open_action.setShortcut('Ctrl+O')
        open_action.triggered.connect(self.open_file)
        menu.addAction(open_action)
        
        save_action = QAction('Save', self)
        save_action.setShortcut('Ctrl+S')
        save_action.triggered.connect(self.save_file)
        menu.addAction(save_action)
        
        save_as_action = QAction('Save As...', self)
        save_as_action.setShortcut('Ctrl+Shift+S')
        save_as_action.triggered.connect(self.save_file_as)
        menu.addAction(save_as_action)
        
        menu.addSeparator()
        
        print_preview_action = QAction('Print Preview...', self)
        print_preview_action.triggered.connect(self.print_preview)
        menu.addAction(print_preview_action)
        
        print_action = QAction('Print...', self)
        print_action.setShortcut('Ctrl+P')
        print_action.triggered.connect(self.print_document)
        menu.addAction(print_action)
        
        menu.addSeparator()
        
        exit_action = QAction('Exit', self)
        exit_action.setShortcut('Ctrl+Q')
        exit_action.triggered.connect(self.close)
        menu.addAction(exit_action)
    
    def _add_edit_menu_actions(self, menu):
        """Add actions to Edit menu."""
        undo_action = QAction('Undo', self)
        undo_action.setShortcut('Ctrl+Z')
        undo_action.triggered.connect(self.text_edit.undo)
        menu.addAction(undo_action)
        
        redo_action = QAction('Redo', self)
        redo_action.setShortcut('Ctrl+Y')
        redo_action.triggered.connect(self.text_edit.redo)
        menu.addAction(redo_action)
        
        menu.addSeparator()
        
        cut_action = QAction('Cut', self)
        cut_action.setShortcut('Ctrl+X')
        cut_action.triggered.connect(self.text_edit.cut)
        menu.addAction(cut_action)
        
        copy_action = QAction('Copy', self)
        copy_action.setShortcut('Ctrl+C')
        copy_action.triggered.connect(self.text_edit.copy)
        menu.addAction(copy_action)
        
        paste_action = QAction('Paste', self)
        paste_action.setShortcut('Ctrl+V')
        paste_action.triggered.connect(self.text_edit.paste)
        menu.addAction(paste_action)
        
        menu.addSeparator()
        
        find_action = QAction('Find and Replace...', self)
        find_action.setShortcut('Ctrl+F')
        find_action.triggered.connect(self.show_find_replace)
        menu.addAction(find_action)
    
    def _add_format_menu_actions(self, menu):
        """Add actions to Format menu."""
        bold_action = QAction('Bold', self)
        bold_action.setShortcut('Ctrl+B')
        bold_action.triggered.connect(self.toggle_bold)
        menu.addAction(bold_action)
        
        italic_action = QAction('Italic', self)
        italic_action.setShortcut('Ctrl+I')
        italic_action.triggered.connect(self.toggle_italic)
        menu.addAction(italic_action)
        
        underline_action = QAction('Underline', self)
        underline_action.setShortcut('Ctrl+U')
        underline_action.triggered.connect(self.toggle_underline)
        menu.addAction(underline_action)