# 🚀 Quick Start Guide

## How to Launch the Library of Babel Searcher

### Option 1: Use the Launch Script (Recommended)
```bash
python launch.py
```
This will:
- Test all dependencies
- Verify the installation
- Launch the GUI with confirmation

### Option 2: Launch GUI Directly
```bash
python babel_gui.py
```
This launches the GUI immediately.

### Option 3: Command Line Interface
```bash
python babel.py "your phrase here"
```
This runs a command-line search.

## What You Can Do

### Manual Search Tab
- Enter any phrase using letters, space, comma, period
- Search for exact matches or use wildcards (* and ?)
- View results with page content and coordinates
- Bookmark interesting discoveries

### Page Comparison Tab
- Load two pages by seed number
- Compare them side-by-side
- See detailed similarity analysis
- Find differences and common elements

### Background Search Tab
- Set up continuous searching for multiple phrases
- Uses multiple CPU cores for faster results
- Runs in the background while you do other work

### Bookmarks Tab
- Save and organize your favorite discoveries
- Add notes and tags to results
- Export your bookmarks for sharing

### Analytics Tab
- Various statistical analyses of your search results
- Entropy analysis of page content
- Distribution visualizations

### Coordinate Browser Tab
- Navigate the Library using Borges' coordinate system
- Jump between hexagons, walls, shelves, volumes, and pages
- Explore neighborhoods of related pages

## Quick Test

1. Launch the GUI
2. Go to "Manual Search" tab
3. Enter "the" in the phrase field
4. Click "Start Search"
5. You should see results appear in a few seconds

## Features Currently Available

✅ **Core Search**: Find any phrase in the infinite library
✅ **Page Generation**: Deterministic page creation with seeds
✅ **Bookmarking**: Save and organize discoveries
✅ **Page Comparison**: Side-by-side analysis of two pages
✅ **Coordinate Navigation**: Browse using Library coordinates
✅ **Analytics**: Basic statistical analysis
✅ **Export**: Save results as CSV/JSON

## Troubleshooting

If the GUI doesn't launch:
1. Run `python launch.py` for diagnostic information
2. Check that you have Python 3.7+ installed
3. Install missing dependencies with `pip install matplotlib psutil`

## Example Searches

- **"hello"** - Find the word hello
- **"the quick"** - Find this phrase  
- **"hel*"** - Find words starting with "hel"
- **"h?llo"** - Find words like "hello", "hallo", etc.

Have fun exploring the infinite Library of Babel! 📚✨
