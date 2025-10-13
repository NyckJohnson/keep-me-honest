"""Main word processor application."""

import sys
import os
os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PyQt5.QtWidgets import (QApplication, QMainWindow, QAction, 
                             QFileDialog, QMessageBox, QSpinBox,
                             QToolBar, QColorDialog, QDoubleSpinBox)
from PyQt5.QtGui import (QFont, QTextCharFormat, QColor, QTextCursor, 
                         QTextListFormat, QTextBlockFormat)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

try:
    from spell_checker import SpellCheckHighlighter, SpellCheckTextEdit
    from font_manager import CustomFontComboBox, FavoriteFontsDialog, FontSettingsManager
    from find_replace import FindReplaceDialog
    from writing_checker import WritingChecker
    from writing_checker_ui import WritingCheckerDock, WritingHighlighter
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class WordProcessor(QMainWindow):
    """Main word processor application window."""
    
    def __init__(self):
        super().__init__()
        self.current_file = None
        self.find_dialog = None
        self.font_manager = FontSettingsManager()
        self.favorite_fonts = self.font_manager.load_favorites()
        self.spell_check_enabled = True
        self.writing_checker = WritingChecker()
        self.writing_checker_visible = False
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.run_writing_check)
        self.check_timer.setInterval(1000)  # Check every 1 second
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Keep Me Honest')
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
        
        # Create writing checker dock
        self.writing_checker_dock = WritingCheckerDock(self)
        self.writing_checker_dock.check_type_changed.connect(self.on_check_type_changed)
        self.writing_checker_dock.ignore_issue.connect(self.on_ignore_issue)
        self.writing_checker_dock.add_cinnamon_word.connect(self.on_add_cinnamon_word)
        self.writing_checker_dock.remove_cinnamon_word.connect(self.on_remove_cinnamon_word)
        self.writing_checker_dock.refresh_requested.connect(self.run_writing_check)
        self.addDockWidget(Qt.RightDockWidgetArea, self.writing_checker_dock)
        self.writing_checker_dock.hide()
        
        # Connect text changes for writing checker
        self.text_edit.textChanged.connect(self.schedule_writing_check)
        self.text_edit.selectionChanged.connect(self.update_selection_readability)
        
        self.show()
    
    # Writing checker methods (must be here, before first use in __init__)
    def toggle_writing_checker(self):
        """Toggle writing checker visibility."""
        self.writing_checker_visible = not self.writing_checker_visible
        if self.writing_checker_visible:
            self.writing_checker_dock.show()
            self.run_writing_check()
            self.check_timer.start()
        else:
            self.writing_checker_dock.hide()
            self.check_timer.stop()
            WritingHighlighter.highlight_issues(self.text_edit, [])
        self.writing_check_action.setChecked(self.writing_checker_visible)
    
    def schedule_writing_check(self):
        """Schedule a writing check (debounced)."""
        if self.writing_checker_visible:
            self.check_timer.stop()
            self.check_timer.start()
    
    def run_writing_check(self):
        """Run the writing checker and update highlights."""
        self.check_timer.stop()
        
        if not self.readability or not self.writing_checker:
            return
        
        text = self.text_edit.toPlainText()
        issues = self.writing_checker.check_text(text)
        
        # Analyze readability of entire document
        analysis = self.readability.analyze(text)
        readability_text = self.readability.format_analysis(analysis)
        self.writing_checker_dock.set_readability(readability_text)
        
        # Analyze selection if text is selected
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            selection_analysis = self.readability.analyze(selected_text)
            selection_readability = self.readability.format_analysis_compact(selection_analysis)
            self.writing_checker_dock.set_selection_readability(
                f"✓ {selection_readability}"
            )
        else:
            self.writing_checker_dock.set_selection_readability(
                "(Select text to analyze)"
            )
        
        self.writing_checker_dock.set_issues(issues)
        WritingHighlighter.highlight_issues(self.text_edit, issues)
    
    def update_selection_readability(self):
        """Update readability analysis for selected text."""
        if not self.writing_checker_visible:
            return
        
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            selection_analysis = self.readability.analyze(selected_text)
            selection_readability = self.readability.format_analysis_compact(selection_analysis)
            self.writing_checker_dock.set_selection_readability(
                f"✓ {selection_readability}"
            )
        else:
            self.writing_checker_dock.set_selection_readability(
                "(Select text to analyze)"
            )
    
    def on_check_type_changed(self, check_type: str, enabled: bool):
        """Handle check type toggle."""
        self.writing_checker.set_check_enabled(check_type, enabled)
        self.run_writing_check()
    
    def on_ignore_issue(self, issue_index: int):
        """Handle ignoring an issue by removing its highlight."""
        issues = self.writing_checker_dock.issues
        if 0 <= issue_index < len(issues):
            removed_issue = issues.pop(issue_index)
            WritingHighlighter.highlight_issues(self.text_edit, issues)
            self.writing_checker_dock.set_issues(issues)
            if issues:
                next_index = min(issue_index, len(issues) - 1)
                self.writing_checker_dock.show_issue(next_index)
    
    def on_add_cinnamon_word(self, word: str):
        """Add a word to cinnamon words list."""
        self.writing_checker.add_cinnamon_word(word)
        self.writing_checker_dock.set_cinnamon_words(self.writing_checker.cinnamon_words)
        self.run_writing_check()
    
    def on_remove_cinnamon_word(self, word: str):
        """Remove a word from cinnamon words list."""
        self.writing_checker.remove_cinnamon_word(word)
        self.writing_checker_dock.set_cinnamon_words(self.writing_checker.cinnamon_words)
        self.run_writing_check()
    
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
        
        strikethrough_action = QAction('Strikethrough', self)
        strikethrough_action.setShortcut('Ctrl+Shift+X')
        strikethrough_action.triggered.connect(self.toggle_strikethrough)
        menu.addAction(strikethrough_action)
        
        menu.addSeparator()
        
        color_action = QAction('Text Color...', self)
        color_action.triggered.connect(self.change_text_color)
        menu.addAction(color_action)
        
        highlight_action = QAction('Highlight Color...', self)
        highlight_action.triggered.connect(self.change_highlight_color)
        menu.addAction(highlight_action)
        
        menu.addSeparator()
        
        align_submenu = menu.addMenu('Alignment')
        
        align_left_menu = QAction('Align Left', self)
        align_left_menu.triggered.connect(lambda: self.set_alignment(Qt.AlignLeft))
        align_submenu.addAction(align_left_menu)
        
        align_center_menu = QAction('Align Center', self)
        align_center_menu.triggered.connect(lambda: self.set_alignment(Qt.AlignCenter))
        align_submenu.addAction(align_center_menu)
        
        align_right_menu = QAction('Align Right', self)
        align_right_menu.triggered.connect(lambda: self.set_alignment(Qt.AlignRight))
        align_submenu.addAction(align_right_menu)
        
        align_justify_menu = QAction('Justify', self)
        align_justify_menu.triggered.connect(lambda: self.set_alignment(Qt.AlignJustify))
        align_submenu.addAction(align_justify_menu)
        
        menu.addSeparator()
        
        bullet_menu_action = QAction('Bullet List', self)
        bullet_menu_action.triggered.connect(self.toggle_bullet_list)
        menu.addAction(bullet_menu_action)
        
        numbered_menu_action = QAction('Numbered List', self)
        numbered_menu_action.triggered.connect(self.toggle_numbered_list)
        menu.addAction(numbered_menu_action)
    
    def _add_tools_menu_actions(self, menu):
        """Add actions to Tools menu."""
        self.spell_check_action = QAction('Enable Spell Check', self)
        self.spell_check_action.setCheckable(True)
        self.spell_check_action.setChecked(self.spell_check_enabled)
        self.spell_check_action.triggered.connect(self.toggle_spell_check)
        menu.addAction(self.spell_check_action)
        
        menu.addSeparator()
        
        self.writing_check_action = QAction('Writing Checker', self)
        self.writing_check_action.setCheckable(True)
        self.writing_check_action.setChecked(False)
        self.writing_check_action.triggered.connect(self.toggle_writing_checker)
        menu.addAction(self.writing_check_action)
    
    # Font methods
    def change_font(self, font):
        """Change the current font."""
        self.text_edit.setCurrentFont(font)
    
    def change_font_size(self, size):
        """Change the font size."""
        self.text_edit.setFontPointSize(size)
    
    def add_current_font_to_favorites(self):
        """Add current font to favorites."""
        current_font = self.font_combo.currentFont().family()
        if current_font not in self.font_combo.favorites:
            self.font_combo.add_to_favorites(current_font)
            QMessageBox.information(self, 'Added to Favorites', 
                                  f'"{current_font}" has been added to your favorites!')
        else:
            QMessageBox.information(self, 'Already a Favorite', 
                                  f'"{current_font}" is already in your favorites.')
    
    def manage_favorites(self):
        """Open dialog to manage favorite fonts."""
        dialog = FavoriteFontsDialog(self.font_combo.favorites, self)
        if dialog.exec_() == QDialog.Accepted:
            from PyQt5.QtWidgets import QDialog
            new_favorites = dialog.get_favorites()
            self.font_combo.set_favorites(new_favorites)
            self.save_favorites()
    
    def save_favorites(self):
        """Save favorite fonts."""
        self.font_manager.save_favorites(self.font_combo.favorites)
    
    # Text formatting methods
    def toggle_bold(self):
        """Toggle bold formatting."""
        fmt = self.text_edit.currentCharFormat()
        if fmt.fontWeight() == QFont.Bold:
            fmt.setFontWeight(QFont.Normal)
        else:
            fmt.setFontWeight(QFont.Bold)
        self.text_edit.setCurrentCharFormat(fmt)
    
    def toggle_italic(self):
        """Toggle italic formatting."""
        state = self.text_edit.fontItalic()
        self.text_edit.setFontItalic(not state)
    
    def toggle_underline(self):
        """Toggle underline formatting."""
        state = self.text_edit.fontUnderline()
        self.text_edit.setFontUnderline(not state)
    
    def toggle_strikethrough(self):
        """Toggle strikethrough formatting."""
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.text_edit.setCurrentCharFormat(fmt)
    
    def change_text_color(self):
        """Change text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_edit.setTextColor(color)
    
    def change_highlight_color(self):
        """Change text highlight color."""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = self.text_edit.currentCharFormat()
            fmt.setBackground(color)
            self.text_edit.setCurrentCharFormat(fmt)
    
    # Paragraph formatting methods
    def set_alignment(self, alignment):
        """Set text alignment."""
        self.text_edit.setAlignment(alignment)
    
    def toggle_bullet_list(self):
        """Toggle bullet list formatting."""
        cursor = self.text_edit.textCursor()
        current_list = cursor.currentList()
        
        if current_list:
            cursor.currentList().remove(cursor.block())
        else:
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDisc)
            cursor.createList(list_format)
    
    def toggle_numbered_list(self):
        """Toggle numbered list formatting."""
        cursor = self.text_edit.textCursor()
        current_list = cursor.currentList()
        
        if current_list:
            cursor.currentList().remove(cursor.block())
        else:
            list_format = QTextListFormat()
            list_format.setStyle(QTextListFormat.ListDecimal)
            cursor.createList(list_format)
    
    def change_line_spacing(self, value):
        """Change line spacing."""
        cursor = self.text_edit.textCursor()
        block_format = cursor.blockFormat()
        block_format.setLineHeight(value * 100, QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(block_format)
    
    # Spell check methods
    def toggle_spell_check(self):
        """Toggle spell checking on/off."""
        if self.highlighter:
            self.spell_check_enabled = not self.spell_check_enabled
            self.highlighter.set_enabled(self.spell_check_enabled)
            self.spell_check_action.setChecked(self.spell_check_enabled)
    
    # Find and Replace methods
    def show_find_replace(self):
        """Show find and replace dialog."""
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(self)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()
    
    # File operations
    def new_file(self):
        """Create a new document."""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                                        'Do you want to save changes to the current document?',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        self.text_edit.clear()
        self.current_file = None
        self.setWindowTitle('Keep Me Honest - Untitled')
    
    def open_file(self):
        """Open a file."""
        filename, _ = QFileDialog.getOpenFileName(self, 'Open File', '',
                                                  'HTML Files (*.html);;Text Files (*.txt);;All Files (*)')
        if filename:
            try:
                with open(filename, 'r') as f:
                    content = f.read()
                    if filename.endswith('.html'):
                        self.text_edit.setHtml(content)
                    else:
                        self.text_edit.setPlainText(content)
                    self.current_file = filename
                    self.setWindowTitle(f'Keep Me Honest - {filename}')
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not open file: {str(e)}')
    
    def save_file(self):
        """Save the current file."""
        if self.current_file:
            try:
                with open(self.current_file, 'w') as f:
                    if self.current_file.endswith('.html'):
                        f.write(self.text_edit.toHtml())
                    else:
                        f.write(self.text_edit.toPlainText())
                self.text_edit.document().setModified(False)
                return True
            except Exception as e:
                QMessageBox.warning(self, 'Error', f'Could not save file: {str(e)}')
                return False
        else:
            return self.save_file_as()
    
    def save_file_as(self):
        """Save file with a new name."""
        filename, _ = QFileDialog.getSaveFileName(self, 'Save File As', '',
                                                  'HTML Files (*.html);;Text Files (*.txt);;All Files (*)')
        if filename:
            self.current_file = filename
            self.setWindowTitle(f'Keep Me Honest - {filename}')
            return self.save_file()
        return False
    
    # Print methods
    def print_document(self):
        """Print the document."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        
        if dialog.exec_() == QPrintDialog.Accepted:
            self.text_edit.document().print_(printer)
    
    def print_preview(self):
        """Show print preview."""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.text_edit.document().print_(p))
        preview.exec_()
    
    # Update UI methods
    def update_format_buttons(self):
        """Update format button states based on cursor position."""
        fmt = self.text_edit.currentCharFormat()
        
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(fmt.font().italic())
        self.underline_action.setChecked(fmt.font().underline())
        self.strikethrough_action.setChecked(fmt.fontStrikeOut())
        
        self.font_combo.setCurrentFont(fmt.font())
        self.font_size.setValue(int(fmt.font().pointSize()) if fmt.font().pointSize() > 0 else 12)
    
    def update_paragraph_buttons(self):
        """Update paragraph button states."""
        alignment = self.text_edit.alignment()
        
        self.align_left_action.setChecked(alignment == Qt.AlignLeft)
        self.align_center_action.setChecked(alignment == Qt.AlignCenter)
        self.align_right_action.setChecked(alignment == Qt.AlignRight)
        self.align_justify_action.setChecked(alignment == Qt.AlignJustify)
    
    def closeEvent(self, event):
        """Handle application close."""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(self, 'Save Changes?',
                                        'Do you want to save changes before closing?',
                                        QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            if reply == QMessageBox.Yes:
                if self.save_file():
                    event.accept()
                else:
                    event.ignore()
            elif reply == QMessageBox.No:
                event.accept()
            else:
                event.ignore()
        else:
            event.accept()


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    word_processor = WordProcessor()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()