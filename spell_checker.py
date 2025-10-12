"""Spell checking functionality for the word processor."""

import enchant
from PyQt5.QtWidgets import QTextEdit, QMessageBox
from PyQt5.QtGui import QSyntaxHighlighter, QTextCharFormat, QColor, QTextCursor


class SpellCheckHighlighter(QSyntaxHighlighter):
    """Highlights misspelled words with a wavy red underline."""
    
    def __init__(self, document, language='en'):
        super().__init__(document)
        self.spell_checker = enchant.Dict(language)
        self.enabled = True
        
        # Format for misspelled words - thicker wavy underline
        self.error_format = QTextCharFormat()
        self.error_format.setUnderlineColor(QColor(255, 0, 0))  # Bright red
        self.error_format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
    
    def set_enabled(self, enabled):
        """Enable or disable spell checking."""
        self.enabled = enabled
        self.rehighlight()
    
    def highlightBlock(self, text):
        """Check each word in the text block."""
        if not self.enabled:
            return
        
        import re
        for match in re.finditer(r'\b[a-zA-Z]+\b', text):
            word = match.group()
            if not self.spell_checker.check(word):
                self.setFormat(match.start(), len(word), self.error_format)
    
    def add_to_dictionary(self, word):
        """Add word to personal dictionary."""
        self.spell_checker.add(word)
    
    def get_suggestions(self, word):
        """Get spelling suggestions for a word."""
        return self.spell_checker.suggest(word)


class SpellCheckTextEdit(QTextEdit):
    """QTextEdit with integrated spell checking and suggestions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.spell_checker = None
    
    def set_spell_checker(self, spell_checker):
        """Set the spell checker instance."""
        self.spell_checker = spell_checker
    
    def contextMenuEvent(self, event):
        """Override context menu to add spell check suggestions."""
        menu = self.createStandardContextMenu()
        
        # Get word at cursor
        cursor = self.cursorForPosition(event.pos())
        cursor.select(QTextCursor.WordUnderCursor)
        word = cursor.selectedText()
        
        # Check if word is misspelled
        if self.spell_checker and word and self.spell_checker.enabled:
            if not self.spell_checker.spell_checker.check(word):
                # Add suggestions
                suggestions = self.spell_checker.get_suggestions(word)[:5]
                
                if suggestions:
                    for suggestion in suggestions:
                        action = menu.addAction(suggestion)
                        action.triggered.connect(
                            lambda checked, s=suggestion, c=cursor: self.replace_word(c, s)
                        )
                    menu.addSeparator()
                
                # Add "Add to Dictionary" option
                add_action = menu.addAction("Add to Dictionary")
                add_action.triggered.connect(
                    lambda: self.add_word_to_dictionary(word)
                )
                menu.addSeparator()
        
        menu.exec_(event.globalPos())
    
    def replace_word(self, cursor, new_word):
        """Replace misspelled word with suggestion."""
        cursor.beginEditBlock()
        cursor.removeSelectedText()
        cursor.insertText(new_word)
        cursor.endEditBlock()
    
    def add_word_to_dictionary(self, word):
        """Add word to personal dictionary."""
        if self.spell_checker:
            self.spell_checker.add_to_dictionary(word)
            self.spell_checker.rehighlight()
            QMessageBox.information(
                self, 'Dictionary Updated',
                f'"{word}" has been added to your personal dictionary.'
            )
