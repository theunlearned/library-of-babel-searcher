"""
babel_tools.py

Search algorithms, coordinate mathematics, pattern matching utilities,
and helper functions for the Library of Babel searcher.

This module contains specialized tools for navigating and searching
the infinite Library space.
"""

import re
import math
from typing import List, Tuple, Optional, Generator, Dict, Any
from babel_core import generate_page, validate_phrase, PAGE_LENGTH

# Library structure constants (following Borges' architecture)
WALLS_PER_HEXAGON = 6
SHELVES_PER_WALL = 4
VOLUMES_PER_SHELF = 10
PAGES_PER_VOLUME = 100

# Calculated constants
PAGES_PER_HEXAGON = WALLS_PER_HEXAGON * SHELVES_PER_WALL * VOLUMES_PER_SHELF * PAGES_PER_VOLUME
VOLUMES_PER_HEXAGON = WALLS_PER_HEXAGON * SHELVES_PER_WALL * VOLUMES_PER_SHELF
SHELVES_PER_HEXAGON = WALLS_PER_HEXAGON * SHELVES_PER_WALL

class LibraryCoordinates:
    """Represents a location in the Library using Borges' hierarchical system."""
    
    def __init__(self, hexagon: int = 0, wall: int = 0, shelf: int = 0, 
                 volume: int = 0, page: int = 0):
        self.hexagon = hexagon
        self.wall = wall
        self.shelf = shelf
        self.volume = volume
        self.page = page
    
    def __str__(self) -> str:
        return f"H{self.hexagon}:W{self.wall}:S{self.shelf}:V{self.volume}:P{self.page}"
    
    def __repr__(self) -> str:
        return f"LibraryCoordinates({self.hexagon}, {self.wall}, {self.shelf}, {self.volume}, {self.page})"

def seed_to_coordinates(seed: int) -> LibraryCoordinates:
    """
    Convert a linear seed number to Library coordinates.
    
    Args:
        seed: Linear seed number
        
    Returns:
        LibraryCoordinates object representing the location
    """
    page = seed % PAGES_PER_VOLUME
    remaining = seed // PAGES_PER_VOLUME
    
    volume = remaining % VOLUMES_PER_SHELF
    remaining = remaining // VOLUMES_PER_SHELF
    
    shelf = remaining % SHELVES_PER_WALL
    remaining = remaining // SHELVES_PER_WALL
    
    wall = remaining % WALLS_PER_HEXAGON
    hexagon = remaining // WALLS_PER_HEXAGON
    
    return LibraryCoordinates(hexagon, wall, shelf, volume, page)

def coordinates_to_seed(coords: LibraryCoordinates) -> int:
    """
    Convert Library coordinates to a linear seed number.
    
    Args:
        coords: LibraryCoordinates object
        
    Returns:
        Linear seed number
    """
    return (coords.hexagon * PAGES_PER_HEXAGON + 
            coords.wall * SHELVES_PER_WALL * VOLUMES_PER_SHELF * PAGES_PER_VOLUME +
            coords.shelf * VOLUMES_PER_SHELF * PAGES_PER_VOLUME +
            coords.volume * PAGES_PER_VOLUME +
            coords.page)

def get_adjacent_seeds(seed: int, radius: int = 1) -> List[int]:
    """
    Get seeds for pages adjacent to a given seed.
    
    Args:
        seed: Central seed
        radius: How far to extend in each direction
        
    Returns:
        List of adjacent seed numbers
    """
    adjacent = []
    
    for offset in range(-radius, radius + 1):
        new_seed = seed + offset
        if new_seed >= 0:  # Ensure non-negative seeds
            adjacent.append(new_seed)
    
    return adjacent

def get_grid_seeds(center_seed: int, grid_size: int = 3) -> List[List[int]]:
    """
    Get a grid of seeds around a center seed for exploration.
    
    Args:
        center_seed: Center of the grid
        grid_size: Size of the grid (should be odd)
        
    Returns:
        2D list representing the grid of seeds
    """
    half_size = grid_size // 2
    grid = []
    
    for row in range(-half_size, half_size + 1):
        grid_row = []
        for col in range(-half_size, half_size + 1):
            # Calculate seed based on row/column offset
            seed = center_seed + (row * 100) + col  # Arbitrary spacing
            if seed >= 0:
                grid_row.append(seed)
            else:
                grid_row.append(0)
        grid.append(grid_row)
    
    return grid

def wildcard_match(text: str, pattern: str) -> bool:
    """
    Check if text matches a pattern with wildcards.
    
    Supports:
    - * for any sequence of characters
    - ? for any single character
    
    Args:
        text: Text to check
        pattern: Pattern with wildcards
        
    Returns:
        True if text matches pattern
    """
    # Convert wildcard pattern to regex
    regex_pattern = pattern.replace('*', '.*').replace('?', '.')
    return bool(re.match(regex_pattern, text))

def find_wildcard_matches(page: str, pattern: str) -> List[Tuple[int, str]]:
    """
    Find all matches of a wildcard pattern in a page.
    
    Args:
        page: Page content to search
        pattern: Pattern with wildcards
        
    Returns:
        List of (index, matched_text) tuples
    """
    matches = []
    
    # Convert wildcard pattern to regex
    regex_pattern = pattern.replace('*', '.*?').replace('?', '.')
    
    for match in re.finditer(regex_pattern, page):
        matches.append((match.start(), match.group()))
    
    return matches

def search_for_phrase(phrase: str, max_attempts: int = 100000, 
                     max_matches: int = 5, page_length: int = PAGE_LENGTH,
                     start_seed: int = 0) -> List[Tuple[int, int]]:
    """
    Search for a phrase in randomly generated pages.
    
    Args:
        phrase: Phrase to search for
        max_attempts: Maximum number of pages to search
        max_matches: Maximum number of matches to find
        page_length: Length of each generated page
        start_seed: Starting seed for search
        
    Returns:
        List of (seed, index) tuples where phrase was found
    """
    validate_phrase(phrase)
    found = []
    
    for i in range(start_seed, start_seed + max_attempts):
        page = generate_page(i, length=page_length)
        idx = page.find(phrase)
        if idx != -1:
            found.append((i, idx))
            if len(found) >= max_matches:
                break
    
    return found

def search_with_wildcards(pattern: str, max_attempts: int = 100000,
                         max_matches: int = 5, page_length: int = PAGE_LENGTH,
                         start_seed: int = 0) -> List[Tuple[int, int, str]]:
    """
    Search for a wildcard pattern in randomly generated pages.
    
    Args:
        pattern: Pattern with wildcards to search for
        max_attempts: Maximum number of pages to search
        max_matches: Maximum number of matches to find
        page_length: Length of each generated page
        start_seed: Starting seed for search
        
    Returns:
        List of (seed, index, matched_text) tuples
    """
    found = []
    
    for i in range(start_seed, start_seed + max_attempts):
        page = generate_page(i, length=page_length)
        matches = find_wildcard_matches(page, pattern)
        
        for idx, matched_text in matches:
            found.append((i, idx, matched_text))
            if len(found) >= max_matches:
                return found
    
    return found

def generate_phrase_mutations(base_phrase: str, mutation_types: List[str] = None) -> List[str]:
    """
    Generate variations/mutations of a phrase for evolutionary search.
    
    Args:
        base_phrase: Original phrase to mutate
        mutation_types: Types of mutations to apply ['substitute', 'insert', 'delete', 'swap']
        
    Returns:
        List of mutated phrases
    """
    if mutation_types is None:
        mutation_types = ['substitute', 'insert', 'delete', 'swap']
    
    from babel_core import ALPHABET
    mutations = []
    
    # Substitution mutations
    if 'substitute' in mutation_types:
        for i in range(len(base_phrase)):
            for char in ALPHABET:
                if char != base_phrase[i]:
                    mutated = base_phrase[:i] + char + base_phrase[i+1:]
                    mutations.append(mutated)
    
    # Insertion mutations
    if 'insert' in mutation_types:
        for i in range(len(base_phrase) + 1):
            for char in ALPHABET:
                mutated = base_phrase[:i] + char + base_phrase[i:]
                mutations.append(mutated)
    
    # Deletion mutations
    if 'delete' in mutation_types and len(base_phrase) > 1:
        for i in range(len(base_phrase)):
            mutated = base_phrase[:i] + base_phrase[i+1:]
            mutations.append(mutated)
    
    # Swap mutations
    if 'swap' in mutation_types and len(base_phrase) > 1:
        for i in range(len(base_phrase) - 1):
            mutated = (base_phrase[:i] + 
                      base_phrase[i+1] + 
                      base_phrase[i] + 
                      base_phrase[i+2:])
            mutations.append(mutated)
    
    # Remove duplicates and return
    return list(set(mutations))

def find_partial_matches(page: str, target_phrase: str, min_match_length: int = 3) -> List[Tuple[int, str, float]]:
    """
    Find partial matches of a phrase in a page.
    
    Args:
        page: Page content to search
        target_phrase: Phrase to find partial matches for
        min_match_length: Minimum length of partial matches
        
    Returns:
        List of (index, partial_match, similarity_score) tuples
    """
    from babel_core import similarity_percentage
    
    matches = []
    target_len = len(target_phrase)
    
    # Search for substrings of various lengths
    for length in range(min_match_length, target_len + 1):
        for i in range(len(page) - length + 1):
            substring = page[i:i + length]
            similarity = similarity_percentage(substring, target_phrase[:length])
            
            # Include matches above a threshold
            if similarity > 70:  # Adjustable threshold
                matches.append((i, substring, similarity))
    
    # Sort by similarity score (descending)
    matches.sort(key=lambda x: x[2], reverse=True)
    
    # Remove overlapping matches, keeping highest scoring
    filtered_matches = []
    used_positions = set()
    
    for idx, match, score in matches:
        if not any(pos in used_positions for pos in range(idx, idx + len(match))):
            filtered_matches.append((idx, match, score))
            used_positions.update(range(idx, idx + len(match)))
    
    return filtered_matches

def calculate_search_efficiency(attempts: int, matches_found: int, time_elapsed: float) -> Dict[str, float]:
    """
    Calculate search efficiency metrics.
    
    Args:
        attempts: Number of pages searched
        matches_found: Number of matches found
        time_elapsed: Time taken in seconds
        
    Returns:
        Dictionary of efficiency metrics
    """
    if attempts == 0 or time_elapsed == 0:
        return {'pages_per_second': 0, 'matches_per_hour': 0, 'success_rate': 0}
    
    pages_per_second = attempts / time_elapsed
    matches_per_hour = (matches_found / time_elapsed) * 3600
    success_rate = (matches_found / attempts) * 100
    
    return {
        'pages_per_second': pages_per_second,
        'matches_per_hour': matches_per_hour,
        'success_rate': success_rate,
        'average_time_per_match': time_elapsed / matches_found if matches_found > 0 else 0
    }

def estimate_search_time(target_phrase: str, desired_matches: int = 1) -> Dict[str, Any]:
    """
    Estimate time required to find a phrase based on its probability.
    
    Args:
        target_phrase: Phrase to estimate search time for
        desired_matches: Number of matches desired
        
    Returns:
        Dictionary with time estimates and probability info
    """
    from babel_core import ALPHABET
    
    # Calculate probability of finding phrase
    alphabet_size = len(ALPHABET)
    phrase_length = len(target_phrase)
    
    # Probability of exact match at any given position
    exact_probability = (1 / alphabet_size) ** phrase_length
    
    # Expected pages to check for one match
    expected_pages = 1 / exact_probability
    
    # For multiple matches
    expected_pages_total = expected_pages * desired_matches
    
    # Rough time estimates (based on typical performance)
    pages_per_second = 1000  # Estimated processing rate
    estimated_seconds = expected_pages_total / pages_per_second
    
    return {
        'exact_probability': exact_probability,
        'expected_pages_per_match': expected_pages,
        'expected_pages_total': expected_pages_total,
        'estimated_seconds': estimated_seconds,
        'estimated_hours': estimated_seconds / 3600,
        'estimated_days': estimated_seconds / (3600 * 24),
        'phrase_length': phrase_length,
        'alphabet_size': alphabet_size
    }

def find_echo_pages(seed1: int, seed2: int, page_length: int = PAGE_LENGTH) -> Dict[str, any]:
    """
    Compare two pages by seed to detect echo patterns.
    
    Args:
        seed1: First page seed
        seed2: Second page seed
        page_length: Length of pages to generate
        
    Returns:
        Dictionary with echo analysis results
    """
    from babel_core import generate_page, compare_pages
    
    page1 = generate_page(seed1, page_length)
    page2 = generate_page(seed2, page_length)
    
    comparison = compare_pages(page1, page2)
    
    # Add seed information
    comparison.update({
        'seed1': seed1,
        'seed2': seed2,
        'seed_difference': abs(seed1 - seed2),
        'page1': page1,
        'page2': page2
    })
    
    return comparison

def search_for_similar_pages(reference_seed: int, search_range: int = 10000, 
                           similarity_threshold: float = 80.0,
                           max_results: int = 10) -> List[Dict[str, any]]:
    """
    Search for pages similar to a reference page within a seed range.
    
    Args:
        reference_seed: Seed of the reference page
        search_range: Range of seeds to search (±range around reference)
        similarity_threshold: Minimum similarity percentage
        max_results: Maximum number of results to return
        
    Returns:
        List of similar pages with comparison data
    """
    from babel_core import generate_page, similarity_percentage
    
    reference_page = generate_page(reference_seed, PAGE_LENGTH)
    similar_pages = []
    
    start_seed = max(0, reference_seed - search_range)
    end_seed = reference_seed + search_range
    
    for seed in range(start_seed, end_seed + 1):
        if seed == reference_seed:
            continue
            
        test_page = generate_page(seed, PAGE_LENGTH)
        similarity = similarity_percentage(reference_page, test_page)
        
        if similarity >= similarity_threshold:
            similar_pages.append({
                'reference_seed': reference_seed,
                'similar_seed': seed,
                'similarity': similarity,
                'seed_distance': abs(seed - reference_seed),
                'page': test_page
            })
            
            if len(similar_pages) >= max_results:
                break
    
    return sorted(similar_pages, key=lambda x: x['similarity'], reverse=True)

def generate_comparison_grid(center_seed: int, grid_size: int = 3) -> Dict[str, any]:
    """
    Generate a grid of pages around a center seed for comparison.
    
    Args:
        center_seed: Central seed for the grid
        grid_size: Size of the grid (should be odd number)
        
    Returns:
        Dictionary with grid data and comparison metrics
    """
    from babel_core import generate_page, calculate_page_similarity_matrix
    
    half_size = grid_size // 2
    grid_seeds = []
    grid_pages = []
    
    # Generate grid of seeds and pages
    for row in range(-half_size, half_size + 1):
        row_seeds = []
        row_pages = []
        for col in range(-half_size, half_size + 1):
            seed = center_seed + (row * 1000) + col  # Spacing for interesting variations
            if seed < 0:
                seed = abs(seed)
            
            page = generate_page(seed, PAGE_LENGTH)
            row_seeds.append(seed)
            row_pages.append(page)
        
        grid_seeds.append(row_seeds)
        grid_pages.append(row_pages)
    
    # Flatten for similarity matrix calculation
    flat_pages = [page for row in grid_pages for page in row]
    similarity_matrix = calculate_page_similarity_matrix(flat_pages)
    
    return {
        'center_seed': center_seed,
        'grid_size': grid_size,
        'grid_seeds': grid_seeds,
        'grid_pages': grid_pages,
        'similarity_matrix': similarity_matrix,
        'center_index': half_size * grid_size + half_size  # Index of center in flat list
    }

def analyze_page_neighborhood(seed: int, radius: int = 5) -> Dict[str, any]:
    """
    Analyze the neighborhood of pages around a given seed.
    
    Args:
        seed: Central seed to analyze
        radius: How many seeds to check in each direction
        
    Returns:
        Dictionary with neighborhood analysis
    """
    from babel_core import generate_page, compute_entropy, similarity_percentage
    
    reference_page = generate_page(seed, PAGE_LENGTH)
    neighborhood = []
    
    for offset in range(-radius, radius + 1):
        neighbor_seed = max(0, seed + offset)
        neighbor_page = generate_page(neighbor_seed, PAGE_LENGTH)
        
        similarity = similarity_percentage(reference_page, neighbor_page)
        entropy = compute_entropy(neighbor_page)
        
        neighborhood.append({
            'seed': neighbor_seed,
            'offset': offset,
            'similarity_to_center': similarity,
            'entropy': entropy,
            'page': neighbor_page
        })
    
    # Calculate neighborhood statistics
    similarities = [n['similarity_to_center'] for n in neighborhood if n['offset'] != 0]
    entropies = [n['entropy'] for n in neighborhood]
    
    return {
        'reference_seed': seed,
        'radius': radius,
        'neighborhood': neighborhood,
        'avg_similarity': sum(similarities) / len(similarities) if similarities else 0,
        'max_similarity': max(similarities) if similarities else 0,
        'min_similarity': min(similarities) if similarities else 0,
        'avg_entropy': sum(entropies) / len(entropies),
        'entropy_variation': max(entropies) - min(entropies)
    }

def detect_page_patterns(pages: List[str], pattern_length: int = 10) -> Dict[str, any]:
    """
    Detect common patterns across multiple pages.
    
    Args:
        pages: List of page contents to analyze
        pattern_length: Length of patterns to search for
        
    Returns:
        Dictionary with pattern analysis results
    """
    from babel_core import analyze_page_patterns
    from collections import Counter
    
    all_patterns = Counter()
    page_patterns = []
    
    # Analyze patterns in each page
    for i, page in enumerate(pages):
        patterns = analyze_page_patterns(page, pattern_length)
        page_patterns.append(patterns)
        
        # Add to global pattern count
        for pattern, count in patterns.items():
            all_patterns[pattern] += count
    
    # Find patterns that appear in multiple pages
    cross_page_patterns = {}
    for pattern, total_count in all_patterns.items():
        pages_with_pattern = sum(1 for pp in page_patterns if pattern in pp)
        if pages_with_pattern > 1:
            cross_page_patterns[pattern] = {
                'total_count': total_count,
                'pages_containing': pages_with_pattern,
                'frequency': pages_with_pattern / len(pages)
            }
    
    return {
        'total_pages': len(pages),
        'pattern_length': pattern_length,
        'unique_patterns': len(all_patterns),
        'cross_page_patterns': cross_page_patterns,
        'most_common_patterns': all_patterns.most_common(20),
        'page_pattern_counts': [len(pp) for pp in page_patterns]
    }
