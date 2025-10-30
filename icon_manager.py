"""Icon manager for Keep Me Honest."""

import os
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize


class IconManager:
    """Manages application icons."""
    
    def __init__(self, icon_dir='icons'):
        """
        Initialize icon manager.
        
        Args:
            icon_dir: Directory containing icon files
        """
        self.icon_dir = icon_dir
        self.icon_cache = {}
        
        # Default icon size
        self.default_size = QSize(20, 20)
        
        # Create icons directory if it doesn't exist
        if not os.path.exists(self.icon_dir):
            os.makedirs(self.icon_dir)
    
    def get_icon(self, name):
        """
        Get an icon by name.
        
        Args:
            name: Icon name (without extension)
            
        Returns:
            QIcon object
        """
        # Check cache first
        if name in self.icon_cache:
            return self.icon_cache[name]
        
        # Try to load icon
        icon = self._load_icon(name)
        
        # Cache it
        self.icon_cache[name] = icon
        
        return icon
    
    def _load_icon(self, name):
        """Load icon from file."""
        # Try different file extensions
        extensions = ['.svg', '.png', '.jpg', '.ico']
        
        for ext in extensions:
            icon_path = os.path.join(self.icon_dir, name + ext)
            if os.path.exists(icon_path):
                return QIcon(icon_path)
        
        # Icon not found - return empty icon
        print(f"Warning: Icon '{name}' not found in {self.icon_dir}")
        return QIcon()
    
    def set_icon_size(self, size):
        """Set default icon size."""
        self.default_size = size


# Icon name constants for easy reference
class Icons:
    """Icon name constants using Material Design Icons naming."""
    
    # Text formatting
    BOLD = 'format-bold'
    ITALIC = 'format-italic'
    UNDERLINE = 'format-underline'
    STRIKETHROUGH = 'format-strikethrough-variant'
    HIGHLIGHT = 'marker'
    
    # Alignment
    ALIGN_LEFT = 'format-align-left'
    ALIGN_CENTER = 'format-align-center'
    ALIGN_RIGHT = 'format-align-right'
    ALIGN_JUSTIFY = 'format-align-justify'
    
    # Lists
    LIST = 'format-list-bulleted-square'
    BULLET_LIST = 'format-list-bulleted'
    NUMBERED_LIST = 'format-list-numbered'
    
    # File operations
    NEW = 'file-plus'
    OPEN = 'folder-open'
    SAVE = 'content-save'
    PRINT = 'printer'
    
    # Edit operations
    UNDO = 'undo'
    REDO = 'redo'
    CUT = 'content-cut'
    COPY = 'content-copy'
    PASTE = 'content-paste'
    FIND = 'magnify'
    
    # Other
    FONT = 'format-font'
    STAR = 'star'
    CHECK = 'check'