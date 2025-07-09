#!/usr/bin/env python3
"""
Library of Babel Searcher - Core Engine
Created by: The Unlearned
In tribute to: Jorge Luis Borges and his infinite vision

"I am not sure that I exist, actually. I am all the writers that I have read, 
all the people that I have met, all the women that I have loved; 
all the cities I have visited."
"""

import random
import argparse
import sys
import re

# Fixed character set used by the Library
ALPHABET = "abcdefghijklmnopqrstuvwxyz ,."

def generate_page(seed, length=3200):
    """Generate a random page of text using a fixed seed."""
    rng = random.Random(seed)
    return ''.join(rng.choices(ALPHABET, k=length))

def search_for_phrase(phrase, max_attempts=100000, max_matches=5, page_length=3200):
    """Search for a phrase in randomly generated pages. Returns a list of (seed, index)."""
    found = []
    for i in range(max_attempts):
        page = generate_page(i, length=page_length)
        idx = page.find(phrase)
        if idx != -1:
            found.append((i, idx))
            if len(found) >= max_matches:
                break
    return found

def format_page_output(page_text, width=80, highlight=None, highlight_index=None):
    """Format the page for display, optionally highlighting a phrase at highlight_index."""
    if highlight and highlight_index is not None:
        before = page_text[:highlight_index]
        match = page_text[highlight_index:highlight_index+len(highlight)]
        after = page_text[highlight_index+len(highlight):]
        # Use ANSI escape codes for highlighting
        match = f"\033[1;31m{match}\033[0m"
        page_text = before + match + after
    lines = [page_text[i:i+width] for i in range(0, len(page_text), width)]
    return '\n'.join(lines)

def validate_phrase(phrase):
    """Ensure the phrase contains only allowed characters."""
    allowed = set(ALPHABET)
    if not phrase or not all(c in allowed for c in phrase):
        raise ValueError(f"Phrase must only contain: {ALPHABET}")

def save_results_to_file(results, filename):
    """Save search results to a file."""
    with open(filename, 'w', encoding='utf-8') as f:
        for i, (seed, index, page, phrase) in enumerate(results, 1):
            f.write(f"\n📖 Match {i}: Seed={seed}, Index={index}\n")
            formatted = format_page_output(page, highlight=phrase, highlight_index=index)
            f.write(formatted + '\n')
            f.write(f"\n👉 Phrase starts at character {index}\n")

def run_tests():
    """Simple test suite for core functions."""
    test_phrase = "abc"
    page = generate_page(42, length=100)
    assert len(page) == 100
    assert all(c in ALPHABET for c in page)
    # Insert phrase at a known location
    page = page[:10] + test_phrase + page[13:]
    idx = page.find(test_phrase)
    assert idx == 10
    print("All tests passed.")

def main():
    parser = argparse.ArgumentParser(description="Library of Babel phrase searcher.")
    parser.add_argument("phrase", nargs="?", help="Phrase to search for.")
    parser.add_argument("--max-matches", type=int, default=5, help="Number of matches to find.")
    parser.add_argument("--max-attempts", type=int, default=100000, help="Maximum number of pages to search.")
    parser.add_argument("--page-length", type=int, default=3200, help="Length of each page.")
    parser.add_argument("--save", type=str, help="File to save results to.")
    parser.add_argument("--test", action="store_true", help="Run tests and exit.")
    args = parser.parse_args()

    if args.test:
        run_tests()
        sys.exit(0)

    phrase = args.phrase
    if not phrase:
        phrase = input("Enter a phrase to search for: ").lower()
    else:
        phrase = phrase.lower()
    try:
        validate_phrase(phrase)
    except ValueError as e:
        print(e)
        sys.exit(1)

    print(f"Searching for '{phrase}' in random pages...")
    matches = search_for_phrase(phrase, max_attempts=args.max_attempts, max_matches=args.max_matches, page_length=args.page_length)

    if matches:
        results = []
        for i, (seed, index) in enumerate(matches, 1):
            print(f"\n📖 Match {i}: Seed={seed}, Index={index}")
            page = generate_page(seed, length=args.page_length)
            formatted = format_page_output(page, highlight=phrase, highlight_index=index)
            print(formatted)
            print(f"\n👉 Phrase starts at character {index}")
            results.append((seed, index, page, phrase))
        if args.save:
            save_results_to_file(results, args.save)
            print(f"Results saved to {args.save}")
    else:
        print("No matches found in sample search range.")

if __name__ == "__main__":
    main()
