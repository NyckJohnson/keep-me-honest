"""UI components for the writing checker."""

from PyQt5.QtWidgets import (QDockWidget, QWidget, QVBoxLayout, QHBoxLayout,
                             QCheckBox, QListWidget, QListWidgetItem, QPushButton,
                             QLabel, QLineEdit)
from PyQt5.QtGui import QColor, QTextCursor, QTextCharFormat
from PyQt5.QtCore import Qt, pyqtSignal


class WritingCheckerDock(QDockWidget):
    """Sidebar dock for writing checker controls and issues."""
    
    check_type_changed = pyqtSignal(str, bool)
    ignore_issue = pyqtSignal(int)
    add_cinnamon_word = pyqtSignal(str)
    remove_cinnamon_word = pyqtSignal(str)
    refresh_requested = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__("Writing Checker", parent)
        self.setAllowedAreas(Qt.RightDockWidgetArea | Qt.LeftDockWidgetArea)
        self.issues = []
        self.current_issue_index = 0
        self.init_ui()
    
    def init_ui(self):
        """Set up the dock UI."""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Readability section (simplified)
        layout.addWidget(QLabel("📊 Readability:"))
        self.readability_display = QLabel("-- Grade")
        self.readability_display.setAlignment(Qt.AlignCenter)
        self.readability_display.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
                border-radius: 5px;
                background-color: #f0f0f0;
            }
        """)
        layout.addWidget(self.readability_display)
        
        # Selection readability
        layout.addWidget(QLabel("📖 Selection:"))
        self.selection_readability = QLabel("(Select text to analyze)")
        self.selection_readability.setWordWrap(True)
        self.selection_readability.setStyleSheet("padding: 5px;")
        layout.addWidget(self.selection_readability)
        
        layout.addSpacing(10)
        
        # Check type toggles
        layout.addWidget(QLabel("Writing Checks:"))
        
        self.checks = {
            'passive_voice': QCheckBox('Passive Voice'),
            'weak_words': QCheckBox('Weak Words'),
            'long_sentences': QCheckBox('Long Sentences'),
            'jargon': QCheckBox('Jargon'),
            'adjectives_adverbs': QCheckBox('Adjectives/Adverbs'),
            'simple_alternatives': QCheckBox('Simple Alternatives'),
            'confused_synonyms': QCheckBox('Confused Synonyms'),
            'repeated_words': QCheckBox('Repeated Words'),
            'cinnamon_words': QCheckBox('Cinnamon Words')
        }
        
        for check_type, checkbox in self.checks.items():
            checkbox.setChecked(True)
            checkbox.stateChanged.connect(
                lambda state, ct=check_type: self.check_type_changed.emit(ct, state == Qt.Checked)
            )
            layout.addWidget(checkbox)
        
        layout.addSpacing(10)
        
        # Refresh button
        refresh_btn = QPushButton('Refresh Check')
        refresh_btn.clicked.connect(self.refresh_requested.emit)
        layout.addWidget(refresh_btn)
        
        layout.addSpacing(10)
        
        # Issues list
        layout.addWidget(QLabel("Issues Found:"))
        self.issues_list = QListWidget()
        self.issues_list.itemSelectionChanged.connect(self.on_issue_selected)
        layout.addWidget(self.issues_list)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        prev_btn = QPushButton('← Previous')
        prev_btn.clicked.connect(self.show_previous_issue)
        nav_layout.addWidget(prev_btn)
        
        next_btn = QPushButton('Next →')
        next_btn.clicked.connect(self.show_next_issue)
        nav_layout.addWidget(next_btn)
        
        layout.addLayout(nav_layout)
        
        # Issue details
        layout.addWidget(QLabel("Issue Details:"))
        self.issue_text = QLineEdit()
        self.issue_text.setReadOnly(True)
        layout.addWidget(self.issue_text)
        
        self.suggestion_text = QLineEdit()
        self.suggestion_text.setReadOnly(True)
        layout.addWidget(self.suggestion_text)
        
        # Action buttons
        action_layout = QHBoxLayout()
        
        ignore_btn = QPushButton('Ignore This')
        ignore_btn.clicked.connect(self.ignore_current_issue)
        action_layout.addWidget(ignore_btn)
        
        layout.addLayout(action_layout)
        
        # Cinnamon words section
        layout.addSpacing(10)
        layout.addWidget(QLabel("Cinnamon Words:"))
        
        cinnamon_layout = QHBoxLayout()
        self.cinnamon_input = QLineEdit()
        self.cinnamon_input.setPlaceholderText("Add a word...")
        cinnamon_layout.addWidget(self.cinnamon_input)
        
        add_cinnamon_btn = QPushButton('+')
        add_cinnamon_btn.setMaximumWidth(40)
        add_cinnamon_btn.clicked.connect(self.add_cinnamon)
        cinnamon_layout.addWidget(add_cinnamon_btn)
        
        layout.addLayout(cinnamon_layout)
        
        self.cinnamon_list = QListWidget()
        self.cinnamon_list.itemDoubleClicked.connect(self.remove_cinnamon)
        layout.addWidget(self.cinnamon_list)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        self.setWidget(widget)
    
    def set_issues(self, issues):
        """Update the issues list."""
        self.issues = issues
        self.issues_list.clear()
        
        # Group issues by type
        issue_groups = {}
        for i, issue in enumerate(issues):
            if issue.issue_type not in issue_groups:
                issue_groups[issue.issue_type] = []
            issue_groups[issue.issue_type].append((i, issue))
        
        # Add to list
        for issue_type in sorted(issue_groups.keys()):
            for idx, issue in issue_groups[issue_type]:
                item = QListWidgetItem(f"[{issue.issue_type}] {issue.text[:50]}")
                item.setData(Qt.UserRole, idx)
                
                # Color code by type
                colors = {
                    'passive_voice': QColor(255, 200, 0),
                    'weak_words': QColor(255, 150, 0),
                    'long_sentences': QColor(200, 150, 255),
                    'jargon': QColor(150, 200, 255),
                    'adjectives_adverbs': QColor(150, 255, 150),
                    'simple_alternatives': QColor(255, 150, 150),
                    'confused_synonyms': QColor(255, 200, 150),
                    'repeated_words': QColor(200, 200, 255),
                    'cinnamon_words': QColor(255, 200, 200)
                }
                
                if issue_type in colors:
                    item.setBackground(colors[issue_type])
                
                self.issues_list.addItem(item)
        
        if issues:
            self.issues_list.setCurrentRow(0)
            self.show_issue(0)
    
    def on_issue_selected(self):
        """Handle issue selection from list."""
        current = self.issues_list.currentItem()
        if current:
            idx = current.data(Qt.UserRole)
            self.current_issue_index = idx
            self.show_issue(idx)
    
    def show_issue(self, idx):
        """Display a specific issue."""
        if 0 <= idx < len(self.issues):
            issue = self.issues[idx]
            self.issue_text.setText(f"{issue.text}")
            self.suggestion_text.setText(f"💡 {issue.suggestion}")
            self.current_issue_index = idx
    
    def show_next_issue(self):
        """Navigate to next issue."""
        if self.issues:
            idx = (self.current_issue_index + 1) % len(self.issues)
            self.show_issue(idx)
    
    def show_previous_issue(self):
        """Navigate to previous issue."""
        if self.issues:
            idx = (self.current_issue_index - 1) % len(self.issues)
            self.show_issue(idx)
    
    def ignore_current_issue(self):
        """Ignore the current issue."""
        if 0 <= self.current_issue_index < len(self.issues):
            self.ignore_issue.emit(self.current_issue_index)
    
    def add_cinnamon(self):
        """Add a word to cinnamon list."""
        word = self.cinnamon_input.text().strip()
        if word:
            self.add_cinnamon_word.emit(word)
            self.cinnamon_input.clear()
    
    def remove_cinnamon(self, item):
        """Remove a word from cinnamon list."""
        word = item.text().split(' (')[0]
        self.remove_cinnamon_word.emit(word)
    
    def set_cinnamon_words(self, words):
        """Update the cinnamon words list display."""
        self.cinnamon_list.clear()
        for word in sorted(words):
            item = QListWidgetItem(f"{word} (double-click to remove)")
            self.cinnamon_list.addItem(item)
    
    def set_readability_grade(self, grade: float):
        """
        Update readability display with grade and appropriate color.
        
        Args:
            grade: Flesch-Kincaid grade level
        """
        # Determine color based on grade
        if grade < 10:
            color = '#90EE90'  # Soft green
        elif grade <= 13:
            color = '#FFE66D'  # Soft yellow
        else:
            color = '#FFB3B3'  # Soft red
        
        # Update display
        self.readability_display.setText(f"{grade:.1f} Grade")
        self.readability_display.setStyleSheet(f"""
            QLabel {{
                font-size: 32px;
                font-weight: bold;
                padding: 20px;
                border-radius: 5px;
                background-color: {color};
            }}
        """)
    
    def set_selection_readability(self, analysis_text: str):
        """Update the selection readability display."""
        self.selection_readability.setText(analysis_text)


class WritingHighlighter:
    """Applies highlighting to text for writing issues."""
    
    COLOR_MAP = {
        'passive_voice': QColor(255, 200, 0, 100),
        'weak_words': QColor(255, 150, 0, 100),
        'long_sentences': QColor(200, 150, 255, 100),
        'jargon': QColor(150, 200, 255, 100),
        'adjectives_adverbs': QColor(150, 255, 150, 100),
        'simple_alternatives': QColor(255, 150, 150, 100),
        'confused_synonyms': QColor(255, 200, 150, 100),
        'repeated_words': QColor(200, 200, 255, 100),
        'cinnamon_words': QColor(255, 200, 200, 100)
    }
    
    @staticmethod
    def highlight_issues(text_edit, issues):
        """Apply highlighting to text editor for all issues."""
        cursor = text_edit.textCursor()
        cursor.movePosition(QTextCursor.Start)
        text_edit.setTextCursor(cursor)
        
        # Clear previous highlighting
        fmt = QTextCharFormat()
        cursor.select(QTextCursor.Document)
        cursor.setCharFormat(fmt)
        
        # Apply new highlighting
        for issue in issues:
            cursor.setPosition(issue.start)
            cursor.movePosition(QTextCursor.Right, QTextCursor.KeepAnchor, issue.end - issue.start)
            
            fmt = QTextCharFormat()
            fmt.setBackground(WritingHighlighter.COLOR_MAP.get(
                issue.issue_type,
                QColor(200, 200, 200, 100)
            ))
            fmt.setToolTip(f"{issue.issue_type}: {issue.suggestion}")
            
            cursor.setCharFormat(fmt)