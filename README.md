# Library of Babel Searcher

*"In tribute to Jorge Luis Borges and the infinite library"*  
**Created by:** The Unlearned ✍️

A powerful GUI application inspired by Jorge Luis Borges' "The Library of Babel" that allows you to search through an infinite library of algorithmically generated text pages.

## 🎯 Overview

This tool simulates Borges' infinite library where every possible combination of characters exists somewhere. Using deterministic random generation with seeds, you can:

- **Search** for specific phrases across millions of generated pages
- **Explore** the library using coordinate-based navigation  
- **Analyze** content patterns with entropy and statistical tools
- **Bookmark** interesting discoveries for later reference
- **Background Search** continuously across multiple CPU cores

## ✨ Key Features

### 🔍 Manual Search
- Search for any phrase using the allowed character set: `abcdefghijklmnopqrstuvwxyz ,.`
- Wildcard support with `*` and `?` patterns
- Configurable search parameters (max matches, attempts, page length)
- Real-time progress tracking with performance metrics
- Partial match scoring when exact matches aren't found

### � **NEW! Phrase Evolution Mode**
- **Evolutionary Search**: Generate and test mutations of base phrases
- **Mutation Types**: Substitute, insert, delete, and swap character operations
- **Population Evolution**: Multi-generation search with fitness-based selection
- **Phrase Family Discovery**: Find clusters of related phrases in seed space
- **Evolution Analysis**: Visualize generation progress, variant success, and fitness distribution
- **Adaptive Learning**: Successful phrases guide future mutations

### �🤖 Background Search  
- Multi-phrase continuous searching
- Multi-core processing support
- Persistent progress tracking
- Automatic result logging and storage

### 🧭 Coordinate Browser
- Navigate the library using Borges-style coordinates (Hexagon, Wall, Shelf, Volume, Page)
- Visual grid explorer for adjacent pages
- Direct seed jumping capabilities
- Real-time coordinate-to-seed conversion

### 📊 Analytics & Visualization
- **Entropy Analysis**: Measure randomness and patterns in pages
- **Seed Distribution**: Statistical analysis of match distributions  
- **Phrase Frequency**: Track which phrases appear most often
- **Timeline Analysis**: Temporal patterns in search results
- **Match Density Heatmaps**: Visual representation of search success rates
- **Entropy Maps**: Track content randomness across seed ranges
- **Evolution Analysis**: Track phrase mutation success across generations

### � **NEW! Page Comparison View**
- **Side-by-Side Analysis**: Compare two pages simultaneously with synchronized scrolling
- **Difference Detection**: Character-level highlighting of differences with context
- **Similarity Analysis**: Comprehensive similarity scoring and statistical comparison  
- **Common Substring Discovery**: Find shared text segments between pages
- **Twin Page Detection**: Identify nearly identical pages (echo pages)
- **Neighborhood Analysis**: Study similarity patterns around reference seeds
- **Echo Page Search**: Find pages with high similarity to a reference page
- **SHA256 Hashing**: Every page gets a cryptographic hash for verification
- **Duplicate Detection**: Identify identical content across different seeds
- **Data Integrity**: Ensure reproducible results across sessions

### 💾 Data Management
- **Bookmarking**: Save interesting results with notes and tags
- **Session Management**: Save and restore complete search sessions
- **Export Options**: CSV and JSON export for further analysis
- **Import Capabilities**: Load previous background search results

## 🚀 Getting Started

### Prerequisites
```bash
pip install tkinter matplotlib psutil hashlib
```

### Required Files
- `babel.py` - Core library functions
- `babel_gui.py` - Main GUI application

### Basic Usage

1. **Launch the application**:
   ```bash
   python babel_gui.py
   ```

2. **Search for a phrase**:
   - Enter your search phrase in the "Manual Search" tab
   - Set your search parameters (defaults are good for testing)
   - Click "Start Search"
   - Browse results and bookmark interesting findings

3. **Explore coordinates**:
   - Switch to "Coordinate Browser" tab
   - Use the coordinate inputs or navigation buttons
   - Explore adjacent pages with the grid explorer

4. **Analyze patterns**:
   - Use the "Analytics" tab for statistical insights
   - Generate entropy maps and distribution charts
   - Export data for external analysis

## 🧠 How It Works

### The Library Concept
The application generates text pages using Python's `random.Random(seed)` to ensure deterministic, reproducible content. Each seed corresponds to a unique page in the infinite library.

### Coordinate System
Following Borges' vision, pages are organized in a hierarchical structure:
- **Hexagon**: Highest level organizational unit (6 walls each)
- **Wall**: Six walls per hexagon (4 shelves each)
- **Shelf**: Four shelves per wall (10 volumes each)
- **Volume**: Ten volumes per shelf (100 pages each)
- **Page**: One hundred pages per volume

### Search Algorithm
1. Generate pages sequentially using incremental seeds
2. Search each page for the target phrase
3. Record matches with full metadata (seed, index, timestamp, hash)
4. Support wildcard patterns and partial matching
5. Track performance metrics and resource usage

### Content Hashing
Every page receives a SHA256 hash to ensure:
- **Reproducibility**: Same seed always produces same content
- **Integrity**: Detect any changes in the generation algorithm
- **Deduplication**: Identify identical content across different contexts

## 📁 File Structure

```
quest/
├── babel.py              # Core library functions
├── babel_core.py         # Core algorithms and analysis functions  
├── babel_tools.py        # Search utilities and coordinate system
├── babel_gui.py          # Main GUI application  
├── babel_background.py   # Background search utilities
├── launch.py             # Test and launch script
├── cleanup.py            # Cleanup script for obsolete files
├── bookmarks.json        # Saved bookmarks
├── bg_phrases.json       # Background search phrases
├── background_results.json # Background search results
├── background_progress.json # Search progress state
├── search_terms.txt      # Background search terms
├── requirements.txt      # Python dependencies
├── README.md            # This file
├── USER_GUIDE.md        # Detailed user guide
├── QUICK_START.md       # Quick setup guide
├── PREFACE.md           # Personal journey and philosophy
├── EVOLUTION_GUIDE.md   # Evolution mode documentation
├── COMPARISON_GUIDE.md  # Page comparison documentation
├── PHASE3_COMPLETE.md   # Phase 3 completion summary
├── test_babel.py        # Basic functionality tests
├── test_modular.py      # Modular structure tests
├── test_evolution.py    # Evolution functionality tests
├── test_comparison.py   # Page comparison tests
└── test_phase3_complete.py # Comprehensive Phase 3 tests
```

## 📷 Screenshots

![Manual Search Tab](screenshots/manual_search.png)
![Analytics Tab](screenshots/analytics.png)
![Coordinate Browser](screenshots/coordinate_browser.png)

## 🔬 Research Applications

This tool serves multiple research and educational purposes:

- **Literature Studies**: Explore concepts from Borges' work practically
- **Information Theory**: Demonstrate entropy, randomness, and pattern detection
- **Computer Science**: Algorithm analysis and computational complexity
- **Philosophy**: Questions about infinite possibility spaces and meaning
- **Cryptography**: Hash verification and data integrity concepts

## 🎯 Goals
- Make the Library of Babel explorable and analyzable
- Provide advanced search and analytics tools
- Support reproducibility via hashing and session save/load
- Demonstrate concepts from information theory and literature
- Serve as an educational tool for multiple disciplines

## 🤝 Contributing

This is an educational and experimental tool. Contributions are welcome for:
- Performance optimizations
- Additional analysis features  
- UI/UX improvements
- Documentation enhancements

## 📜 License

This project is inspired by Jorge Luis Borges' "The Library of Babel" and is intended for educational and research purposes.

## 🙏 Acknowledgments

- **Jorge Luis Borges** for the original conceptual framework
- **Jonathan Basile** for inspiring practical implementations of the concept
- **The Python Community** for the excellent libraries that make this possible

## ✍️ Authorship

**Created by:** The Unlearned  
**Philosophy:** True knowledge comes from curiosity, not credentials  
**Signature:** `TU-2025-BABEL-∞`

This work is released anonymously as a gift to all seekers of the infinite library, especially fellow autodidacts who learn from life itself. See [AUTHORSHIP.md](./AUTHORSHIP.md) for the complete anonymous release declaration.

## 📚 Documentation

- [User Guide](./USER_GUIDE.md) - Complete user documentation with Phase 3 features
- [Quick Start](./QUICK_START.md) - Get up and running quickly  
- [Evolution Guide](./EVOLUTION_GUIDE.md) - **NEW!** Complete guide to Phrase Evolution Mode
- [Comparison Guide](./COMPARISON_GUIDE.md) - **NEW!** Page comparison features and analysis
- [Personal Preface](./PREFACE.md) - My journey and philosophy as The Unlearned
- [Phase 3 Summary](./PHASE3_COMPLETE.md) - **NEW!** Complete implementation details
- [Anonymous Authorship](./AUTHORSHIP.md) - **NEW!** Release declaration and philosophy

---

*"The universe (which others call the Library) is composed of an indefinite and perhaps infinite number of hexagonal galleries..."* - Jorge Luis Borges

**Signature of The Unlearned:** `TU-2025-BABEL-∞` ✍️
