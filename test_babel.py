#!/usr/bin/env python3
"""
Test script for Library of Babel Searcher
Verifies core functionality is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all required modules can be imported"""
    try:
        from babel import generate_page, search_for_phrase, format_page_output, validate_phrase, ALPHABET
        print("✓ babel.py imports successful")
        return True
    except ImportError as e:
        print(f"✗ babel.py import failed: {e}")
        return False

def test_page_generation():
    """Test basic page generation functionality"""
    try:
        from babel import generate_page
        
        # Test reproducible generation
        page1 = generate_page(42, length=100)
        page2 = generate_page(42, length=100)
        
        if page1 == page2:
            print("✓ Page generation is deterministic")
        else:
            print("✗ Page generation is not deterministic")
            return False
            
        # Test different seeds produce different content
        page3 = generate_page(43, length=100)
        if page1 != page3:
            print("✓ Different seeds produce different content")
        else:
            print("✗ Different seeds produce identical content")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Page generation test failed: {e}")
        return False

def test_search_functionality():
    """Test search functionality"""
    try:
        from babel import search_for_phrase
        
        # Test basic search
        results = search_for_phrase("the", max_attempts=1000, max_matches=1)
        if results:
            print(f"✓ Search found 'the' at seed {results[0][0]}")
        else:
            print("✗ Search failed to find common phrase 'the'")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Search test failed: {e}")
        return False

def test_gui_imports():
    """Test that GUI components can be imported"""
    try:
        import tkinter as tk
        from tkinter import ttk
        import matplotlib.pyplot as plt
        import psutil
        import hashlib
        print("✓ GUI dependencies available")
        return True
    except ImportError as e:
        print(f"✗ GUI dependency missing: {e}")
        return False

def test_hashing():
    """Test SHA256 hashing functionality"""
    try:
        import hashlib
        from babel import generate_page
        
        page = generate_page(42, length=100)
        hash1 = hashlib.sha256(page.encode('utf-8')).hexdigest()
        hash2 = hashlib.sha256(page.encode('utf-8')).hexdigest()
        
        if hash1 == hash2:
            print("✓ SHA256 hashing is consistent")
        else:
            print("✗ SHA256 hashing is inconsistent")
            return False
            
        return True
    except Exception as e:
        print(f"✗ Hashing test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("Library of Babel Searcher - Test Suite")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_page_generation,
        test_search_functionality,
        test_gui_imports,
        test_hashing
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 50)
    print(f"Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All tests passed! The application should work correctly.")
        return 0
    else:
        print("✗ Some tests failed. Check dependencies and installation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
