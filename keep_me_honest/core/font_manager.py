"""Font management and favorites system."""

import json
import os
from PyQt5.QtWidgets import QComboBox, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QListWidget, QFontDialog, QMessageBox
from PyQt5.QtGui import QFont, QFontDatabase
from PyQt5.QtCore import Qt


class CustomFontComboBox(QComboBox):
    """Font selector with favorites support."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.favorites = []
        self.currentIndexChanged.connect(self.on_font_changed)
        self.setEditable(False)
        self.setMaxVisibleItems(20)
    
    def set_favorites(self, favorites):
        """Set and display favorite fonts."""
        self.favorites = favorites
        self.update_font_list()
    
    def update_font_list(self):
        """Rebuild font list with favorites at top."""
        current_text = self.currentText()
        if current_text.startswith('★ '):
            current_text = current_text[2:]
        if current_text == "─────────────":
            current_text = ""
        
        self.blockSignals(True)
        self.clear()
        
        if self.favorites:
            for fav in self.favorites:
                self.addItem(f"★ {fav}", fav)
                self.setItemData(self.count() - 1, QFont(fav), Qt.FontRole)
            
            self.addItem("─────────────", "")
            separator_index = self.count() - 1
            
            model = self.model()
            item = model.item(separator_index)
            if item:
                item.setEnabled(False)
        
        font_db = QFontDatabase()
        for family in font_db.families():
            if not family.startswith('.') and family not in self.favorites:
                self.addItem(family, family)
                self.setItemData(self.count() - 1, QFont(family), Qt.FontRole)
        
        if current_text:
            for i in range(self.count()):
                if self.itemData(i) == current_text:
                    self.setCurrentIndex(i)
                    break
        
        self.blockSignals(False)
    
    def on_font_changed(self, index):
        """Handle font selection change."""
        font_name = self.itemData(index)
        if font_name and self.parent_window:
            self.parent_window.change_font(QFont(font_name))
    
    def currentFont(self):
        """Get currently selected font."""
        font_name = self.itemData(self.currentIndex())
        if font_name:
            return QFont(font_name)
        return QFont()
    
    def setCurrentFont(self, font):
        """Set current font by name."""
        font_name = font.family()
        for i in range(self.count()):
            if self.itemData(i) == font_name:
                self.setCurrentIndex(i)
                break
    
    def add_to_favorites(self, font_name):
        """Add font to favorites."""
        if font_name and font_name not in self.favorites:
            self.favorites.append(font_name)
            self.update_font_list()
            if self.parent_window:
                self.parent_window.save_favorites()
    
    def remove_from_favorites(self, font_name):
        """Remove font from favorites."""
        if font_name in self.favorites:
            self.favorites.remove(font_name)
            self.update_font_list()
            if self.parent_window:
                self.parent_window.save_favorites()


class FavoriteFontsDialog(QDialog):
    """Dialog to manage favorite fonts."""
    
    def __init__(self, favorites, parent=None):
        super().__init__(parent)
        self.parent = parent
        self.favorites = favorites.copy()
        self.setWindowTitle('Manage Favorite Fonts')
        self.setModal(True)
        self.init_ui()
    
    def init_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel('Your Favorite Fonts:'))
        
        self.list_widget = QListWidget()
        self.list_widget.addItems(self.favorites)
        layout.addWidget(self.list_widget)
        
        button_layout = QHBoxLayout()
        
        remove_btn = QPushButton('Remove Selected')
        remove_btn.clicked.connect(self.remove_selected)
        button_layout.addWidget(remove_btn)
        
        add_btn = QPushButton('Add Font')
        add_btn.clicked.connect(self.add_font)
        button_layout.addWidget(add_btn)
        
        layout.addLayout(button_layout)
        
        ok_cancel_layout = QHBoxLayout()
        
        ok_btn = QPushButton('OK')
        ok_btn.clicked.connect(self.accept)
        ok_cancel_layout.addWidget(ok_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        ok_cancel_layout.addWidget(cancel_btn)
        
        layout.addLayout(ok_cancel_layout)
        
        self.setLayout(layout)
        self.resize(400, 300)
    
    def remove_selected(self):
        """Remove selected font from favorites."""
        current_item = self.list_widget.currentItem()
        if current_item:
            font_name = current_item.text()
            self.favorites.remove(font_name)
            self.list_widget.takeItem(self.list_widget.row(current_item))
    
    def add_font(self):
        """Add a new font to favorites."""
        font, ok = QFontDialog.getFont()
        if ok:
            font_name = font.family()
            if font_name not in self.favorites:
                self.favorites.append(font_name)
                self.list_widget.addItem(font_name)
    
    def get_favorites(self):
        """Return the updated favorites list."""
        return self.favorites


class FontSettingsManager:
    """Manages font preferences and persistence."""
    
    def __init__(self):
        self.settings_file = os.path.expanduser('~/.word_processor_settings.json')
    
    def load_favorites(self):
        """Load favorite fonts from settings file."""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    return settings.get('favorite_fonts', [])
            except:
                return []
        return []
    
    def save_favorites(self, favorites):
        """Save favorite fonts to settings file."""
        settings = {'favorite_fonts': favorites}
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f)
        except Exception as e:
            print(f"Could not save favorites: {e}")
