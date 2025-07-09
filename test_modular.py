#!/usr/bin/env python3
"""
Test script for the new modular structure
Verifies that babel_core and babel_tools work correctly
"""

def test_core_module():
    """Test babel_core functionality"""
    try:
        from babel_core import generate_page, compute_page_hash, compute_entropy, validate_phrase
        
        # Test page generation
        page1 = generate_page(42, 100)
        page2 = generate_page(42, 100)
        assert page1 == page2, "Page generation not deterministic"
        
        # Test hashing
        hash1 = compute_page_hash(page1)
        hash2 = compute_page_hash(page1)
        assert hash1 == hash2, "Hashing not consistent"
        assert len(hash1) == 64, "SHA256 hash wrong length"
        
        # Test entropy
        entropy = compute_entropy(page1)
        assert 0 <= entropy <= 10, f"Entropy out of range: {entropy}"
        
        # Test validation
        validate_phrase("hello world")
        try:
            validate_phrase("hello@world")
            assert False, "Should have failed validation"
        except ValueError:
            pass  # Expected
            
        print("✓ babel_core module tests passed")
        return True
        
    except Exception as e:
        print(f"✗ babel_core module test failed: {e}")
        return False

def test_tools_module():
    """Test babel_tools functionality"""
    try:
        from babel_tools import (
            LibraryCoordinates, seed_to_coordinates, coordinates_to_seed,
            wildcard_match, search_for_phrase
        )
        
        # Test coordinate conversion
        coords = seed_to_coordinates(12345)
        seed_back = coordinates_to_seed(coords)
        assert seed_back == 12345, f"Coordinate conversion failed: {seed_back} != 12345"
        
        # Test wildcard matching
        assert wildcard_match("hello world", "hello*"), "Wildcard match failed"
        assert wildcard_match("hello", "h?llo"), "Single char wildcard failed"
        assert not wildcard_match("hello", "world"), "False positive wildcard match"
        
        # Test search (quick test)
        results = search_for_phrase("the", max_attempts=1000, max_matches=1)
        assert len(results) <= 1, "Too many results returned"
        
        print("✓ babel_tools module tests passed")
        return True
        
    except Exception as e:
        print(f"✗ babel_tools module test failed: {e}")
        return False

def test_module_integration():
    """Test that modules work together"""
    try:
        from babel_core import generate_page, get_page_statistics
        from babel_tools import seed_to_coordinates, LibraryCoordinates
        
        # Generate a page and analyze it
        page = generate_page(42, 200)
        stats = get_page_statistics(page)
        
        assert 'entropy' in stats, "Missing entropy in statistics"
        assert 'hash' in stats, "Missing hash in statistics"
        assert stats['length'] == 200, "Wrong page length in stats"
        
        # Test coordinate integration
        coords = seed_to_coordinates(42)
        assert isinstance(coords, LibraryCoordinates), "Wrong coordinate type"
        
        print("✓ Module integration tests passed")
        return True
        
    except Exception as e:
        print(f"✗ Module integration test failed: {e}")
        return False

def main():
    """Run all modular tests"""
    print("Library of Babel - Modular Structure Test Suite")
    print("=" * 60)
    
    tests = [
        test_core_module,
        test_tools_module, 
        test_module_integration
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        if test():
            passed += 1
        else:
            failed += 1
        print()
    
    print("=" * 60)
    print(f"Modular Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All modular tests passed! Ready for Phase 3.2")
        return 0
    else:
        print("✗ Some modular tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
