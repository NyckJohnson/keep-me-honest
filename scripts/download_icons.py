"""Download Material Design Icons for Keep Me Honest.

This script downloads all required icons from the official Material Design Icons
GitHub repository and saves them to the correct location in the project.
"""

import os
import urllib.request
import urllib.error
import sys

# Base URL for Material Design Icons SVG files
MDI_BASE_URL = "https://raw.githubusercontent.com/Templarian/MaterialDesign/master/svg/"

# Icon mappings: filename -> MDI icon name
ICONS = {
    'format-bold': 'format-bold',
    'format-italic': 'format-italic',
    'format-underline': 'format-underline',
    'format-strikethrough-variant': 'format-strikethrough-variant',
    'marker': 'marker',
    'format-align-left': 'format-align-left',
    'format-align-center': 'format-align-center',
    'format-align-right': 'format-align-right',
    'format-align-justify': 'format-align-justify',
    'format-list-bulleted-square': 'format-list-bulleted-square',
    'format-list-bulleted': 'format-list-bulleted',
    'format-list-numbered': 'format-list-numbered',
}


def get_icons_directory():
    """Get the path to the icons directory."""
    # Get the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up one level to project root, then into keep_me_honest/resources/icons
    project_root = os.path.dirname(script_dir)
    icons_dir = os.path.join(project_root, 'keep_me_honest', 'resources', 'icons')
    
    return icons_dir


def download_icon(icon_name, output_dir):
    """
    Download a single icon from Material Design Icons.
    
    Args:
        icon_name: Name of the icon (same for filename and MDI name)
        output_dir: Directory to save the icon
    
    Returns:
        bool: True if successful, False otherwise
    """
    url = f"{MDI_BASE_URL}{icon_name}.svg"
    output_path = os.path.join(output_dir, f"{icon_name}.svg")
    
    try:
        print(f"  Downloading {icon_name}.svg... ", end="", flush=True)
        urllib.request.urlretrieve(url, output_path)
        print("✓")
        return True
    except urllib.error.HTTPError as e:
        print(f"✗ (HTTP {e.code})")
        return False
    except Exception as e:
        print(f"✗ ({e})")
        return False


def main():
    """Download all icons."""
    print("=" * 70)
    print("Material Design Icons Downloader for Keep Me Honest")
    print("=" * 70)
    print()
    
    # Get icons directory
    icons_dir = get_icons_directory()
    
    # Create directory if it doesn't exist
    if not os.path.exists(icons_dir):
        print(f"Creating directory: {icons_dir}")
        os.makedirs(icons_dir)
        print()
    else:
        print(f"Icons directory: {icons_dir}")
        print()
    
    # Download all icons
    print(f"Downloading {len(ICONS)} icons...")
    print()
    
    success_count = 0
    failed_count = 0
    failed_icons = []
    
    for icon_name in ICONS.values():
        if download_icon(icon_name, icons_dir):
            success_count += 1
        else:
            failed_count += 1
            failed_icons.append(icon_name)
    
    # Summary
    print()
    print("=" * 70)
    print("Download Summary")
    print("=" * 70)
    print(f"  Success: {success_count}/{len(ICONS)}")
    print(f"  Failed:  {failed_count}/{len(ICONS)}")
    
    if failed_icons:
        print()
        print("Failed icons:")
        for icon in failed_icons:
            print(f"  - {icon}")
    
    print("=" * 70)
    print()
    
    if success_count > 0:
        print(f"✓ Icons saved to: {icons_dir}")
        print("✓ You can now run Keep Me Honest with professional icons!")
    
    if failed_count > 0:
        print()
        print("Note: Some icons failed to download.")
        print("The app will use text fallbacks for missing icons.")
        print()
        print("You can manually download missing icons from:")
        print("https://pictogrammers.com/library/mdi/")
    
    return 0 if failed_count == 0 else 1


if __name__ == '__main__':
    sys.exit(main())