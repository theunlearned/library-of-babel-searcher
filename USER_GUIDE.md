# Library of Babel Searcher - User Guide

## 📖 Table of Contents
1. [Getting Started](#getting-started)
2. [Interface Overview](#interface-overview)
3. [Manual Search](#manual-search)
4. [Background Search](#background-search)
5. [Coordinate Browser](#coordinate-browser)
6. [Bookmarks](#bookmarks)
7. [Analytics](#analytics)
8. [Advanced Features](#advanced-features)
9. [Phrase Evolution Mode](#phrase-evolution-mode)
10. [Page Comparison Mode](#page-comparison-mode)
11. [Tips & Best Practices](#tips--best-practices)
12. [Troubleshooting](#troubleshooting)

## 🚀 Getting Started

### System Requirements
- Python 3.7+
- Windows/macOS/Linux
- Minimum 4GB RAM (8GB+ recommended for background search)
- 100MB+ free disk space

### First Launch
1. Double-click `babel_gui.py` or run `python babel_gui.py`
2. The application will open with 6 tabs: Manual Search, Background Search, Bookmarks, Analytics, Coordinate Browser, and Page Comparison
3. All previous sessions and bookmarks will be automatically loaded

### Character Set
The Library uses a fixed alphabet: `abcdefghijklmnopqrstuvwxyz ,.` (26 letters, space, comma, period)

## 🖥️ Interface Overview

### Manual Search Tab
- **Search Input**: Enter phrases to search for
- **Parameters**: Configure max matches, attempts, and page length
- **Results List**: Browse found matches
- **Page Viewer**: View formatted pages with highlighted matches
- **Progress Bar**: Real-time search progress and performance metrics

### Background Search Tab
- **Phrase Manager**: Add/remove phrases for continuous searching
- **Control Panel**: Start/stop background search with CPU core selection
- **Log Window**: Real-time search results and status updates

### Bookmarks Tab
- **Bookmark List**: View all saved results
- **Page Viewer**: Display bookmarked pages
- **Export Options**: Save bookmarks as CSV or JSON

### Analytics Tab
- **Visualization Buttons**: Generate various statistical charts
- **Chart Display**: Interactive matplotlib plots

### Coordinate Browser Tab
- **Coordinate Inputs**: Navigate by hexagon, wall, shelf, volume, page
- **Navigation Controls**: Increment/decrement any coordinate
- **Explorer Grid**: 3x3 grid showing adjacent pages
- **Page Display**: View current page content

### Page Comparison Tab
- **Page Loading**: Load two pages for side-by-side comparison
- **Analysis Tabs**: Differences, common substrings, statistics
- **Similarity Metrics**: Comprehensive similarity analysis
- **Echo Page Detection**: Find nearly identical pages

## 🔍 Manual Search

### Basic Search
1. Enter your search phrase (e.g., "hello world")
2. Set search parameters:
   - **Max Matches**: How many results to find (default: 5)
   - **Max Attempts**: How many pages to search (default: 100,000)
   - **Page Length**: Characters per page (default: 3,200)
3. Click "Start Search"
4. Watch the progress bar and performance metrics
5. Browse results in the list below

### Advanced Search Options
- **Wildcard Patterns**: Use `*` for any characters, `?` for single character
  - Example: `hello*world` finds "hello beautiful world"
  - Example: `h?llo` finds "hello", "hallo", etc.
- **Case Sensitivity**: All searches are case-insensitive
- **Partial Matching**: If no exact matches found, best partial matches are shown

### Understanding Results
Each result shows:
- **Seed Number**: Unique identifier for the page
- **Index**: Character position where phrase was found
- **Timestamp**: When the result was discovered
- **SHA256 Hash**: Cryptographic verification of page content
- **Library Coordinates**: Borges-style location (Hexagon, Wall, Shelf, Volume, Page)

### Navigation
- **Previous/Next Buttons**: Move between results
- **Bookmark Button**: Save interesting results
- **Jump to Seed**: Go directly to any page by seed number
- **Notes Field**: Add personal comments to results

## 🤖 Background Search

### Setting Up
1. **Add Phrases**: Type phrases and click "Add Phrase"
   - Each phrase is searched for continuously
   - Invalid characters will show an error
   - Phrases are saved automatically
2. **Select CPU Cores**: Choose how many processor cores to use
   - More cores = faster searching but higher CPU usage
   - Default uses all available cores

### Running Background Search
1. Click "Start Background Search"
2. Watch the log window for real-time results
3. Results are automatically saved to `background_results.json`
4. Progress is saved to `background_progress.json`
5. Click "Stop" to pause (can resume later)

### Viewing Results
- Use "View Background Results" button in Manual Search tab
- Results include same metadata as manual search
- Background searches can run for hours/days to find rare phrases

## 🧭 Coordinate Browser

### Understanding Coordinates
The Library is organized hierarchically:
- **Hexagon**: Largest unit (millions exist)
- **Wall**: 6 walls per hexagon
- **Shelf**: 4 shelves per wall
- **Volume**: 10 volumes per shelf  
- **Page**: 100 pages per volume

### Navigation Methods
1. **Direct Input**: Type coordinates and click "Jump to Seed"
2. **Increment/Decrement**: Use +/- buttons for each coordinate
3. **Explorer Grid**: Click any adjacent page in the 3x3 grid
4. **Seed Jumping**: Enter any seed number directly

### Exploring
- Each coordinate change generates a different page
- Adjacent pages often show similar but distinct content
- The explorer grid shows 9 nearby pages at once
- Perfect for discovering patterns and interesting content clusters

## 📚 Bookmarks

### Adding Bookmarks
- **From Manual Search**: Click "Bookmark Selected Result"
- **Automatic Fields**: Seed, phrase, coordinates, and hash are saved
- **Add Notes**: Include personal observations or tags

### Managing Bookmarks
- **Browse**: Click any bookmark to view its page
- **Export**: Save as CSV for spreadsheets or JSON for analysis
- **Persistent**: Bookmarks are saved automatically to `bookmarks.json`

### Bookmark Organization
- Add descriptive notes for later reference
- Use consistent tagging (e.g., "philosophical", "interesting-pattern")
- Export regularly to backup important discoveries

## 📊 Analytics

### Available Visualizations

#### Seed Distribution
- Shows histogram of where matches were found
- Helps identify patterns in the random generation
- Useful for understanding search algorithm behavior

#### Phrase Frequency  
- Charts how often different phrases appear
- Compares relative success rates of searches
- Identifies most/least common phrases in your results

#### Timeline Analysis
- Shows when matches were discovered over time
- Reveals search session patterns
- Useful for understanding search efficiency

#### Entropy Analysis
- **Single Page**: Analyze character frequency and randomness
- **Bookmark Analysis**: Compare entropy across saved pages
- **Entropy Map**: Chart entropy changes across seed ranges

#### Match Density Heatmap
- Visual representation of search success rates
- Shows "hot spots" where matches are more common
- Helps optimize future search strategies

### Interpreting Charts
- **High Entropy**: More random, typical of most pages
- **Low Entropy**: More patterns, potentially more interesting
- **Clustering**: Non-random distribution suggests patterns
- **Timeline Gaps**: Periods of unsuccessful searching

## 🔧 Advanced Features

### Content Hashing (SHA256)
- Every page gets a unique cryptographic hash
- Ensures reproducibility across sessions
- Detects if generation algorithm changes
- Helps identify duplicate content across different searches

### Seed Reverse Lookup
1. Click "Seed Reverse Lookup" in Manual Search tab
2. Enter SHA256 hash of desired page
3. Set search range (start and end seed)
4. System will brute-force search for matching seed
5. Useful for verifying page integrity or finding specific content

### Twin Page Discovery
- Find pages with similar content patterns
- Useful for understanding how random generation creates clusters
- Helps identify near-duplicate content

### Session Management
- **Save Session**: Preserves all results, bookmarks, and settings
- **Load Session**: Restore previous work
- **Auto-save**: Background search progress saved continuously
- **Export**: Share sessions with others

### Wildcard Patterns
- **Asterisk (*)**: Matches any number of characters
  - `the*book` finds "the book", "the great book", "the ancient book"
- **Question Mark (?)**: Matches exactly one character
  - `b?ok` finds "book", "brok", "baok"
- **Combinations**: `th?*book` finds "the book", "that book", "this old book"

### Performance Optimization
- **Adjust Page Length**: Shorter pages = faster search but less content
- **Limit Max Attempts**: Balance search time vs. thoroughness
- **CPU Core Usage**: More cores = faster but higher resource usage
- **Progress Tracking**: Monitor search efficiency in real-time

## 💡 Tips & Best Practices

### Effective Searching
1. **Start Small**: Begin with max attempts of 10,000-100,000
2. **Common Phrases**: Short, common words are easier to find
3. **Wildcards**: Use patterns when exact phrases are too rare
4. **Background Search**: Let it run overnight for rare phrases
5. **Multiple Approaches**: Try different page lengths and parameters

### Bookmark Organization
- Use descriptive notes with consistent keywords
- Tag by content type: "poetry", "dialogue", "philosophical"
- Include discovery context: search parameters used
- Export regularly to backup important finds

### Performance Management
- **Close Other Applications**: Free up RAM for large searches
- **Monitor CPU Usage**: Reduce cores if system becomes sluggish
- **Disk Space**: Background searches can generate large result files
- **Session Breaks**: Save sessions before long background searches

### Research Applications
- **Literature Studies**: Search for Borges quotes or literary references
- **Linguistic Patterns**: Analyze character frequency and distributions
- **Information Theory**: Demonstrate concepts of entropy and randomness
- **Philosophy**: Explore questions of infinite possibility and meaning

### Content Discovery
- **Interesting Coordinates**: Certain coordinate ranges may have patterns
- **Adjacent Pages**: Use explorer grid to find content clusters
- **Entropy Hunting**: Look for pages with unusually low entropy
- **Hash Verification**: Verify important discoveries with hash lookup

## 🚨 Troubleshooting

### Application Won't Start
- **Check Python Version**: Requires Python 3.7+
- **Install Dependencies**: `pip install tkinter matplotlib psutil`
- **File Permissions**: Ensure write access to program directory
- **Missing babel.py**: Core library file must be present

### Search Issues
- **No Results Found**: Try longer searches or shorter phrases
- **Invalid Phrase Error**: Only use allowed characters: `abcdefghijklmnopqrstuvwxyz ,.`
- **Slow Performance**: Reduce max attempts or use fewer CPU cores
- **Memory Errors**: Reduce page length or close other applications

### Background Search Problems
- **Won't Start**: Check that phrases are added and valid
- **High CPU Usage**: Reduce number of cores
- **Disk Full**: Background results can become large files
- **Process Hangs**: Stop and restart, progress is saved automatically

### Interface Issues
- **Blank Analytics Charts**: Ensure you have search results first
- **Coordinate Browser Errors**: Check that all coordinates are valid integers
- **Export Failures**: Verify write permissions and available disk space
- **Session Load Errors**: Check file integrity and format

### Data Issues
- **Hash Mismatches**: May indicate corrupted files or changed algorithms
- **Missing Bookmarks**: Check `bookmarks.json` file exists and is readable
- **Lost Progress**: Background progress is saved frequently but check `background_progress.json`
- **Export Problems**: Large datasets may require CSV instead of JSON

### Performance Issues
- **Slow Searches**: Reduce max attempts or page length
- **Memory Usage**: Close other applications, reduce background search cores
- **Disk Space**: Regular cleanup of large result files
- **UI Freezing**: Background search should run in separate thread

### Getting Help
1. **Check Error Messages**: Often provide specific guidance
2. **Restart Application**: Solves many temporary issues
3. **Reset Settings**: Delete `.json` files to restore defaults
4. **Verify Installation**: Ensure all required files are present

## 📚 Additional Resources

- **README.md**: Overview and technical details
- **PREFACE.md**: Personal journey and philosophical context
- **EVOLUTION_GUIDE.md**: Detailed guide to phrase evolution mode
- **COMPARISON_GUIDE.md**: Complete page comparison documentation
- **PHASE3_COMPLETE.md**: Summary of Phase 3 implementation
- **babel.py**: Core algorithm documentation in code comments

## 🧬 Phrase Evolution Mode

### Overview
Evolution mode allows you to discover phrase families and clusters by generating variations of a base phrase using evolutionary algorithms.

### Basic Usage
1. Enter a base phrase in the Evolution section
2. Adjust mutation rate (0.1-1.0, default 0.3)
3. Set number of generations (3-10, default 5)
4. Select mutation types (substitute, insert, delete, swap)
5. Click "Start Evolution"

### Evolution Process
- **Generation 1**: Creates mutations of your base phrase
- **Fitness Evaluation**: Tests how often each phrase appears
- **Selection**: Successful phrases survive to next generation
- **Mutation**: New variations created from survivors
- **Iteration**: Process repeats for specified generations

### Analyzing Results
- **Generation Progress**: Track matches found per generation
- **Phrase Variants**: See most successful mutations
- **Fitness Distribution**: Understand success patterns
- **Phrase Families**: Discover related phrase clusters

## 🔍 Page Comparison Mode

### Overview
Compare two pages side-by-side to analyze similarities, differences, and relationships between different regions of the Library.

### Loading Pages
1. **Manual Entry**: Enter seed numbers for both pages
2. **From Results**: Load pages from search results
3. **Click Compare**: Analyze the loaded pages

### Analysis Features
- **Side-by-Side View**: Visual comparison with synchronized scrolling
- **Differences**: Character-level highlighting of changes
- **Common Substrings**: Find shared text segments
- **Statistics**: Similarity percentages, entropy, edit distance

### Advanced Features
- **Find Similar Pages**: Search for pages similar to current page
- **Neighborhood Analysis**: Study pages around a reference seed
- **Echo Detection**: Find nearly identical pages (twins)
- **Pattern Analysis**: Identify recurring motifs
- **Borges' Original Story**: "The Library of Babel" for conceptual background

---

*Happy exploring! The infinite library awaits your discoveries.* 📖✨
