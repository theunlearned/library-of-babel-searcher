#!/usr/bin/env python3
"""
Quick test and launch script for the Library of Babel Searcher
Run this file to test the installation and launch the GUI
"""

#!/usr/bin/env python3
"""
Library of Babel Searcher - Application Launcher
Created by: The Unlearned

"I have always imagined that Paradise will be a kind of library."

Launch the Library of Babel Searcher application.
"""

import sys
import os

def test_dependencies():
    """Test if all required dependencies are available"""
    print("Testing dependencies...")
    
    try:
        import tkinter
        print("✓ tkinter (GUI framework)")
    except ImportError:
        print("✗ tkinter missing - required for GUI")
        return False
    
    try:
        import matplotlib
        print("✓ matplotlib (plotting)")
    except ImportError:
        print("✗ matplotlib missing - install with: pip install matplotlib")
        return False
    
    try:
        import psutil
        print("✓ psutil (system monitoring)")
    except ImportError:
        print("✗ psutil missing - install with: pip install psutil")
        return False
    
    print("✓ All dependencies available")
    return True

def test_modules():
    """Test if our custom modules work"""
    print("\nTesting Library of Babel modules...")
    
    try:
        from babel import generate_page, search_for_phrase
        print("✓ babel.py (core functions)")
    except ImportError as e:
        print(f"✗ babel.py import failed: {e}")
        return False
    
    try:
        from babel_core import compute_entropy, compare_pages
        print("✓ babel_core.py (analysis functions)")
    except ImportError as e:
        print(f"✗ babel_core.py import failed: {e}")
        return False
    
    try:
        from babel_tools import generate_phrase_mutations, LibraryCoordinates
        print("✓ babel_tools.py (search and coordinate tools)")
    except ImportError as e:
        print(f"✗ babel_tools.py import failed: {e}")
        return False
    
    return True

def test_basic_functionality():
    """Test basic Library functions"""
    print("\nTesting basic functionality...")
    
    try:
        from babel import generate_page, search_for_phrase
        
        # Test page generation
        page = generate_page(42, 100)
        assert len(page) == 100
        print("✓ Page generation working")
        
        # Test search
        results = search_for_phrase("the", max_attempts=1000, max_matches=1)
        if results:
            print(f"✓ Search working - found 'the' at seed {results[0][0]}")
        else:
            print("✓ Search working (no matches in small sample)")
        
        return True
        
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        return False

def launch_gui():
    """Launch the main GUI application"""
    print("\nLaunching Library of Babel Searcher GUI...")
    print("Close the GUI window to return to this script.")
    
    try:
        import babel_gui
        app = babel_gui.BabelGUI()
        print("✓ GUI created successfully")
        print("\nGUI Features Available:")
        print("  • Manual Search - Search for specific phrases")
        print("  • Background Search - Continuous multi-phrase searching")
        print("  • Bookmarks - Save and organize interesting results")
        print("  • Analytics - Statistical analysis and visualization")
        print("  • Coordinate Browser - Navigate using Library coordinates")
        print("  • Page Comparison - Compare two pages side-by-side")
        print("\nStarting GUI...")
        app.mainloop()
        print("GUI closed.")
        return True
        
    except Exception as e:
        print(f"✗ GUI launch failed: {e}")
        print(f"Error details: {type(e).__name__}: {str(e)}")
        return False

def main():
    """Main test and launch function"""
    print("=" * 60)
    print("Library of Babel Searcher - Test & Launch")
    print("=" * 60)
    
    # Run tests
    if not test_dependencies():
        print("\n❌ Dependency test failed. Please install missing packages.")
        return 1
    
    if not test_modules():
        print("\n❌ Module test failed. Check file integrity.")
        return 1
    
    if not test_basic_functionality():
        print("\n❌ Functionality test failed. Check implementation.")
        return 1
    
    print("\n✅ All tests passed!")
    
    # Ask user if they want to launch GUI
    try:
        response = input("\nLaunch the GUI now? (y/n): ").lower().strip()
        if response in ['y', 'yes', '']:
            success = launch_gui()
            if success:
                print("\n✅ Application ran successfully!")
                return 0
            else:
                print("\n❌ GUI failed to launch properly.")
                return 1
        else:
            print("\nSkipping GUI launch. Run 'python babel_gui.py' to launch manually.")
            return 0
            
    except KeyboardInterrupt:
        print("\n\nInterrupted by user.")
        return 0

if __name__ == "__main__":
    sys.exit(main())
