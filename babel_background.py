import time
import json
import os
import datetime
from babel import generate_page, validate_phrase, ALPHABET

TERMS_FILE = 'search_terms.txt'
PROGRESS_FILE = 'background_progress.json'
RESULTS_FILE = 'background_results.json'
PAGE_LENGTH = 3200
SLEEP_SECONDS = 0  # Time between each page search


def load_search_terms():
    if not os.path.exists(TERMS_FILE):
        print(f"No {TERMS_FILE} found. Please create it with one phrase per line.")
        return []
    with open(TERMS_FILE, 'r', encoding='utf-8') as f:
        terms = [line.strip().lower() for line in f if line.strip()]
    # Validate all terms
    valid_terms = []
    for term in terms:
        try:
            validate_phrase(term)
            valid_terms.append(term)
        except Exception as e:
            print(f"Skipping invalid term '{term}': {e}")
    return valid_terms

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('last_seed', 0)
    return 0

def save_progress(seed):
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump({'last_seed': seed}, f)

def append_result(result):
    results = []
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE, 'r', encoding='utf-8') as f:
            try:
                results = json.load(f)
            except Exception:
                results = []
    results.append(result)
    with open(RESULTS_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

def main():
    print("[Babel Background Searcher] Starting...")
    terms = load_search_terms()
    if not terms:
        print("No valid search terms found. Exiting.")
        return
    print(f"Loaded {len(terms)} search terms.")
    seed = load_progress()
    print(f"Resuming from seed {seed}.")
    try:
        while True:
            page = generate_page(seed, length=PAGE_LENGTH)
            for term in terms:
                idx = page.find(term)
                if idx != -1:
                    result = {
                        'phrase': term,
                        'seed': seed,
                        'index': idx,
                        'timestamp': datetime.datetime.now().isoformat()
                    }
                    print(f"[FOUND] '{term}' at seed {seed}, index {idx}")
                    append_result(result)
            seed += 1
            save_progress(seed)
            time.sleep(SLEEP_SECONDS)
    except KeyboardInterrupt:
        print("\n[Babel Background Searcher] Stopped by user.")
        save_progress(seed)

if __name__ == "__main__":
    main()
