"""
babel_core.py

Core deterministic page generation logic, cryptographic hashing, 
entropy calculations, and fundamental Library of Babel operations.

This module contains the essential mathematical and algorithmic 
foundations that power the Library of Babel searcher.
"""

import random
import hashlib
import math
from collections import Counter
from typing import Dict, Tuple, List, Optional

# Fixed character set used by the Library
ALPHABET = "abcdefghijklmnopqrstuvwxyz ,."
PAGE_LENGTH = 3200

def generate_page(seed: int, length: int = PAGE_LENGTH) -> str:
    """
    Generate a deterministic page of text using a fixed seed.
    
    Args:
        seed: Integer seed for reproducible random generation
        length: Number of characters to generate (default: 3200)
        
    Returns:
        String containing the generated page content
    """
    rng = random.Random(seed)
    return ''.join(rng.choices(ALPHABET, k=length))

def compute_page_hash(page: str) -> str:
    """
    Compute SHA256 hash of a page for verification and deduplication.
    
    Args:
        page: The page content to hash
        
    Returns:
        Hexadecimal string representation of the SHA256 hash
    """
    return hashlib.sha256(page.encode('utf-8')).hexdigest()

def validate_phrase(phrase: str) -> bool:
    """
    Validate that a phrase contains only allowed characters.
    
    Args:
        phrase: The phrase to validate
        
    Returns:
        True if valid, raises ValueError if invalid
    """
    if not phrase:
        raise ValueError("Phrase cannot be empty")
    
    allowed = set(ALPHABET)
    invalid_chars = [c for c in phrase if c not in allowed]
    
    if invalid_chars:
        raise ValueError(f"Phrase contains invalid characters: {invalid_chars}. "
                        f"Allowed characters: {ALPHABET}")
    
    return True

def compute_entropy(text: str) -> float:
    """
    Calculate Shannon entropy of text to measure randomness.
    
    Args:
        text: The text to analyze
        
    Returns:
        Entropy value in bits (0 = completely predictable, higher = more random)
    """
    if not text:
        return 0.0
    
    # Count character frequencies
    char_counts = Counter(text)
    text_length = len(text)
    
    # Calculate entropy
    entropy = 0.0
    for count in char_counts.values():
        probability = count / text_length
        if probability > 0:
            entropy -= probability * math.log2(probability)
    
    return entropy

def char_frequency_analysis(text: str) -> Dict[str, float]:
    """
    Analyze character frequency distribution in text.
    
    Args:
        text: The text to analyze
        
    Returns:
        Dictionary mapping characters to their frequency percentages
    """
    if not text:
        return {}
    
    char_counts = Counter(text)
    text_length = len(text)
    
    return {char: (count / text_length) * 100 
            for char, count in char_counts.items()}

def longest_common_substring(s1: str, s2: str) -> str:
    """
    Find the longest common substring between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        The longest common substring
    """
    if not s1 or not s2:
        return ""
    
    # Dynamic programming approach
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    max_length = 0
    ending_pos = 0
    
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
                if dp[i][j] > max_length:
                    max_length = dp[i][j]
                    ending_pos = i
            else:
                dp[i][j] = 0
    
    return s1[ending_pos - max_length:ending_pos]

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Calculate Levenshtein (edit) distance between two strings.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Minimum number of edits (insertions, deletions, substitutions) needed
    """
    if not s1:
        return len(s2)
    if not s2:
        return len(s1)
    
    # Create matrix
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    
    # Initialize base cases
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    
    # Fill matrix
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = 1 + min(
                    dp[i - 1][j],      # deletion
                    dp[i][j - 1],      # insertion
                    dp[i - 1][j - 1]   # substitution
                )
    
    return dp[m][n]

def similarity_percentage(s1: str, s2: str) -> float:
    """
    Calculate similarity percentage between two strings using Levenshtein distance.
    
    Args:
        s1: First string
        s2: Second string
        
    Returns:
        Similarity percentage (0-100)
    """
    if not s1 and not s2:
        return 100.0
    if not s1 or not s2:
        return 0.0
    
    max_length = max(len(s1), len(s2))
    distance = levenshtein_distance(s1, s2)
    
    return ((max_length - distance) / max_length) * 100

def format_page_output(page_text: str, width: int = 80, 
                      highlight: Optional[str] = None, 
                      highlight_index: Optional[int] = None) -> str:
    """
    Format page text for display with optional highlighting.
    
    Args:
        page_text: The text to format
        width: Line width for wrapping
        highlight: Phrase to highlight
        highlight_index: Starting index of phrase to highlight
        
    Returns:
        Formatted text with line breaks
    """
    if highlight and highlight_index is not None:
        before = page_text[:highlight_index]
        match = page_text[highlight_index:highlight_index + len(highlight)]
        after = page_text[highlight_index + len(highlight):]
        # Use ANSI escape codes for terminal highlighting
        match = f"\033[1;31m{match}\033[0m"
        page_text = before + match + after
    
    # Wrap text to specified width
    lines = [page_text[i:i + width] for i in range(0, len(page_text), width)]
    return '\n'.join(lines)

def is_duplicate_content(page1: str, page2: str) -> bool:
    """
    Check if two pages have identical content using hash comparison.
    
    Args:
        page1: First page content
        page2: Second page content
        
    Returns:
        True if pages are identical
    """
    return compute_page_hash(page1) == compute_page_hash(page2)

def analyze_page_patterns(page: str, pattern_length: int = 3) -> Dict[str, int]:
    """
    Analyze repeating patterns in a page.
    
    Args:
        page: The page content to analyze
        pattern_length: Length of patterns to look for
        
    Returns:
        Dictionary mapping patterns to their occurrence counts
    """
    patterns = {}
    
    for i in range(len(page) - pattern_length + 1):
        pattern = page[i:i + pattern_length]
        patterns[pattern] = patterns.get(pattern, 0) + 1
    
    # Return only patterns that occur more than once
    return {pattern: count for pattern, count in patterns.items() if count > 1}

def get_page_statistics(page: str) -> Dict[str, any]:
    """
    Generate comprehensive statistics for a page.
    
    Args:
        page: The page content to analyze
        
    Returns:
        Dictionary containing various page statistics
    """
    return {
        'length': len(page),
        'entropy': compute_entropy(page),
        'hash': compute_page_hash(page),
        'char_frequencies': char_frequency_analysis(page),
        'unique_chars': len(set(page)),
        'most_common_char': Counter(page).most_common(1)[0] if page else None,
        'patterns_3char': len(analyze_page_patterns(page, 3)),
        'patterns_4char': len(analyze_page_patterns(page, 4))
    }

def compare_pages(page1: str, page2: str) -> Dict[str, any]:
    """
    Comprehensive comparison between two pages.
    
    Args:
        page1: First page content
        page2: Second page content
        
    Returns:
        Dictionary containing detailed comparison metrics
    """
    if not page1 or not page2:
        return {}
    
    # Basic metrics
    length_diff = abs(len(page1) - len(page2))
    hash1 = compute_page_hash(page1)
    hash2 = compute_page_hash(page2)
    are_identical = hash1 == hash2
    
    # Content similarity
    similarity_pct = similarity_percentage(page1, page2)
    lcs = longest_common_substring(page1, page2)
    edit_distance = levenshtein_distance(page1, page2)
    
    # Character frequency comparison
    freq1 = char_frequency_analysis(page1)
    freq2 = char_frequency_analysis(page2)
    
    # Calculate frequency difference
    all_chars = set(freq1.keys()) | set(freq2.keys())
    freq_diff = sum(abs(freq1.get(char, 0) - freq2.get(char, 0)) for char in all_chars)
    
    # Entropy comparison
    entropy1 = compute_entropy(page1)
    entropy2 = compute_entropy(page2)
    entropy_diff = abs(entropy1 - entropy2)
    
    # Pattern analysis
    patterns1 = analyze_page_patterns(page1, 3)
    patterns2 = analyze_page_patterns(page2, 3)
    common_patterns = set(patterns1.keys()) & set(patterns2.keys())
    
    return {
        'identical': are_identical,
        'hash1': hash1,
        'hash2': hash2,
        'length_diff': length_diff,
        'similarity_percentage': similarity_pct,
        'longest_common_substring': lcs,
        'lcs_length': len(lcs),
        'edit_distance': edit_distance,
        'entropy1': entropy1,
        'entropy2': entropy2,
        'entropy_difference': entropy_diff,
        'frequency_difference': freq_diff,
        'common_patterns': len(common_patterns),
        'total_patterns1': len(patterns1),
        'total_patterns2': len(patterns2),
        'pattern_overlap_ratio': len(common_patterns) / max(len(patterns1), len(patterns2), 1)
    }

def highlight_differences(page1: str, page2: str, context_chars: int = 50) -> List[Dict[str, any]]:
    """
    Find and highlight character-level differences between two pages.
    
    Args:
        page1: First page content
        page2: Second page content
        context_chars: Number of context characters around each difference
        
    Returns:
        List of difference regions with context
    """
    differences = []
    
    # Use dynamic programming to find optimal alignment
    m, n = len(page1), len(page2)
    
    # Simple approach: find differing regions
    min_len = min(m, n)
    max_len = max(m, n)
    
    i = 0
    while i < min_len:
        if page1[i] != page2[i]:
            # Found difference, find the extent
            start = i
            while i < min_len and page1[i] != page2[i]:
                i += 1
            end = i
            
            # Extract context
            context_start = max(0, start - context_chars)
            context_end = min(min_len, end + context_chars)
            
            differences.append({
                'position': start,
                'length': end - start,
                'page1_text': page1[start:end],
                'page2_text': page2[start:end],
                'context1': page1[context_start:context_end],
                'context2': page2[context_start:context_end],
                'context_start': context_start,
                'context_end': context_end
            })
        else:
            i += 1
    
    # Handle length differences
    if m != n:
        longer_page = page1 if m > n else page2
        shorter_len = min_len
        
        differences.append({
            'position': shorter_len,
            'length': abs(m - n),
            'page1_text': page1[shorter_len:] if m > n else '',
            'page2_text': page2[shorter_len:] if n > m else '',
            'context1': page1[max(0, shorter_len - context_chars):shorter_len + context_chars],
            'context2': page2[max(0, shorter_len - context_chars):shorter_len + context_chars],
            'context_start': max(0, shorter_len - context_chars),
            'context_end': shorter_len + context_chars,
            'is_length_diff': True
        })
    
    return differences

def find_common_substrings(page1: str, page2: str, min_length: int = 5) -> List[Dict[str, any]]:
    """
    Find all common substrings between two pages.
    
    Args:
        page1: First page content
        page2: Second page content
        min_length: Minimum length of substrings to consider
        
    Returns:
        List of common substrings with their positions
    """
    common_substrings = []
    
    for i in range(len(page1) - min_length + 1):
        for length in range(min_length, min(len(page1) - i + 1, 100)):  # Limit to avoid huge strings
            substring = page1[i:i + length]
            
            # Find all occurrences in page2
            pos2 = 0
            while True:
                pos2 = page2.find(substring, pos2)
                if pos2 == -1:
                    break
                
                common_substrings.append({
                    'substring': substring,
                    'length': length,
                    'pos1': i,
                    'pos2': pos2,
                    'page1_context': page1[max(0, i-10):i+length+10],
                    'page2_context': page2[max(0, pos2-10):pos2+length+10]
                })
                
                pos2 += 1
    
    # Remove duplicates and sort by length (descending)
    seen = set()
    unique_substrings = []
    
    for item in sorted(common_substrings, key=lambda x: x['length'], reverse=True):
        key = (item['substring'], item['pos1'], item['pos2'])
        if key not in seen:
            seen.add(key)
            unique_substrings.append(item)
    
    return unique_substrings[:50]  # Limit to top 50

def calculate_page_similarity_matrix(pages: List[str]) -> List[List[float]]:
    """
    Calculate similarity matrix for multiple pages.
    
    Args:
        pages: List of page contents
        
    Returns:
        2D matrix of similarity percentages
    """
    n = len(pages)
    matrix = [[0.0 for _ in range(n)] for _ in range(n)]
    
    for i in range(n):
        for j in range(n):
            if i == j:
                matrix[i][j] = 100.0
            else:
                matrix[i][j] = similarity_percentage(pages[i], pages[j])
    
    return matrix

def detect_twin_pages(page: str, seed_range: int = 1000, similarity_threshold: float = 95.0) -> List[Dict[str, any]]:
    """
    Detect pages that are very similar to the given page (potential twins).
    
    Args:
        page: Page content to find twins for
        seed_range: Range of seeds to check around the original
        similarity_threshold: Minimum similarity percentage to consider as twin
        
    Returns:
        List of twin page information
    """
    twins = []
    page_hash = compute_page_hash(page)
    
    # This is a placeholder - in practice, you'd search systematically
    # For demonstration, we'll check a few nearby seeds
    for offset in range(-seed_range, seed_range + 1):
        if offset == 0:
            continue
            
        # Generate a test page (in practice, you'd know the original seed)
        test_page = generate_page(abs(offset), len(page))
        
        if compute_page_hash(test_page) == page_hash:
            twins.append({
                'seed': abs(offset),
                'page': test_page,
                'similarity': 100.0,
                'type': 'identical_hash'
            })
        else:
            similarity = similarity_percentage(page, test_page)
            if similarity >= similarity_threshold:
                twins.append({
                    'seed': abs(offset),
                    'page': test_page,
                    'similarity': similarity,
                    'type': 'high_similarity'
                })
    
    return sorted(twins, key=lambda x: x['similarity'], reverse=True)
