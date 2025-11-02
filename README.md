# Keep Me Honest

A feature-rich word processor with writing analysis, spell checking, and readability metrics.

## Features

- **Text Formatting**: Bold, italic, underline, strikethrough, fonts, colors
- **Paragraph Formatting**: Alignment, lists (bullets, numbers, roman numerals), line spacing
- **Spell Checking**: Real-time spell checking with suggestions
- **Writing Analysis**: 
  - Passive voice detection
  - Weak words identification
  - Long sentence detection
  - Jargon and complex words
  - Readability scoring (Flesch-Kincaid)
- **File Operations**: Open, save, print
- **Find and Replace**: Search and replace text
- **Font Favorites**: Save and manage favorite fonts

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install enchant library (for spell checking):
```bash
# macOS
brew install enchant

# Linux
sudo apt-get install enchant
```

4. Download icons (optional):
```bash
python scripts/download_icons.py
```

## Usage

Run the application:
```bash
python -m keep_me_honest.main
```

Or from the project root:
```bash
python keep_me_honest/main.py
```

## Project Structure

```
keep-me-honest/
├── keep_me_honest/          # Main package
│   ├── main.py              # Application entry point
│   ├── ui/                  # UI components
│   ├── core/                # Core functionality
│   └── resources/           # Icons and resources
├── tests/                   # Tests
├── scripts/                 # Utility scripts
├── docs/                    # Documentation
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Icons

The application uses Material Design Icons. Run the download script to get icons:
```bash
python scripts/download_icons.py
```

Or manually download from: https://pictogrammers.com/library/mdi/

## License

Open source - feel free to use and modify.

## Version

1.0.0
