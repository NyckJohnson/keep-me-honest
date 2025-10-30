"""Keep Me Honest - A word processor with writing analysis."""

import sys
import os
os.environ['QT_MAC_WANTS_LAYER'] = '1'

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QAction, QFileDialog, QMessageBox,
    QSpinBox, QToolBar, QColorDialog, QDoubleSpinBox, QLabel,
    QMenu, QToolButton, QDialog
)
from PyQt5.QtGui import (
    QFont, QTextCharFormat, QColor, QTextCursor,
    QTextListFormat, QTextBlockFormat
)
from PyQt5.QtCore import Qt, QTimer, QSize
from PyQt5.QtPrintSupport import QPrintDialog, QPrinter, QPrintPreviewDialog

from spell_checker import SpellCheckHighlighter, SpellCheckTextEdit
from font_manager import CustomFontComboBox, FavoriteFontsDialog, FontSettingsManager
from find_replace import FindReplaceDialog
from writing_checker import WritingChecker
from writing_checker_ui import WritingCheckerDock, WritingHighlighter
from icon_manager import IconManager, Icons


class KeepMeHonest(QMainWindow):
    """Main application window."""
    
    def __init__(self):
        super().__init__()
        
        # Core state
        self.current_file = None
        self.find_dialog = None
        
        # Managers
        self.font_manager = FontSettingsManager()
        self.favorite_fonts = self.font_manager.load_favorites()
        self.icons = IconManager()
        self.writing_checker = WritingChecker()
        
        # Settings
        self.spell_check_enabled = True
        self.writing_checker_visible = False
        
        # Timer for writing checks
        self.check_timer = QTimer()
        self.check_timer.timeout.connect(self.run_writing_check)
        self.check_timer.setInterval(1000)
        
        self.setup_ui()
    
    def setup_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Keep Me Honest')
        self.setGeometry(100, 100, 1000, 600)
        
        self.setup_text_editor()
        self.setup_spell_checker()
        self.setup_menus()
        self.setup_toolbars()
        self.setup_writing_checker_dock()
        self.connect_signals()
        
        self.show()
    
    def setup_text_editor(self):
        """Create and configure text editor."""
        self.text_edit = SpellCheckTextEdit()
        self.text_edit.setFontPointSize(12)
        self.setCentralWidget(self.text_edit)
    
    def setup_spell_checker(self):
        """Initialize spell checking."""
        try:
            self.highlighter = SpellCheckHighlighter(self.text_edit.document())
            self.text_edit.set_spell_checker(self.highlighter)
        except Exception as e:
            print(f"Spell checker initialization failed: {e}")
            self.highlighter = None
            self.spell_check_enabled = False
    
    def setup_menus(self):
        """Create menu bar."""
        menubar = self.menuBar()
        
        self.setup_file_menu(menubar.addMenu('File'))
        self.setup_edit_menu(menubar.addMenu('Edit'))
        self.setup_format_menu(menubar.addMenu('Format'))
        self.setup_tools_menu(menubar.addMenu('Tools'))
    
    def setup_file_menu(self, menu):
        """Create File menu."""
        menu.addAction('New', self.new_file, 'Ctrl+N')
        menu.addAction('Open', self.open_file, 'Ctrl+O')
        menu.addAction('Save', self.save_file, 'Ctrl+S')
        menu.addAction('Save As...', self.save_file_as, 'Ctrl+Shift+S')
        menu.addSeparator()
        menu.addAction('Print Preview...', self.print_preview)
        menu.addAction('Print...', self.print_document, 'Ctrl+P')
        menu.addSeparator()
        menu.addAction('Exit', self.close, 'Ctrl+Q')
    
    def setup_edit_menu(self, menu):
        """Create Edit menu."""
        menu.addAction('Undo', self.text_edit.undo, 'Ctrl+Z')
        menu.addAction('Redo', self.text_edit.redo, 'Ctrl+Y')
        menu.addSeparator()
        menu.addAction('Cut', self.text_edit.cut, 'Ctrl+X')
        menu.addAction('Copy', self.text_edit.copy, 'Ctrl+C')
        menu.addAction('Paste', self.text_edit.paste, 'Ctrl+V')
        menu.addSeparator()
        menu.addAction('Find and Replace...', self.show_find_replace, 'Ctrl+F')
    
    def setup_format_menu(self, menu):
        """Create Format menu."""
        menu.addAction('Bold', self.toggle_bold, 'Ctrl+B')
        menu.addAction('Italic', self.toggle_italic, 'Ctrl+I')
        menu.addAction('Underline', self.toggle_underline, 'Ctrl+U')
        menu.addAction('Strikethrough', self.toggle_strikethrough, 'Ctrl+Shift+X')
        menu.addSeparator()
        menu.addAction('Highlight Color...', self.change_highlight_color)
        menu.addSeparator()
        
        align_menu = menu.addMenu('Alignment')
        align_menu.addAction('Align Left', lambda: self.set_alignment(Qt.AlignLeft))
        align_menu.addAction('Align Center', lambda: self.set_alignment(Qt.AlignCenter))
        align_menu.addAction('Align Right', lambda: self.set_alignment(Qt.AlignRight))
        align_menu.addAction('Justify', lambda: self.set_alignment(Qt.AlignJustify))
        
        menu.addSeparator()
        menu.addAction('Bullet List', self.toggle_bullet_list)
        menu.addAction('Numbered List', self.toggle_numbered_list)
        menu.addSeparator()
        menu.addAction('Add Current Font to Favorites', 
                      self.add_current_font_to_favorites, 'Ctrl+Shift+F')
        menu.addAction('Manage Favorite Fonts...', self.manage_favorites)
    
    def setup_tools_menu(self, menu):
        """Create Tools menu."""
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
    
    def setup_toolbars(self):
        """Create all toolbars."""
        self.setup_format_toolbar()
        self.setup_alignment_toolbar()
        self.setup_paragraph_toolbar()
    
    def setup_format_toolbar(self):
        """Create format toolbar."""
        toolbar = QToolBar('Format')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))  # Smaller icons
        self.addToolBar(toolbar)
        
        # Font selector
        self.font_combo = CustomFontComboBox(self)
        self.font_combo.set_favorites(self.favorite_fonts)
        toolbar.addWidget(self.font_combo)
        
        # Font size
        self.font_size = QSpinBox()
        self.font_size.setRange(8, 72)
        self.font_size.setValue(12)
        self.font_size.valueChanged.connect(self.change_font_size)
        toolbar.addWidget(self.font_size)
        
        toolbar.addSeparator()
        
        # Text style buttons
        self.bold_action = self.create_toolbar_action(
            Icons.BOLD, 'Bold', 'Ctrl+B', self.toggle_bold, checkable=True
        )
        toolbar.addAction(self.bold_action)
        
        self.italic_action = self.create_toolbar_action(
            Icons.ITALIC, 'Italic', 'Ctrl+I', self.toggle_italic, checkable=True
        )
        toolbar.addAction(self.italic_action)
        
        self.underline_action = self.create_toolbar_action(
            Icons.UNDERLINE, 'Underline', 'Ctrl+U', self.toggle_underline, checkable=True
        )
        toolbar.addAction(self.underline_action)
        
        self.strikethrough_action = self.create_toolbar_action(
            Icons.STRIKETHROUGH, 'Strikethrough', 'Ctrl+Shift+X', 
            self.toggle_strikethrough, checkable=True
        )
        toolbar.addAction(self.strikethrough_action)
        
        # List menu button
        list_button = QToolButton()
        list_button.setIcon(self.icons.get_icon(Icons.LIST))
        list_button.setToolTip('Lists')
        list_button.setPopupMode(QToolButton.InstantPopup)
        list_button.setMenu(self.create_list_menu())
        toolbar.addWidget(list_button)
        
        toolbar.addSeparator()
        
        # Color button
        toolbar.addAction(self.create_toolbar_action(
            Icons.HIGHLIGHT, 'Highlight', None, self.change_highlight_color
        ))
    
    def setup_alignment_toolbar(self):
        """Create alignment toolbar."""
        toolbar = QToolBar('Alignment')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))  # Smaller icons
        self.addToolBar(toolbar)
        
        self.align_left_action = self.create_toolbar_action(
            Icons.ALIGN_LEFT, 'Align Left', None,
            lambda: self.set_alignment(Qt.AlignLeft), checkable=True
        )
        toolbar.addAction(self.align_left_action)
        
        self.align_center_action = self.create_toolbar_action(
            Icons.ALIGN_CENTER, 'Align Center', None,
            lambda: self.set_alignment(Qt.AlignCenter), checkable=True
        )
        toolbar.addAction(self.align_center_action)
        
        self.align_right_action = self.create_toolbar_action(
            Icons.ALIGN_RIGHT, 'Align Right', None,
            lambda: self.set_alignment(Qt.AlignRight), checkable=True
        )
        toolbar.addAction(self.align_right_action)
        
        self.align_justify_action = self.create_toolbar_action(
            Icons.ALIGN_JUSTIFY, 'Justify', None,
            lambda: self.set_alignment(Qt.AlignJustify), checkable=True
        )
        toolbar.addAction(self.align_justify_action)
    
    def setup_paragraph_toolbar(self):
        """Create paragraph toolbar."""
        toolbar = QToolBar('Paragraph')
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(16, 16))  # Smaller icons
        self.addToolBar(toolbar)
        
        # Line spacing
        toolbar.addWidget(QLabel(' Line Spacing: '))
        self.line_spacing = QDoubleSpinBox()
        self.line_spacing.setRange(0.5, 3.0)
        self.line_spacing.setSingleStep(0.1)
        self.line_spacing.setValue(1.0)
        self.line_spacing.valueChanged.connect(self.change_line_spacing)
        toolbar.addWidget(self.line_spacing)
    
    def create_list_menu(self):
        """Create list style menu."""
        menu = QMenu()
        
        menu.addAction('• Disc Bullets', 
                      lambda: self.set_list_style(QTextListFormat.ListDisc))
        menu.addAction('◦ Circle Bullets', 
                      lambda: self.set_list_style(QTextListFormat.ListCircle))
        menu.addAction('▪ Square Bullets', 
                      lambda: self.set_list_style(QTextListFormat.ListSquare))
        menu.addSeparator()
        menu.addAction('1. Decimal', 
                      lambda: self.set_list_style(QTextListFormat.ListDecimal))
        menu.addAction('a. Lowercase Letters', 
                      lambda: self.set_list_style(QTextListFormat.ListLowerAlpha))
        menu.addAction('A. Uppercase Letters', 
                      lambda: self.set_list_style(QTextListFormat.ListUpperAlpha))
        menu.addAction('i. Lowercase Roman', 
                      lambda: self.set_list_style(QTextListFormat.ListLowerRoman))
        menu.addAction('I. Uppercase Roman', 
                      lambda: self.set_list_style(QTextListFormat.ListUpperRoman))
        menu.addSeparator()
        menu.addAction('Remove List', self.remove_list)
        
        return menu
    
    def setup_writing_checker_dock(self):
        """Create writing checker sidebar."""
        self.writing_checker_dock = WritingCheckerDock(self)
        self.writing_checker_dock.check_type_changed.connect(self.on_check_type_changed)
        self.writing_checker_dock.ignore_issue.connect(self.on_ignore_issue)
        self.writing_checker_dock.add_cinnamon_word.connect(self.on_add_cinnamon_word)
        self.writing_checker_dock.remove_cinnamon_word.connect(self.on_remove_cinnamon_word)
        self.writing_checker_dock.refresh_requested.connect(self.run_writing_check)
        self.addDockWidget(Qt.RightDockWidgetArea, self.writing_checker_dock)
        self.writing_checker_dock.hide()
    
    def connect_signals(self):
        """Connect all signals."""
        self.text_edit.cursorPositionChanged.connect(self.update_format_buttons)
        self.text_edit.cursorPositionChanged.connect(self.update_paragraph_buttons)
        self.text_edit.textChanged.connect(self.schedule_writing_check)
        self.text_edit.selectionChanged.connect(self.update_selection_readability)
    
    def create_toolbar_action(self, icon_name, tooltip, shortcut, callback, checkable=False):
        """Helper to create toolbar action with icon."""
        action = QAction(self.icons.get_icon(icon_name), '', self)
        action.setToolTip(tooltip)
        if shortcut:
            action.setShortcut(shortcut)
        action.triggered.connect(callback)
        if checkable:
            action.setCheckable(True)
        return action
    
    # ========== Writing Checker ==========
    
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
        """Schedule writing check (debounced)."""
        if self.writing_checker_visible:
            # Don't run check if user has text selected (they're reading/reviewing)
            if not self.text_edit.textCursor().hasSelection():
                self.check_timer.stop()
                self.check_timer.start()
    
    def run_writing_check(self):
        """Run writing checker."""
        self.check_timer.stop()
        if not self.writing_checker:
            return
        
        text = self.text_edit.toPlainText()
        issues, readability_data = self.writing_checker.check_text(text)
        
        # Update readability display with just the grade
        grade = readability_data.get('flesch_kincaid_grade', 0)
        self.writing_checker_dock.set_readability_grade(grade)
        
        self.update_selection_readability()
        
        self.writing_checker_dock.set_issues(issues)
        WritingHighlighter.highlight_issues(self.text_edit, issues)
    
    def update_selection_readability(self):
        """Update readability for selection."""
        if not self.writing_checker_visible or not self.writing_checker:
            return
        
        cursor = self.text_edit.textCursor()
        if cursor.hasSelection():
            selected_text = cursor.selectedText()
            analysis = self.writing_checker.get_readability_compact(selected_text)
            self.writing_checker_dock.set_selection_readability(f"✓ {analysis}")
        else:
            self.writing_checker_dock.set_selection_readability("(Select text to analyze)")
    
    def on_check_type_changed(self, check_type, enabled):
        """Handle check type toggle."""
        self.writing_checker.set_check_enabled(check_type, enabled)
        self.run_writing_check()
    
    def on_ignore_issue(self, issue_index):
        """Handle ignore issue."""
        issues = self.writing_checker_dock.issues
        if 0 <= issue_index < len(issues):
            issues.pop(issue_index)
            WritingHighlighter.highlight_issues(self.text_edit, issues)
            self.writing_checker_dock.set_issues(issues)
            if issues:
                next_index = min(issue_index, len(issues) - 1)
                self.writing_checker_dock.show_issue(next_index)
    
    def on_add_cinnamon_word(self, word):
        """Add cinnamon word."""
        self.writing_checker.add_cinnamon_word(word)
        self.writing_checker_dock.set_cinnamon_words(self.writing_checker.cinnamon_words)
        self.run_writing_check()
    
    def on_remove_cinnamon_word(self, word):
        """Remove cinnamon word."""
        self.writing_checker.remove_cinnamon_word(word)
        self.writing_checker_dock.set_cinnamon_words(self.writing_checker.cinnamon_words)
        self.run_writing_check()
    
    # ========== Font Management ==========
    
    def change_font(self, font):
        """Change font."""
        self.text_edit.setCurrentFont(font)
    
    def change_font_size(self, size):
        """Change font size."""
        self.text_edit.setFontPointSize(size)
    
    def add_current_font_to_favorites(self):
        """Add current font to favorites."""
        current_font = self.font_combo.currentFont().family()
        if current_font not in self.font_combo.favorites:
            self.font_combo.add_to_favorites(current_font)
            QMessageBox.information(self, 'Added', f'"{current_font}" added to favorites!')
        else:
            QMessageBox.information(self, 'Already Added', 
                                  f'"{current_font}" is already in favorites.')
    
    def manage_favorites(self):
        """Open favorites dialog."""
        dialog = FavoriteFontsDialog(self.font_combo.favorites, self)
        if dialog.exec_() == QDialog.Accepted:
            self.font_combo.set_favorites(dialog.get_favorites())
            self.font_manager.save_favorites(self.font_combo.favorites)
    
    # ========== Text Formatting ==========
    
    def toggle_bold(self):
        """Toggle bold."""
        fmt = self.text_edit.currentCharFormat()
        weight = QFont.Normal if fmt.fontWeight() == QFont.Bold else QFont.Bold
        fmt.setFontWeight(weight)
        self.text_edit.setCurrentCharFormat(fmt)
    
    def toggle_italic(self):
        """Toggle italic."""
        self.text_edit.setFontItalic(not self.text_edit.fontItalic())
    
    def toggle_underline(self):
        """Toggle underline."""
        self.text_edit.setFontUnderline(not self.text_edit.fontUnderline())
    
    def toggle_strikethrough(self):
        """Toggle strikethrough."""
        fmt = self.text_edit.currentCharFormat()
        fmt.setFontStrikeOut(not fmt.fontStrikeOut())
        self.text_edit.setCurrentCharFormat(fmt)
    
    def change_text_color(self):
        """Change text color."""
        color = QColorDialog.getColor()
        if color.isValid():
            self.text_edit.setTextColor(color)
    
    def change_highlight_color(self):
        """Change highlight color."""
        color = QColorDialog.getColor()
        if color.isValid():
            fmt = self.text_edit.currentCharFormat()
            fmt.setBackground(color)
            self.text_edit.setCurrentCharFormat(fmt)
    
    # ========== Paragraph Formatting ==========
    
    def set_alignment(self, alignment):
        """Set alignment."""
        self.text_edit.setAlignment(alignment)
    
    def toggle_bullet_list(self):
        """Toggle bullet list."""
        self.set_list_style(QTextListFormat.ListDisc)
    
    def toggle_numbered_list(self):
        """Toggle numbered list."""
        self.set_list_style(QTextListFormat.ListDecimal)
    
    def set_list_style(self, style):
        """Set list style."""
        cursor = self.text_edit.textCursor()
        current_list = cursor.currentList()
        
        if current_list:
            fmt = current_list.format()
            fmt.setStyle(style)
            current_list.setFormat(fmt)
        else:
            fmt = QTextListFormat()
            fmt.setStyle(style)
            cursor.createList(fmt)
    
    def remove_list(self):
        """Remove list."""
        cursor = self.text_edit.textCursor()
        if cursor.currentList():
            cursor.currentList().remove(cursor.block())
    
    def change_line_spacing(self, value):
        """Change line spacing."""
        cursor = self.text_edit.textCursor()
        fmt = cursor.blockFormat()
        fmt.setLineHeight(value * 100, QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(fmt)
    
    # ========== Spell Check ==========
    
    def toggle_spell_check(self):
        """Toggle spell check."""
        if self.highlighter:
            self.spell_check_enabled = not self.spell_check_enabled
            self.highlighter.set_enabled(self.spell_check_enabled)
            self.spell_check_action.setChecked(self.spell_check_enabled)
    
    # ========== Find/Replace ==========
    
    def show_find_replace(self):
        """Show find/replace dialog."""
        if not self.find_dialog:
            self.find_dialog = FindReplaceDialog(self)
        self.find_dialog.show()
        self.find_dialog.raise_()
        self.find_dialog.activateWindow()
    
    # ========== File Operations ==========
    
    def new_file(self):
        """Create new file."""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, 'Save Changes?', 'Save changes?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
            if reply == QMessageBox.Yes:
                self.save_file()
            elif reply == QMessageBox.Cancel:
                return
        
        self.text_edit.clear()
        self.current_file = None
        self.setWindowTitle('Keep Me Honest - Untitled')
    
    def open_file(self):
        """Open file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Open File', '',
            'HTML Files (*.html);;Text Files (*.txt);;All Files (*)'
        )
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
                QMessageBox.warning(self, 'Error', f'Could not open file: {e}')
    
    def save_file(self):
        """Save file."""
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
                QMessageBox.warning(self, 'Error', f'Could not save: {e}')
                return False
        return self.save_file_as()
    
    def save_file_as(self):
        """Save file as."""
        filename, _ = QFileDialog.getSaveFileName(
            self, 'Save File As', '',
            'HTML Files (*.html);;Text Files (*.txt);;All Files (*)'
        )
        if filename:
            self.current_file = filename
            self.setWindowTitle(f'Keep Me Honest - {filename}')
            return self.save_file()
        return False
    
    # ========== Print ==========
    
    def print_document(self):
        """Print document."""
        printer = QPrinter(QPrinter.HighResolution)
        dialog = QPrintDialog(printer, self)
        if dialog.exec_() == QPrintDialog.Accepted:
            self.text_edit.document().print_(printer)
    
    def print_preview(self):
        """Print preview."""
        printer = QPrinter(QPrinter.HighResolution)
        preview = QPrintPreviewDialog(printer, self)
        preview.paintRequested.connect(lambda p: self.text_edit.document().print_(p))
        preview.exec_()
    
    # ========== UI Updates ==========
    
    def update_format_buttons(self):
        """Update format button states."""
        fmt = self.text_edit.currentCharFormat()
        
        self.bold_action.setChecked(fmt.fontWeight() == QFont.Bold)
        self.italic_action.setChecked(fmt.font().italic())
        self.underline_action.setChecked(fmt.font().underline())
        self.strikethrough_action.setChecked(fmt.fontStrikeOut())
        
        self.font_combo.setCurrentFont(fmt.font())
        point_size = fmt.font().pointSize()
        self.font_size.setValue(int(point_size) if point_size > 0 else 12)
    
    def update_paragraph_buttons(self):
        """Update paragraph button states."""
        alignment = self.text_edit.alignment()
        
        self.align_left_action.setChecked(alignment == Qt.AlignLeft)
        self.align_center_action.setChecked(alignment == Qt.AlignCenter)
        self.align_right_action.setChecked(alignment == Qt.AlignRight)
        self.align_justify_action.setChecked(alignment == Qt.AlignJustify)
    
    def closeEvent(self, event):
        """Handle close."""
        if self.text_edit.document().isModified():
            reply = QMessageBox.question(
                self, 'Save Changes?', 'Save before closing?',
                QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel
            )
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
    """Application entry point."""
    app = QApplication(sys.argv)
    window = KeepMeHonest()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()