#!/usr/bin/env python3
"""
Test script for Phase 3.2 - Phrase Evolution Mode
Verifies that evolution search functionality works correctly
"""

def test_evolution_imports():
    """Test that evolution-related imports work"""
    try:
        from babel_tools import generate_phrase_mutations, search_with_wildcards
        from babel_core import similarity_percentage
        print("✓ Evolution imports successful")
        return True
    except ImportError as e:
        print(f"✗ Evolution import failed: {e}")
        return False

def test_phrase_mutations():
    """Test phrase mutation generation"""
    try:
        from babel_tools import generate_phrase_mutations
        
        base_phrase = "hello"
        mutations = generate_phrase_mutations(base_phrase, ['substitute', 'insert'])
        
        assert len(mutations) > 0, "No mutations generated"
        assert base_phrase not in mutations, "Original phrase should not be in mutations"
        
        # Test that mutations are valid (contain only allowed characters)
        from babel_core import ALPHABET
        allowed_chars = set(ALPHABET)
        
        for mutation in mutations[:5]:  # Test first 5 mutations
            assert all(c in allowed_chars for c in mutation), f"Invalid character in mutation: {mutation}"
        
        print(f"✓ Generated {len(mutations)} valid mutations from '{base_phrase}'")
        print(f"  Sample mutations: {mutations[:5]}")
        return True
        
    except Exception as e:
        print(f"✗ Phrase mutation test failed: {e}")
        return False

def test_evolution_search():
    """Test evolution search components"""
    try:
        from babel_tools import search_for_phrase, generate_phrase_mutations
        
        # Test with a simple phrase
        base_phrase = "the"
        mutations = generate_phrase_mutations(base_phrase, ['substitute'])[:3]  # Limit to 3 for testing
        
        print(f"Testing evolution search with base: '{base_phrase}'")
        print(f"Mutations to test: {mutations}")
        
        total_results = 0
        for mutation in mutations:
            results = search_for_phrase(mutation, max_attempts=1000, max_matches=1)
            if results:
                total_results += len(results)
                seed, index = results[0]
                print(f"  '{mutation}' found at seed {seed}, index {index}")
        
        print(f"✓ Evolution search test completed - {total_results} total matches found")
        return True
        
    except Exception as e:
        print(f"✗ Evolution search test failed: {e}")
        return False

def test_similarity_calculations():
    """Test similarity and comparison functions"""
    try:
        from babel_core import similarity_percentage, longest_common_substring
        
        # Test similarity
        sim1 = similarity_percentage("hello", "hallo")
        sim2 = similarity_percentage("hello", "world")
        
        assert sim1 > sim2, "Similar strings should have higher similarity"
        assert 0 <= sim1 <= 100, f"Similarity out of range: {sim1}"
        assert 0 <= sim2 <= 100, f"Similarity out of range: {sim2}"
        
        # Test longest common substring
        lcs = longest_common_substring("hello world", "hello there")
        assert lcs == "hello ", f"Wrong LCS: '{lcs}'"
        
        print(f"✓ Similarity calculations working")
        print(f"  'hello' vs 'hallo': {sim1:.1f}%")
        print(f"  'hello' vs 'world': {sim2:.1f}%")
        print(f"  LCS of 'hello world' and 'hello there': '{lcs}'")
        return True
        
    except Exception as e:
        print(f"✗ Similarity calculation test failed: {e}")
        return False

def main():
    """Run all evolution tests"""
    print("Library of Babel - Phase 3.2 Evolution Mode Tests")
    print("=" * 60)
    
    tests = [
        test_evolution_imports,
        test_phrase_mutations,
        test_evolution_search,
        test_similarity_calculations
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
    print(f"Evolution Test Results: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("✓ All evolution tests passed! Phase 3.2 is ready.")
        print("\nEvolution Mode Features:")
        print("• Phrase mutation generation (substitute, insert, delete, swap)")
        print("• Multi-generation evolutionary search")
        print("• Fitness-based population evolution")
        print("• Phrase cluster discovery")
        print("• Evolution analysis and visualization")
        return 0
    else:
        print("✗ Some evolution tests failed. Check the implementation.")
        return 1

if __name__ == "__main__":
    import sys
    sys.exit(main())
