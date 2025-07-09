#!/usr/bin/env python3
"""
Test script for Phase 3.3 - Page Comparison View
Verifies that page comparison functionality works correctly
"""

def test_comparison_imports():
    """Test that comparison-related imports work"""
    try:
        from babel_core import compare_pages, highlight_differences, find_common_substrings
        from babel_tools import find_echo_pages, search_for_similar_pages
        print("✓ Comparison imports successful")
        return True
    except ImportError as e:
        print(f"✗ Comparison import failed: {e}")
        return False

def test_page_comparison():
    """Test basic page comparison functionality"""
    try:
        from babel_core import generate_page, compare_pages
        
        # Generate two test pages
        page1 = generate_page(42, 200)
        page2 = generate_page(43, 200)
        
        # Compare them
        comparison = compare_pages(page1, page2)
        
        # Verify comparison results structure
        required_keys = ['identical', 'similarity_percentage', 'edit_distance', 
                        'entropy1', 'entropy2', 'hash1', 'hash2']
        
        for key in required_keys:
            assert key in comparison, f"Missing key in comparison: {key}"
        
        # Test similarity percentage is reasonable
        similarity = comparison['similarity_percentage']
        assert 0 <= similarity <= 100, f"Similarity out of range: {similarity}"
        
        print(f"✓ Page comparison working - similarity: {similarity:.2f}%")
        return True
        
    except Exception as e:
        print(f"✗ Page comparison test failed: {e}")
        return False

def test_difference_highlighting():
    """Test difference highlighting functionality"""
    try:
        from babel_core import highlight_differences
        
        # Test with known different strings
        text1 = "hello world this is a test"
        text2 = "hello there this is a test"
        
        differences = highlight_differences(text1, text2)
        
        assert len(differences) > 0, "No differences found between different texts"
        
        # Test with identical strings
        identical_diffs = highlight_differences(text1, text1)
        assert len(identical_diffs) == 0, "Found differences in identical text"
        
        print(f"✓ Difference highlighting working - found {len(differences)} differences")
        return True
        
    except Exception as e:
        print(f"✗ Difference highlighting test failed: {e}")
        return False

def test_common_substrings():
    """Test common substring finding"""
    try:
        from babel_core import find_common_substrings
        
        text1 = "hello world this is a test of common substrings"
        text2 = "hello there this is a test of different substrings"
        
        substrings = find_common_substrings(text1, text2, min_length=5)
        
        assert len(substrings) > 0, "No common substrings found"
        
        # Verify structure
        for substring in substrings[:3]:  # Check first 3
            assert 'substring' in substring, "Missing substring field"
            assert 'length' in substring, "Missing length field"
            assert 'pos1' in substring, "Missing pos1 field"
            assert 'pos2' in substring, "Missing pos2 field"
        
        print(f"✓ Common substring finding working - found {len(substrings)} substrings")
        return True
        
    except Exception as e:
        print(f"✗ Common substring test failed: {e}")
        return False

def test_echo_pages():
    """Test echo page detection"""
    try:
        from babel_tools import find_echo_pages
        
        # Test with two different seeds
        echo_result = find_echo_pages(42, 43)
        
        required_keys = ['seed1', 'seed2', 'similarity_percentage', 'page1', 'page2']
        for key in required_keys:
            assert key in echo_result, f"Missing key in echo result: {key}"
        
        # Test similarity calculation
        similarity = echo_result['similarity_percentage']
        assert 0 <= similarity <= 100, f"Similarity out of range: {similarity}"
        
        print(f"✓ Echo page detection working - similarity: {similarity:.2f}%")
        return True
        
    except Exception as e:
        print(f"✗ Echo page test failed: {e}")
        return False

def test_similar_page_search():
    """Test similar page search functionality"""
    try:
        from babel_tools import search_for_similar_pages
        
        # Search for pages similar to seed 42 (with low threshold for testing)
        similar_pages = search_for_similar_pages(42, search_range=100, 
                                               similarity_threshold=10.0, 
                                               max_results=3)
        
        # Should find at least some pages with low threshold
        assert len(similar_pages) > 0, "No similar pages found"
        
        # Verify structure
        for page in similar_pages:
            assert 'reference_seed' in page, "Missing reference_seed"
            assert 'similar_seed' in page, "Missing similar_seed"
            assert 'similarity' in page, "Missing similarity"
            assert page['similarity'] >= 10.0, "Similarity below threshold"
        
        print(f"✓ Similar page search working - found {len(similar_pages)} similar pages")
        return True
        
    except Exception as e:
        print(f"✗ Similar page search test failed: {e}")
        return False

def test_gui_comparison_components():
    """Test that GUI comparison components can be created"""
    try:
        import tkinter as tk
        from babel_gui import BabelGUI
        
        # Create a test GUI instance (without mainloop)
        root = tk.Tk()
        app = BabelGUI()
        
        # Check that comparison variables exist
        assert hasattr(app, 'comparison_page1'), "Missing comparison_page1"
        assert hasattr(app, 'comparison_page2'), "Missing comparison_page2"
        assert hasattr(app, 'compare_tab'), "Missing compare_tab"
        
        # Check that comparison methods exist
        assert hasattr(app, 'load_comparison_page1'), "Missing load_comparison_page1 method"
        assert hasattr(app, 'load_comparison_page2'), "Missing load_comparison_page2 method"
        assert hasattr(app, 'compare_loaded_pages'), "Missing compare_loaded_pages method"
        
        root.destroy()
        
        print("✓ GUI comparison components working")
        return True
        
    except Exception as e:
        print(f"✗ GUI comparison test failed: {e}")
        return False

def main():
    """Run all comparison tests"""
    print("Library of Babel - Phase 3.3 Page Comparison Tests")
    print("=" * 65)
    
    tests = [
        test_comparison_imports,
        test_page_comparison,
        test_difference_highlighting,
        test_common_substrings,
        test_echo_pages,
        test_similar_page_search,
        test_gui_comparison_components
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 65)
    print(f"Page Comparison Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All comparison tests passed! Phase 3.3 is ready.")
        print("\nPage Comparison Features:")
        print("• Side-by-side page viewing with synchronized scrolling")
        print("• Comprehensive similarity analysis and statistics")
        print("• Character-level difference highlighting")
        print("• Common substring detection and analysis")
        print("• Echo page detection for twin/similar pages")
        print("• Neighborhood analysis for page clusters")
        print("• Easy loading from search results")
        print("• Export and visualization capabilities")
        return 0
    else:
        print("✗ Some comparison tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
