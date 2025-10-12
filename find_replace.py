"""Find and Replace dialog functionality."""

from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QCheckBox, QMessageBox
from PyQt5.QtGui import QTextDocument, QTextCursor


class FindReplaceDialog(QDialog):
    """Dialog for finding and replacing text."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.setWindowTitle('Find and Replace')
        self.setModal(False)
        self.init_ui()
    
    def init_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Find section
        find_layout = QHBoxLayout()
        find_layout.addWidget(QLabel('Find:'))
        self.find_input = QLineEdit()
        find_layout.addWidget(self.find_input)
        layout.addLayout(find_layout)
        
        # Replace section
        replace_layout = QHBoxLayout()
        replace_layout.addWidget(QLabel('Replace:'))
        self.replace_input = QLineEdit()
        replace_layout.addWidget(self.replace_input)
        layout.addLayout(replace_layout)
        
        # Options
        self.case_sensitive = QCheckBox('Case Sensitive')
        layout.addWidget(self.case_sensitive)
        
        self.whole_word = QCheckBox('Whole Words Only')
        layout.addWidget(self.whole_word)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        find_btn = QPushButton('Find Next')
        find_btn.clicked.connect(self.find_next)
        button_layout.addWidget(find_btn)
        
        find_prev_btn = QPushButton('Find Previous')
        find_prev_btn.clicked.connect(self.find_previous)
        button_layout.addWidget(find_prev_btn)
        
        replace_btn = QPushButton('Replace')
        replace_btn.clicked.connect(self.replace)
        button_layout.addWidget(replace_btn)
        
        replace_all_btn = QPushButton('Replace All')
        replace_all_btn.clicked.connect(self.replace_all)
        button_layout.addWidget(replace_all_btn)
        
        layout.addLayout(button_layout)
        
        close_btn = QPushButton('Close')
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def get_flags(self):
        """Get search flags based on options."""
        flags = QTextDocument.FindFlags()
        if self.case_sensitive.isChecked():
            flags |= QTextDocument.FindCaseSensitively
        if self.whole_word.isChecked():
            flags |= QTextDocument.FindWholeWords
        return flags
    
    def find_next(self):
        """Find next occurrence."""
        text = self.find_input.text()
        if text:
            found = self.parent.text_edit.find(text, self.get_flags())
            if not found:
                QMessageBox.information(self, 'Find', 'No more matches found.')
    
    def find_previous(self):
        """Find previous occurrence."""
        text = self.find_input.text()
        if text:
            flags = self.get_flags() | QTextDocument.FindBackward
            found = self.parent.text_edit.find(text, flags)
            if not found:
                QMessageBox.information(self, 'Find', 'No more matches found.')
    
    def replace(self):
        """Replace current selection."""
        cursor = self.parent.text_edit.textCursor()
        if cursor.hasSelection():
            cursor.insertText(self.replace_input.text())
        self.find_next()
    
    def replace_all(self):
        """Replace all occurrences."""
        find_text = self.find_input.text()
        replace_text = self.replace_input.text()
        if not find_text:
            return
        
        cursor = self.parent.text_edit.textCursor()
        cursor.beginEditBlock()
        
        cursor.movePosition(QTextCursor.Start)
        self.parent.text_edit.setTextCursor(cursor)
        
        count = 0
        while self.parent.text_edit.find(find_text, self.get_flags()):
            cursor = self.parent.text_edit.textCursor()
            cursor.insertText(replace_text)
            count += 1
        
        cursor.endEditBlock()
        QMessageBox.information(
            self, 'Replace All',
            f'Replaced {count} occurrence(s).'
        )
