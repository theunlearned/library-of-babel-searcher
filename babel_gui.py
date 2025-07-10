#!/usr/bin/env python3
"""
Library of Babel Searcher - GUI Interface
Created by: The Unlearned
In tribute to: Jorge Luis Borges and his infinite vision

"Real libraries are places where people come together to solve problems, 
to advance learning and to save the world."
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import csv
import json
import datetime
import time
import os
import random
import multiprocessing
import queue
import hashlib
import re
from babel import generate_page, search_for_phrase, format_page_output, validate_phrase, ALPHABET
from babel_core import compute_entropy, get_page_statistics, similarity_percentage, compare_pages, highlight_differences, find_common_substrings
from babel_tools import generate_phrase_mutations, search_with_wildcards, LibraryCoordinates, find_echo_pages, search_for_similar_pages
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import numpy as np
import psutil
import hashlib
import re
import queue

BACKGROUND_RESULTS_FILE = 'background_results.json'
BACKGROUND_PROGRESS_FILE = 'background_progress.json'
PAGE_LENGTH = 3200

def is_duplicate(result, result_list):
    """Check if a (seed, phrase) pair is already in the result_list."""
    return any(r['seed'] == result['seed'] and r['phrase'] == result['phrase'] for r in result_list)

def bg_search_worker(start_seed, step, phrases, result_q, running_flag):
    """Background search worker function for multiprocessing."""
    def compute_hash(page):
        return hashlib.sha256(page.encode('utf-8')).hexdigest()
    
    seed = start_seed
    while running_flag.is_set():
        try:
            page = generate_page(seed, length=PAGE_LENGTH)
            page_hash = compute_hash(page)
            for term in phrases:
                idx = page.find(term)
                if idx != -1:
                    result = {
                        'phrase': term,
                        'seed': seed,
                        'index': idx,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'hash': page_hash
                    }
                    result_q.put(result)
            seed += step
        except Exception:
            seed += step
            continue

class BabelGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library of Babel Searcher")
        self.geometry("1000x800")
        self.resizable(True, True)
        self.results = []
        self.bg_search_phrases = []
        self.bg_search_thread = None
        self.bg_search_running = threading.Event()
        self.bg_search_log = []
        self.bg_num_cores = multiprocessing.cpu_count()
        self.bookmarks = []
        self.result_queue = queue.Queue()
        self.evolution_results = []
        self.evolution_running = False
        self.evolution_thread = None
        self.current_generation = 0
        self.comparison_page1 = None
        self.comparison_page2 = None
        self.comparison_seed1 = None
        self.comparison_seed2 = None
        self.comparison_results = None
        self.create_widgets()
        self.start_queue_processing()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        self.search_tab = ttk.Frame(tab_control)
        self.bg_tab = ttk.Frame(tab_control)
        self.bookmarks_tab = ttk.Frame(tab_control)
        self.analytics_tab = ttk.Frame(tab_control)
        self.coord_tab = ttk.Frame(tab_control)
        self.compare_tab = ttk.Frame(tab_control)
        tab_control.add(self.search_tab, text="Manual Search")
        tab_control.add(self.bg_tab, text="Background Search")
        tab_control.add(self.bookmarks_tab, text="Bookmarks")
        tab_control.add(self.analytics_tab, text="Analytics")
        tab_control.add(self.coord_tab, text="Coordinate Browser")
        tab_control.add(self.compare_tab, text="Page Comparison")
        tab_control.pack(expand=1, fill="both")

        self._create_manual_search_widgets(self.search_tab)
        self._create_bg_search_widgets(self.bg_tab)
        self._create_bookmarks_widgets(self.bookmarks_tab)
        self._create_analytics_widgets(self.analytics_tab)
        self._create_coordinate_browser_widgets(self.coord_tab)
        self._create_page_comparison_widgets(self.compare_tab)

    def _create_manual_search_widgets(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Search Parameters")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Phrase:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.phrase_var = tk.StringVar()
        self.phrase_entry = ttk.Entry(input_frame, textvariable=self.phrase_var, width=40)
        self.phrase_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Max Matches:").grid(row=0, column=2, sticky="e", padx=5)
        self.max_matches_var = tk.IntVar(value=5)
        ttk.Entry(input_frame, textvariable=self.max_matches_var, width=6).grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Max Attempts:").grid(row=0, column=4, sticky="e", padx=5)
        self.max_attempts_var = tk.IntVar(value=100000)
        ttk.Entry(input_frame, textvariable=self.max_attempts_var, width=10).grid(row=0, column=5, padx=5)


"""
Library of Babel Searcher - GUI Interface
Created by: The Unlearned
In tribute to: Jorge Luis Borges and his infinite vision

"Real libraries are places where people come together to solve problems, 
to advance learning and to save the world."
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import threading
import csv
import json
BACKGROUND_RESULTS_FILE = 'background_results.json'
BACKGROUND_PROGRESS_FILE = 'background_progress.json'
PAGE_LENGTH = 3200

def is_duplicate(result, result_list):
    """Check if a (seed, phrase) pair is already in the result_list."""
    return any(r['seed'] == result['seed'] and r['phrase'] == result['phrase'] for r in result_list)

def bg_search_worker(start_seed, step, phrases, result_q, running_flag):
    """Background search worker function for multiprocessing."""
    def compute_hash(page):
        return hashlib.sha256(page.encode('utf-8')).hexdigest()
    
    seed = start_seed
    while running_flag.is_set():
        try:
            page = generate_page(seed, length=PAGE_LENGTH)
            page_hash = compute_hash(page)
            for term in phrases:
                idx = page.find(term)
                if idx != -1:
                    result = {
                        'phrase': term,
                        'seed': seed,
                        'index': idx,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'hash': page_hash
                    }
                    result_q.put(result)
            seed += step
        except Exception:
            seed += step
            continue

class BabelGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Library of Babel Searcher")
        self.geometry("1000x800")
        self.resizable(True, True)
        self.results = []
        self.bg_search_phrases = []
        self.bg_search_thread = None
        self.bg_search_running = threading.Event()
        self.bg_search_log = []
        self.bg_num_cores = multiprocessing.cpu_count()
        self.bookmarks = []
        self.result_queue = queue.Queue()
        self.evolution_results = []
        self.evolution_running = False
        self.evolution_thread = None
        self.current_generation = 0
        self.comparison_page1 = None
        self.comparison_page2 = None
        self.comparison_seed1 = None
        self.comparison_seed2 = None
        self.comparison_results = None
        self.create_widgets()
        self.start_queue_processing()

    def create_widgets(self):
        tab_control = ttk.Notebook(self)
        self.search_tab = ttk.Frame(tab_control)
        self.bg_tab = ttk.Frame(tab_control)
        self.bookmarks_tab = ttk.Frame(tab_control)
        self.analytics_tab = ttk.Frame(tab_control)
        self.coord_tab = ttk.Frame(tab_control)
        self.compare_tab = ttk.Frame(tab_control)
        tab_control.add(self.search_tab, text="Manual Search")
        tab_control.add(self.bg_tab, text="Background Search")
        tab_control.add(self.bookmarks_tab, text="Bookmarks")
        tab_control.add(self.analytics_tab, text="Analytics")
        tab_control.add(self.coord_tab, text="Coordinate Browser")
        tab_control.add(self.compare_tab, text="Page Comparison")
        tab_control.pack(expand=1, fill="both")

        self._create_manual_search_widgets(self.search_tab)
        self._create_bg_search_widgets(self.bg_tab)
        self._create_bookmarks_widgets(self.bookmarks_tab)
        self._create_analytics_widgets(self.analytics_tab)
        self._create_coordinate_browser_widgets(self.coord_tab)
        self._create_page_comparison_widgets(self.compare_tab)

    def _create_manual_search_widgets(self, parent):
        input_frame = ttk.LabelFrame(parent, text="Search Parameters")
        input_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(input_frame, text="Phrase:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.phrase_var = tk.StringVar()
        self.phrase_entry = ttk.Entry(input_frame, textvariable=self.phrase_var, width=40)
        self.phrase_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(input_frame, text="Max Matches:").grid(row=0, column=2, sticky="e", padx=5)
        self.max_matches_var = tk.IntVar(value=5)
        ttk.Entry(input_frame, textvariable=self.max_matches_var, width=6).grid(row=0, column=3, padx=5)

        ttk.Label(input_frame, text="Max Attempts:").grid(row=0, column=4, sticky="e", padx=5)
        self.max_attempts_var = tk.IntVar(value=100000)
        ttk.Entry(input_frame, textvariable=self.max_attempts_var, width=10).grid(row=0, column=5, padx=5)

        ttk.Label(input_frame, text="Page Length:").grid(row=0, column=6, sticky="e", padx=5)
        self.page_length_var = tk.IntVar(value=3200)
        ttk.Entry(input_frame, textvariable=self.page_length_var, width=8).grid(row=0, column=7, padx=5)

        self.search_btn = ttk.Button(input_frame, text="Start Search", command=self.start_search)
        self.search_btn.grid(row=0, column=8, padx=10)

        evolution_frame = ttk.LabelFrame(parent, text="Phrase Evolution Mode")
        evolution_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(evolution_frame, text="Base Phrase:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.evolution_phrase_var = tk.StringVar()
        self.evolution_phrase_entry = ttk.Entry(evolution_frame, textvariable=self.evolution_phrase_var, width=30)
        self.evolution_phrase_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(evolution_frame, text="Mutation Rate:").grid(row=0, column=2, sticky="e", padx=5)
        self.mutation_rate_var = tk.DoubleVar(value=0.3)
        self.mutation_scale = ttk.Scale(evolution_frame, from_=0.1, to=1.0, variable=self.mutation_rate_var, orient="horizontal", length=100)
        self.mutation_scale.grid(row=0, column=3, padx=5, pady=5)
        self.mutation_label = ttk.Label(evolution_frame, text="0.3")
        self.mutation_label.grid(row=0, column=4, padx=5, pady=5)
        self.mutation_scale.configure(command=self.update_mutation_label)

        ttk.Label(evolution_frame, text="Generations:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.generations_var = tk.IntVar(value=5)
        ttk.Entry(evolution_frame, textvariable=self.generations_var, width=6).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(evolution_frame, text="Population Size:").grid(row=1, column=2, sticky="e", padx=5)
        self.population_size_var = tk.IntVar(value=20)
        ttk.Entry(evolution_frame, textvariable=self.population_size_var, width=6).grid(row=1, column=3, sticky="w", padx=5, pady=5)

        self.evolution_btn = ttk.Button(evolution_frame, text="Start Evolution", command=self.start_evolution_search)
        self.evolution_btn.grid(row=1, column=4, padx=10, pady=5)

        self.stop_evolution_btn = ttk.Button(evolution_frame, text="Stop Evolution", command=self.stop_evolution_search, state="disabled")
        self.stop_evolution_btn.grid(row=1, column=5, padx=5, pady=5)

        mutation_types_frame = ttk.Frame(evolution_frame)
        mutation_types_frame.grid(row=2, column=0, columnspan=6, pady=5, sticky="w")
        ttk.Label(mutation_types_frame, text="Mutation Types:").pack(side="left", padx=5)
        
        self.mutation_substitute = tk.BooleanVar(value=True)
        self.mutation_insert = tk.BooleanVar(value=True)
        self.mutation_delete = tk.BooleanVar(value=True)
        self.mutation_swap = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(mutation_types_frame, text="Substitute", variable=self.mutation_substitute).pack(side="left", padx=5)
        ttk.Checkbutton(mutation_types_frame, text="Insert", variable=self.mutation_insert).pack(side="left", padx=5)
        ttk.Checkbutton(mutation_types_frame, text="Delete", variable=self.mutation_delete).pack(side="left", padx=5)
        ttk.Checkbutton(mutation_types_frame, text="Swap", variable=self.mutation_swap).pack(side="left", padx=5)

        self.evolution_progress_var = tk.StringVar(value="Ready for evolution search")
        ttk.Label(evolution_frame, textvariable=self.evolution_progress_var).grid(row=3, column=0, columnspan=6, pady=5, sticky="w")

        self.progress = ttk.Progressbar(parent, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        results_frame = ttk.LabelFrame(parent, text="Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_list = tk.Listbox(results_frame, height=10)
        self.results_list.pack(fill="x", padx=5, pady=5)
        self.results_list.bind('<<ListboxSelect>>', self.display_result)

        nav_bookmark_frame = ttk.Frame(results_frame)
        nav_bookmark_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(nav_bookmark_frame, text="Previous Result", command=self.prev_result, width=16).pack(side="left", padx=2, pady=2)
        ttk.Button(nav_bookmark_frame, text="Next Result", command=self.next_result, width=16).pack(side="left", padx=2, pady=2)
        ttk.Button(nav_bookmark_frame, text="Bookmark Selected Result", command=self.bookmark_current_result, width=24).pack(side="left", padx=10, pady=2)

        self.result_text = tk.Text(results_frame, wrap="none", height=20, font=("Courier", 10))
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(results_frame, text="Analyze Entropy/Noise", command=self.show_entropy_analysis).pack(fill="x", padx=5, pady=2)
        ttk.Button(results_frame, text="Analyze Evolution Results", command=self.show_evolution_analysis).pack(fill="x", padx=5, pady=2)
        ttk.Button(results_frame, text="Find Twin Pages (±N)", command=self.show_twin_page_dialog).pack(fill="x", padx=5, pady=2)

        notes_frame = ttk.Frame(results_frame)
        notes_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(notes_frame, text="Notes/Tags:").pack(side="left")
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(notes_frame, textvariable=self.notes_var, width=60)
        self.notes_entry.pack(side="left", padx=5)
        self.save_note_btn = ttk.Button(notes_frame, text="Save Note", command=self.save_note)
        self.save_note_btn.pack(side="left", padx=5)

        bottom_frame = ttk.Frame(parent)
        bottom_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(bottom_frame, text="Export as CSV", command=self.export_csv).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Export as JSON", command=self.export_json).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="View Background Results", command=self.load_background_results).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Jump to Seed", command=self.jump_to_seed_dialog).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Save Session", command=self.save_session).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Load Session", command=self.load_session).pack(side="left", padx=5)
        ttk.Button(bottom_frame, text="Seed Reverse Lookup", command=self.show_seed_reverse_lookup).pack(side="left", padx=5)
        self.perf_label = ttk.Label(bottom_frame, text="")
        self.perf_label.pack(side="left", padx=10)

    def _create_bg_search_widgets(self, parent):
        phrase_frame = ttk.LabelFrame(parent, text="Background Search Phrases")
        phrase_frame.pack(fill="x", padx=10, pady=5)
        self.bg_phrase_var = tk.StringVar()
        ttk.Entry(phrase_frame, textvariable=self.bg_phrase_var, width=40).pack(side="left", padx=5, pady=5)
        ttk.Button(phrase_frame, text="Add Phrase", command=self.add_bg_phrase).pack(side="left", padx=5)
        ttk.Button(phrase_frame, text="Remove Selected", command=self.remove_bg_phrase).pack(side="left", padx=5)
        self.bg_phrase_list = tk.Listbox(phrase_frame, height=5, selectmode=tk.MULTIPLE)
        self.bg_phrase_list.pack(fill="x", padx=5, pady=5)

        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", padx=10, pady=5)
        self.bg_start_btn = ttk.Button(control_frame, text="Start Background Search", command=self.start_bg_search)
        self.bg_start_btn.pack(side="left", padx=5)
        self.bg_stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_bg_search, state="disabled")
        self.bg_stop_btn.pack(side="left", padx=5)

        log_frame = ttk.LabelFrame(parent, text="Background Search Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.bg_log_text = scrolledtext.ScrolledText(log_frame, height=20, font=("Courier", 10), state="disabled")
        self.bg_log_text.pack(fill="both", expand=True, padx=5, pady=5)

        core_frame = ttk.Frame(parent)
        core_frame.pack(fill="x", padx=10, pady=2)
        ttk.Label(core_frame, text="CPU Cores:").pack(side="left")
        self.bg_cores_var = tk.IntVar(value=self.bg_num_cores)
        ttk.Spinbox(core_frame, from_=1, to=multiprocessing.cpu_count(), textvariable=self.bg_cores_var, width=4).pack(side="left", padx=5)
        self.load_bg_phrases()

    def _create_bookmarks_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.bookmarks_list = tk.Listbox(frame, height=15)
        self.bookmarks_list.pack(fill="x", padx=5, pady=5)
        self.bookmarks_list.bind('<<ListboxSelect>>', self.display_bookmark)
        self.bookmark_text = tk.Text(frame, wrap="none", height=20, font=("Courier", 10))
        self.bookmark_text.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(frame, text="Analyze Entropy/Noise", command=self.show_bookmark_entropy_analysis).pack(fill="x", padx=5, pady=2)
        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill="x", padx=5, pady=5)
        ttk.Button(btn_frame, text="Export Bookmarks as CSV", command=self.export_bookmarks_csv).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Export Bookmarks as JSON", command=self.export_bookmarks_json).pack(side="left", padx=5)
        ttk.Button(btn_frame, text="Remove Selected Bookmark", command=self.remove_selected_bookmark).pack(side="left", padx=5)
        self.load_bookmarks()

    def _create_analytics_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Title and description
        title_frame = ttk.LabelFrame(frame, text="Analytics Dashboard")
        title_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(title_frame, text="Generate visual analytics and detailed reports from your search results").pack(pady=5)
        
        # Button grid for analytics options
        button_frame = ttk.Frame(frame)
        button_frame.pack(fill="x", padx=5, pady=10)
        
        # Row 1
        row1_frame = ttk.Frame(button_frame)
        row1_frame.pack(fill="x", pady=2)
        ttk.Button(row1_frame, text="📊 Seed Distribution", command=self.show_seed_distribution, width=20).pack(side="left", padx=5)
        ttk.Button(row1_frame, text="📈 Phrase Frequency", command=self.show_phrase_frequency, width=20).pack(side="left", padx=5)
        ttk.Button(row1_frame, text="⏰ Timeline Analysis", command=self.show_timeline, width=20).pack(side="left", padx=5)
        
        # Row 2
        row2_frame = ttk.Frame(button_frame)
        row2_frame.pack(fill="x", pady=2)
        ttk.Button(row2_frame, text="🔥 Match Density Heatmap", command=self.show_match_density_heatmap, width=20).pack(side="left", padx=5)
        ttk.Button(row2_frame, text="🌊 Entropy Map", command=self.show_entropy_map, width=20).pack(side="left", padx=5)
        ttk.Button(row2_frame, text="📋 Detailed Report", command=self.show_detailed_analytics_report, width=20).pack(side="left", padx=5)
        
        # Preview area
        preview_frame = ttk.LabelFrame(frame, text="Analytics Preview")
        preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.analytics_preview_text = tk.Text(preview_frame, wrap="word", height=15, font=("Courier", 10), state="disabled")
        preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=self.analytics_preview_text.yview)
        self.analytics_preview_text.configure(yscrollcommand=preview_scrollbar.set)
        self.analytics_preview_text.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        preview_scrollbar.pack(side="right", fill="y")
        
        # Initialize preview
        self.update_analytics_preview()

    def _create_coordinate_browser_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        coord_frame = ttk.LabelFrame(frame, text="Coordinates")
        coord_frame.pack(fill="x", padx=5, pady=5)
        self.cb_vars = {}
        labels = ["Hexagon", "Wall", "Shelf", "Volume", "Page"]
        defaults = [0, 0, 0, 0, 0]
        for i, (label, default) in enumerate(zip(labels, defaults)):
            ttk.Label(coord_frame, text=label+":").grid(row=0, column=2*i, padx=2, pady=2)
            var = tk.IntVar(value=default)
            entry = ttk.Entry(coord_frame, textvariable=var, width=6)
            entry.grid(row=0, column=2*i+1, padx=2, pady=2)
            self.cb_vars[label.lower()] = var
        ttk.Button(coord_frame, text="Jump to Seed", command=self.cb_jump_to_seed).grid(row=0, column=10, padx=10, pady=2)

        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x", padx=5, pady=5)
        for i, label in enumerate(labels):
            subframe = ttk.Frame(nav_frame)
            subframe.pack(side="left", padx=5)
            ttk.Label(subframe, text=label).pack()
            ttk.Button(subframe, text="-", width=2, command=lambda l=label.lower(): self.cb_adjust_coord(l, -1)).pack(side="left")
            ttk.Button(subframe, text="+", width=2, command=lambda l=label.lower(): self.cb_adjust_coord(l, 1)).pack(side="left")

        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        self.cb_seed_label = ttk.Label(info_frame, text="Seed: 0")
        self.cb_seed_label.pack(side="left", padx=5)
        self.cb_coord_label = ttk.Label(info_frame, text="Coordinates: Hexagon 0, Wall 0, Shelf 0, Volume 0, Page 0")
        self.cb_coord_label.pack(side="left", padx=10)

        self.cb_page_text = tk.Text(frame, wrap="none", height=20, font=("Courier", 10))
        self.cb_page_text.pack(fill="both", expand=True, padx=5, pady=5)

        grid_frame = ttk.LabelFrame(frame, text="Explorer Grid (Adjacent Pages)")
        grid_frame.pack(fill="x", padx=5, pady=5)
        self.cb_grid_buttons = []
        for r in range(3):
            row = []
            for c in range(3):
                btn = ttk.Button(grid_frame, text="", width=12, command=lambda dr=r-1, dc=c-1: self.cb_grid_jump(dr, dc))
                btn.grid(row=r, column=c, padx=2, pady=2)
                row.append(btn)
            self.cb_grid_buttons.append(row)
        self.cb_update_display()

    def _create_page_comparison_widgets(self, parent):
        frame = ttk.LabelFrame(parent, text="Page Comparison")
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        input_frame = ttk.Frame(frame)
        input_frame.pack(fill="x", padx=5, pady=5)
        ttk.Label(input_frame, text="Seed 1:").pack(side="left")
        self.compare_seed1_var = tk.IntVar(value=0)
        ttk.Entry(input_frame, textvariable=self.compare_seed1_var, width=10).pack(side="left", padx=5)
        ttk.Label(input_frame, text="Seed 2:").pack(side="left")
        self.compare_seed2_var = tk.IntVar(value=1)
        ttk.Entry(input_frame, textvariable=self.compare_seed2_var, width=10).pack(side="left", padx=5)
        ttk.Button(input_frame, text="Compare Pages", command=self.compare_pages).pack(side="left", padx=5)

        # Create a paned window for side-by-side comparison
        paned_window = ttk.PanedWindow(frame, orient="horizontal")
        paned_window.pack(fill="both", expand=True, padx=5, pady=5)

        # Left panel for first page
        left_frame = ttk.LabelFrame(paned_window, text="Page 1")
        self.compare_text1 = tk.Text(left_frame, wrap="word", height=20, font=("Courier", 10))
        scrollbar1 = ttk.Scrollbar(left_frame, orient="vertical", command=self.compare_text1.yview)
        self.compare_text1.configure(yscrollcommand=scrollbar1.set)
        self.compare_text1.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar1.pack(side="right", fill="y")
        paned_window.add(left_frame, weight=1)

        # Right panel for second page
        right_frame = ttk.LabelFrame(paned_window, text="Page 2")
        self.compare_text2 = tk.Text(right_frame, wrap="word", height=20, font=("Courier", 10))
        scrollbar2 = ttk.Scrollbar(right_frame, orient="vertical", command=self.compare_text2.yview)
        self.compare_text2.configure(yscrollcommand=scrollbar2.set)
        self.compare_text2.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        scrollbar2.pack(side="right", fill="y")
        paned_window.add(right_frame, weight=1)

        # Results frame for comparison statistics
        results_frame = ttk.LabelFrame(frame, text="Comparison Results")
        results_frame.pack(fill="x", padx=5, pady=5)
        self.comparison_results_text = tk.Text(results_frame, wrap="word", height=5, font=("Courier", 10))
        self.comparison_results_text.pack(fill="both", expand=True, padx=5, pady=5)

    def process_search_queue(self):
        try:
            while True:
                message = self.result_queue.get_nowait()
                msg_type = message.get('type')
                
                if msg_type == 'result_found':
                    result = message['data']
                    self.results.append(result)
                    display_text = f"Match {len(self.results)}: Seed={result['seed']}, Index={result['index']}"
                    if 'partial_score' in result:
                        display_text = f"Partial Match {len(self.results)}: Seed={result['seed']}, Index={result['index']}, Score={result['partial_score']}"
                    self.results_list.insert(tk.END, display_text)
                    # Update analytics preview when new results are added
                    if hasattr(self, 'analytics_preview_text'):
                        self.update_analytics_preview()
                
                elif msg_type == 'progress_update':
                    data = message['data']
                    self.perf_label.config(text=data['status'])
                    self.progress['value'] = data['progress']
                
                elif msg_type == 'search_complete':
                    data = message['data']
                    self.perf_label.config(text="Search complete.")
                    self.search_btn.config(state="normal")
                    if data.get('show_message'):
                        messagebox.showinfo(data['title'], data['message'])
                
                elif msg_type == 'bg_log':
                    self.bg_log_text.config(state="normal")
                    self.bg_log_text.insert(tk.END, message['data'] + "\n")
                    self.bg_log_text.see(tk.END)
                    self.bg_log_text.config(state="disabled")
                
                elif msg_type == 'evolution_update':
                    self.evolution_progress_var.set(message['data']['status'])
                    self.progress['value'] = message['data']['progress']
                
                elif msg_type == 'evolution_complete':
                    self.evolution_progress_var.set("Evolution search complete.")
                    self.evolution_btn.config(state="normal")
                    self.stop_evolution_btn.config(state="disabled")
                    messagebox.showinfo("Evolution Complete", message['data']['message'])
        except queue.Empty:
            pass
        self.after(100, self.process_search_queue)

    def start_queue_processing(self):
        self.process_search_queue()

    def cb_get_coords(self):
        return (
            self.cb_vars["hexagon"].get(),
            self.cb_vars["wall"].get(),
            self.cb_vars["shelf"].get(),
            self.cb_vars["volume"].get(),
            self.cb_vars["page"].get(),
        )

    def cb_jump_to_seed(self):
        self.cb_update_display()

    def cb_adjust_coord(self, coord, delta):
        var = self.cb_vars[coord]
        new_val = max(0, var.get() + delta)
        var.set(new_val)
        self.cb_update_display()

    def cb_grid_jump(self, dr, dc):
        coords = list(self.cb_get_coords())
        coords[4] = max(0, coords[4] + dr*1 + dc*1)
        self.cb_vars["page"].set(coords[4])
        self.cb_update_display()

    def cb_update_display(self):
        coords = self.cb_get_coords()
        seed = self.coordinates_to_seed(*coords)
        self.cb_seed_label.config(text=f"Seed: {seed}")
        self.cb_coord_label.config(text=f"Coordinates: {self.format_coordinates({'hexagon': coords[0], 'wall': coords[1], 'shelf': coords[2], 'volume': coords[3], 'page': coords[4]})}")
        page = generate_page(seed, length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200)
        formatted_page = format_page_output(page, width=80)
        self.cb_page_text.delete(1.0, tk.END)
        self.cb_page_text.insert(tk.END, formatted_page)
        center = self.cb_get_coords()
        for r in range(3):
            for c in range(3):
                dpage = (r-1)*1 + (c-1)*1
                coords = list(center)
                coords[4] = max(0, center[4] + dpage)
                seed = self.coordinates_to_seed(*coords)
                self.cb_grid_buttons[r][c].config(text=f"Seed {seed}\nPage {coords[4]}")

    def add_bg_phrase(self):
        phrase = self.bg_phrase_var.get().strip().lower()
        if not phrase:
            return
        try:
            validate_phrase(phrase)
            if phrase not in self.bg_search_phrases:
                self.bg_search_phrases.append(phrase)
                self.bg_phrase_list.insert(tk.END, phrase)
                self.save_bg_phrases()
            self.bg_phrase_var.set("")
        except Exception as e:
            messagebox.showerror("Invalid Phrase", str(e))

    def remove_bg_phrase(self):
        selected = list(self.bg_phrase_list.curselection())[::-1]
        for idx in selected:
            phrase = self.bg_phrase_list.get(idx)
            self.bg_phrase_list.delete(idx)
            if phrase in self.bg_search_phrases:
                self.bg_search_phrases.remove(phrase)
        self.save_bg_phrases()

    def save_bg_phrases(self):
        with open('bg_phrases.json', 'w', encoding='utf-8') as f:
            json.dump(self.bg_search_phrases, f)

    def load_bg_phrases(self):
        if os.path.exists('bg_phrases.json'):
            with open('bg_phrases.json', 'r', encoding='utf-8') as f:
                try:
                    self.bg_search_phrases = json.load(f)
                    for phrase in self.bg_search_phrases:
                        self.bg_phrase_list.insert(tk.END, phrase)
                except Exception:
                    self.bg_search_phrases = []

    def start_bg_search(self):
        if not self.bg_search_phrases:
            messagebox.showwarning("No Phrases", "Add at least one phrase to search for.")
            return
        self.bg_start_btn.config(state="disabled")
        self.bg_stop_btn.config(state="normal")
        self.bg_search_running.set()
        self.bg_log_text.config(state="normal")
        self.bg_log_text.delete(1.0, tk.END)
        self.bg_log_text.config(state="disabled")
        num_cores = self.bg_cores_var.get()
        self.bg_search_thread = threading.Thread(target=self.run_bg_search_mp, args=(num_cores,), daemon=True)
        self.bg_search_thread.start()

    def stop_bg_search(self):
        self.bg_search_running.clear()
        self.bg_start_btn.config(state="normal")
        self.bg_stop_btn.config(state="disabled")

    def run_bg_search_mp(self, num_cores):
        from multiprocessing import Process, Queue
        result_q = Queue()
        running_flag = multiprocessing.Event()
        running_flag.set()
        workers = []
        for i in range(num_cores):
            p = Process(target=bg_search_worker, args=(i, num_cores, self.bg_search_phrases, result_q, running_flag))
            p.daemon = True
            p.start()
            workers.append(p)
        
        results = []
        if os.path.exists(BACKGROUND_RESULTS_FILE):
            with open(BACKGROUND_RESULTS_FILE, 'r', encoding='utf-8') as f:
                try:
                    results = json.load(f)
                except Exception:
                    results = []
        
        seed = 0
        if os.path.exists(BACKGROUND_PROGRESS_FILE):
            with open(BACKGROUND_PROGRESS_FILE, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    seed = data.get('last_seed', 0)
                except Exception:
                    seed = 0
        
        self.append_bg_log(f"[STARTED] Background search with {num_cores} cores")
        
        try:
            while self.bg_search_running.is_set():
                try:
                    result = result_q.get(timeout=0.5)
                    if not is_duplicate(result, results):
                        results.append(result)
                        self.append_bg_log(f"[FOUND] '{result['phrase']}' at seed {result['seed']}, index {result['index']}")
                        with open(BACKGROUND_RESULTS_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, indent=2)
                except queue.Empty:
                    pass
                
                seed += num_cores
                if seed % 100000 == 0:
                    with open(BACKGROUND_PROGRESS_FILE, 'w', encoding='utf-8') as f:
                        json.dump({'last_seed': seed}, f)
        finally:
            running_flag.clear()
            for p in workers:
                p.terminate()
                p.join(timeout=1.0)
            self.append_bg_log("[Background Search Stopped]")

    def append_bg_log(self, msg):
        self.result_queue.put({
            'type': 'bg_log',
            'data': msg
        })

    def bookmark_current_result(self):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        result = self.results[idx]
        if not any(r['seed'] == result['seed'] and r['phrase'] == result['phrase'] for r in self.bookmarks):
            self.bookmarks.append(result.copy())
            self.save_bookmarks()
            self.update_bookmarks_list()
            messagebox.showinfo("Bookmarked", "Result bookmarked.")
        else:
            messagebox.showinfo("Already Bookmarked", "This result is already bookmarked.")

    def update_bookmarks_list(self):
        self.bookmarks_list.delete(0, tk.END)
        for i, r in enumerate(self.bookmarks, 1):
            self.bookmarks_list.insert(tk.END, f"Bookmark {i}: '{r['phrase']}' Seed={r['seed']}, Index={r['index']}")

    def display_bookmark(self, event):
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        idx = sel[0]
        result = self.bookmarks[idx]
        self.bookmark_text.delete(1.0, tk.END)
        page = result.get('page', generate_page(result['seed'], length=PAGE_LENGTH))
        phrase = result['phrase']
        index = result['index']
        formatted_page = format_page_output(page, width=80)
        self.bookmark_text.insert(tk.END, formatted_page)
        self.bookmark_text.tag_remove('highlight', '1.0', tk.END)
        line_length = 80
        line_num = index // line_length + 1
        col_num = index % line_length
        start_idx = f"{line_num}.{col_num}"
        end_idx = f"{line_num}.{col_num + len(phrase)}"
        self.bookmark_text.tag_add('highlight', start_idx, end_idx)
        self.bookmark_text.tag_config('highlight', background='yellow', foreground='black')

    def save_bookmarks(self):
        with open('bookmarks.json', 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, indent=2)

    def load_bookmarks(self):
        if os.path.exists('bookmarks.json'):
            with open('bookmarks.json', 'r', encoding='utf-8') as f:
                try:
                    self.bookmarks = json.load(f)
                    self.update_bookmarks_list()
                except Exception:
                    self.bookmarks = []

    def remove_selected_bookmark(self):
        sel = self.bookmarks_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.bookmarks.pop(idx)
        self.save_bookmarks()
        self.update_bookmarks_list()

    def export_bookmarks_csv(self):
        if not self.bookmarks:
            messagebox.showwarning("No Data", "No bookmarks to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file:
            return
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['phrase', 'seed', 'index', 'timestamp', 'notes', 'hash'])
            writer.writeheader()
            for r in self.bookmarks:
                if 'hash' not in r:
                    page = r.get('page', generate_page(r['seed'], length=PAGE_LENGTH))
                    r['hash'] = self.compute_page_hash(page)
                writer.writerow({k: r.get(k, '') for k in writer.fieldnames})
        messagebox.showinfo("Exported", f"Bookmarks exported to {file}")

    def export_bookmarks_json(self):
        if not self.bookmarks:
            messagebox.showwarning("No Data", "No bookmarks to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file:
            return
        for r in self.bookmarks:
            if 'hash' not in r:
                page = r.get('page', generate_page(r['seed'], length=PAGE_LENGTH))
                r['hash'] = self.compute_page_hash(page)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, indent=2)
        messagebox.showinfo("Exported", f"Bookmarks exported to {file}")

    def start_search(self):
        phrase = self.phrase_var.get().strip().lower()
        try:
            validate_phrase(phrase)
        except Exception as e:
            messagebox.showerror("Invalid Phrase", str(e))
            return
        self.results.clear()
        self.results_list.delete(0, tk.END)
        self.result_text.delete(1.0, tk.END)
        self.progress['value'] = 0
        self.search_btn.config(state="disabled")
        t = threading.Thread(target=self.run_search, args=(phrase,), daemon=True)
        t.start()

    def compute_page_hash(self, page):
        return hashlib.sha256(page.encode('utf-8')).hexdigest()

    def wildcard_match(self, text, pattern):
        pattern = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        regex = re.compile(pattern, re.IGNORECASE)
        return regex.search(text) is not None

    def find_wildcard_matches(self, page, pattern):
        pattern_re = re.escape(pattern).replace(r'\*', '.*').replace(r'\?', '.')
        regex = re.compile(pattern_re, re.IGNORECASE)
        return [(m.start(), m.end()) for m in regex.finditer(page)]

    def longest_common_substring(self, s1, s2):
        m = [[0]*(len(s2)+1) for _ in range(len(s1)+1)]
        longest = 0
        lcs_end = 0
        for i in range(1, len(s1)+1):
            for j in range(1, len(s2)+1):
                if s1[i-1] == s2[j-1]:
                    m[i][j] = m[i-1][j-1] + 1
                    if m[i][j] > longest:
                        longest = m[i][j]
                        lcs_end = j
        return longest, lcs_end - longest

    def run_search(self, phrase):
        try:
            max_matches = self.max_matches_var.get()
            max_attempts = self.max_attempts_var.get()
            page_length = self.page_length_var.get()
            found = []
            is_wildcard = '*' in phrase or '?' in phrase
            start_time = time.time()
            
            for i in range(max_attempts):
                page = generate_page(i, length=page_length)
                page_hash = self.compute_page_hash(page)
                
                if is_wildcard:
                    matches = self.find_wildcard_matches(page, phrase)
                    for idx, end in matches:
                        result = {
                            'seed': i,
                            'index': idx,
                            'page': page,
                            'phrase': phrase,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'notes': '',
                            'hash': page_hash
                        }
                        found.append(result)
                        self.result_queue.put({
                            'type': 'result_found',
                            'data': result
                        })
                        if len(found) >= max_matches:
                            break
                else:
                    idx = page.lower().find(phrase.lower())
                    if idx != -1:
                        result = {
                            'seed': i,
                            'index': idx,
                            'page': page,
                            'phrase': phrase,
                            'timestamp': datetime.datetime.now().isoformat(),
                            'notes': '',
                            'hash': page_hash
                        }
                        found.append(result)
                        self.result_queue.put({
                            'type': 'result_found',
                            'data': result
                        })
                        if len(found) >= max_matches:
                            break
                            
                if len(found) >= max_matches:
                    break
                    
                if i % 1000 == 0 or i == max_attempts - 1:
                    elapsed = time.time() - start_time
                    speed = (i+1) / elapsed if elapsed > 0 else 0
                    self.result_queue.put({
                        'type': 'progress_update',
                        'data': {
                            'status': f"Progress: {i+1}/{max_attempts} | Speed: {speed:.1f} pages/sec | Found: {len(found)}",
                            'progress': (i+1) / max_attempts * 100
                        }
                    })
            
            self.result_queue.put({
                'type': 'search_complete',
                'data': {
                    'show_message': len(found) == 0,
                    'title': 'Search Complete' if found else 'No Matches',
                    'message': f'Found {len(found)} matches.' if found else 'No matches found.'
                }
            })
        except Exception as e:
            self.result_queue.put({
                'type': 'search_complete',
                'data': {
                    'show_message': True,
                    'title': 'Search Error',
                    'message': f'Search failed: {str(e)}'
                }
            })

    def seed_to_coordinates(self, seed):
        pages_per_volume = 100
        volumes_per_shelf = 10
        shelves_per_wall = 4
        walls_per_hex = 6
        page = seed % pages_per_volume
        volume = (seed // pages_per_volume) % volumes_per_shelf
        shelf = (seed // (pages_per_volume * volumes_per_shelf)) % shelves_per_wall
        wall = (seed // (pages_per_volume * volumes_per_shelf * shelves_per_wall)) % walls_per_hex
        hexagon = seed // (pages_per_volume * volumes_per_shelf * shelves_per_wall * walls_per_hex)
        return {
            'hexagon': hexagon,
            'wall': wall,
            'shelf': shelf,
            'volume': volume,
            'page': page
        }

    def coordinates_to_seed(self, hexagon, wall, shelf, volume, page):
        pages_per_volume = 100
        volumes_per_shelf = 10
        shelves_per_wall = 4
        walls_per_hex = 6
        return (((((hexagon * walls_per_hex + wall) * shelves_per_wall + shelf) * volumes_per_shelf) + volume) * pages_per_volume) + page

    def format_coordinates(self, coords):
        return f"Hexagon {coords['hexagon']}, Wall {coords['wall']}, Shelf {coords['shelf']}, Volume {coords['volume']}, Page {coords['page']}"

    def display_result(self, event):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        result = self.results[idx]
        self.result_text.delete(1.0, tk.END)
        page = result.get('page', generate_page(result['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200))
        phrase = result['phrase']
        index = result['index']
        formatted_page = format_page_output(page, width=80)
        self.result_text.insert(tk.END, formatted_page)
        self.result_text.tag_remove('highlight', '1.0', tk.END)
        line_length = 80
        line_num = index // line_length + 1
        col_num = index % line_length
        start_idx = f"{line_num}.{col_num}"
        end_idx = f"{line_num}.{col_num + len(phrase)}"
        self.result_text.tag_add('highlight', start_idx, end_idx)
        self.result_text.tag_config('highlight', background='yellow', foreground='black')
        self.notes_var.set(result.get('notes', ''))
        coords = self.seed_to_coordinates(result['seed'])
        hash_val = result.get('hash', self.compute_page_hash(page))
        result['hash'] = hash_val
        if not hasattr(self, 'coord_label'):
            self.coord_label = ttk.Label(self.result_text.master, text="")
            self.coord_label.pack(anchor="w", padx=5, pady=2)
        self.coord_label.config(text=f"Coordinates: {self.format_coordinates(coords)} (Seed: {result['seed']}) | Hash: {hash_val}")

    def next_result(self):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx + 1 < len(self.results):
            self.results_list.selection_clear(0, tk.END)
            self.results_list.selection_set(idx + 1)
            self.results_list.event_generate('<<ListboxSelect>>')

    def prev_result(self):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        if idx > 0:
            self.results_list.selection_clear(0, tk.END)
            self.results_list.selection_set(idx - 1)
            self.results_list.event_generate('<<ListboxSelect>>')

    def save_note(self):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        self.results[idx]['notes'] = self.notes_var.get()
        messagebox.showinfo("Note Saved", "Notes/Tags saved for this result.")

    def export_csv(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if not file:
            return
        with open(file, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['phrase', 'seed', 'index', 'timestamp', 'notes', 'hash'])
            writer.writeheader()
            for r in self.results:
                if 'hash' not in r:
                    page = r.get('page', generate_page(r['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200))
                    r['hash'] = self.compute_page_hash(page)
                writer.writerow({k: r.get(k, '') for k in writer.fieldnames})
        messagebox.showinfo("Exported", f"Results exported to {file}")

    def export_json(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to export.")
            return
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file:
            return
        for r in self.results:
            if 'hash' not in r:
                page = r.get('page', generate_page(r['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200))
                r['hash'] = self.compute_page_hash(page)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        messagebox.showinfo("Exported", f"Results exported to {file}")

    def load_background_results(self):
        if os.path.exists(BACKGROUND_RESULTS_FILE):
            with open(BACKGROUND_RESULTS_FILE, 'r', encoding='utf-8') as f:
                try:
                    self.results = json.load(f)
                    self.results_list.delete(0, tk.END)
                    for i, r in enumerate(self.results, 1):
                        self.results_list.insert(tk.END, f"Match {i}: Seed={r['seed']}, Index={r['index']}")
                    messagebox.showinfo("Loaded", "Background search results loaded.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to load background results: {str(e)}")
        else:
            messagebox.showwarning("No Data", "No background results found.")

    def save_session(self):
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON Files", "*.json")])
        if not file:
            return
        session_data = {
            'results': self.results,
            'bookmarks': self.bookmarks,
            'bg_phrases': self.bg_search_phrases
        }
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(session_data, f, indent=2)
        messagebox.showinfo("Saved", f"Session saved to {file}")

    def load_session(self):
        file = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if not file:
            return
        with open(file, 'r', encoding='utf-8') as f:
            try:
                session_data = json.load(f)
                self.results = session_data.get('results', [])
                self.bookmarks = session_data.get('bookmarks', [])
                self.bg_search_phrases = session_data.get('bg_phrases', [])
                self.results_list.delete(0, tk.END)
                for i, r in enumerate(self.results, 1):
                    self.results_list.insert(tk.END, f"Match {i}: Seed={r['seed']}, Index={r['index']}")
                self.update_bookmarks_list()
                self.bg_phrase_list.delete(0, tk.END)
                for phrase in self.bg_search_phrases:
                    self.bg_phrase_list.insert(tk.END, phrase)
                messagebox.showinfo("Loaded", f"Session loaded from {file}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load session: {str(e)}")

    def jump_to_seed_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Jump to Seed")
        dialog.geometry("300x100")
        ttk.Label(dialog, text="Enter Seed:").pack(pady=5)
        seed_var = tk.IntVar(value=0)
        ttk.Entry(dialog, textvariable=seed_var).pack(pady=5)
        ttk.Button(dialog, text="Jump", command=lambda: self.jump_to_seed(seed_var.get(), dialog)).pack(pady=5)

    def jump_to_seed(self, seed, dialog):
        coords = self.seed_to_coordinates(seed)
        for key, value in coords.items():
            self.cb_vars[key].set(value)
        self.cb_update_display()
        dialog.destroy()

    def show_seed_reverse_lookup(self):
        dialog = tk.Toplevel(self)
        dialog.title("Seed Reverse Lookup")
        dialog.geometry("400x200")
        ttk.Label(dialog, text="Enter Page Content (or partial):").pack(pady=5)
        content_var = tk.StringVar()
        ttk.Entry(dialog, textvariable=content_var, width=50).pack(pady=5)
        ttk.Button(dialog, text="Search", command=lambda: self.perform_seed_reverse_lookup(content_var.get(), dialog)).pack(pady=5)

    def perform_seed_reverse_lookup(self, content, dialog):
        max_attempts = 10000
        for seed in range(max_attempts):
            page = generate_page(seed, length=PAGE_LENGTH)
            if content.lower() in page.lower():
                self.jump_to_seed(seed, dialog)
                messagebox.showinfo("Found", f"Content found at seed {seed}")
                return
        messagebox.showwarning("Not Found", f"No match found in {max_attempts} attempts.")
        dialog.destroy()

    def show_entropy_analysis(self):
        sel = self.results_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a result to analyze.")
            return
        idx = sel[0]
        result = self.results[idx]
        
        try:
            page = result.get('page', generate_page(result['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200))
            entropy = compute_entropy(page)
            stats = get_page_statistics(page)
            
            # Generate detailed data text
            data_text = f"SEARCH RESULT ENTROPY ANALYSIS\n{'='*50}\n\n"
            data_text += f"Result: '{result['phrase']}'\n"
            data_text += f"Seed: {result['seed']}\n"
            data_text += f"Index: {result['index']}\n"
            data_text += f"Page Length: {len(page)} characters\n\n"
            
            data_text += f"ENTROPY ANALYSIS\n{'-'*30}\n"
            data_text += f"Shannon Entropy: {entropy:.4f} bits\n"
            
            # Add safety check for division by zero
            unique_chars = len(set(page))
            if unique_chars > 1:
                max_entropy = np.log2(unique_chars)
                efficiency = (entropy / max_entropy * 100) if max_entropy > 0 else 0
                data_text += f"Maximum Possible Entropy: {max_entropy:.4f} bits\n"
                data_text += f"Entropy Efficiency: {efficiency:.1f}%\n\n"
            else:
                data_text += f"Maximum Possible Entropy: N/A (only {unique_chars} unique character)\n"
                data_text += f"Entropy Efficiency: N/A\n\n"
            
            data_text += f"CHARACTER STATISTICS\n{'-'*30}\n"
            if isinstance(stats, dict):
                try:
                    # Ensure all values are numeric
                    numeric_stats = {}
                    for char, count in stats.items():
                        if isinstance(count, (int, float)):
                            numeric_stats[char] = int(count)
                        else:
                            print(f"Warning: Non-numeric count for character '{char}': {count}")
                            continue
                    
                    if numeric_stats:
                        total_chars = sum(numeric_stats.values())
                        if total_chars > 0:
                            for char, count in sorted(numeric_stats.items(), key=lambda x: x[1], reverse=True):
                                percentage = (count / total_chars) * 100
                                data_text += f"'{char}': {count} occurrences ({percentage:.1f}%)\n"
                        else:
                            data_text += "No valid character statistics available.\n"
                    else:
                        data_text += "No valid character statistics available.\n"
                except Exception as e:
                    data_text += f"Error processing character statistics: {str(e)}\n"
                    data_text += f"Raw stats: {stats}\n"
            else:
                data_text += f"Character Statistics: {stats}\n"
            
            # Add some additional analysis
            data_text += f"\nADDITIONAL METRICS\n{'-'*30}\n"
            data_text += f"Unique Characters: {unique_chars}\n"
            if len(page) > 0:
                data_text += f"Character Diversity: {(unique_chars / len(page) * 100):.2f}%\n"
            else:
                data_text += f"Character Diversity: N/A (empty page)\n"
            
            # Find most common substrings
            try:
                substrings = {}
                if len(page) >= 3:
                    for i in range(len(page) - 2):
                        substr = page[i:i+3]
                        substrings[substr] = substrings.get(substr, 0) + 1
                
                if substrings:
                    most_common = sorted(substrings.items(), key=lambda x: x[1], reverse=True)[:5]
                    data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\n"
                    for substr, count in most_common:
                        data_text += f"'{substr}': {count} occurrences\n"
                else:
                    data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\nPage too short for 3-character analysis.\n"
            except Exception as e:
                data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\nError: {str(e)}\n"
            
            def create_entropy_chart(fig):
                try:
                    # Create multiple subplots
                    fig.clear()
                    
                    # Character frequency chart
                    ax1 = fig.add_subplot(221)
                    if isinstance(stats, dict) and stats:
                        chars = list(stats.keys())
                        counts = list(stats.values())
                        
                        # Limit to top 20 characters for readability
                        if len(chars) > 20:
                            sorted_items = sorted(zip(chars, counts), key=lambda x: x[1], reverse=True)[:20]
                            chars, counts = zip(*sorted_items)
                        
                        bars = ax1.bar(range(len(chars)), counts, color='lightblue', alpha=0.7)
                        ax1.set_xlabel('Characters')
                        ax1.set_ylabel('Frequency')
                        ax1.set_title('Character Frequency Distribution')
                        ax1.set_xticks(range(len(chars)))
                        ax1.set_xticklabels([repr(c) for c in chars], rotation=45)
                        
                        # Add value labels on bars
                        for bar, count in zip(bars, counts):
                            height = bar.get_height()
                            ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                   f'{count}', ha='center', va='bottom', fontsize=8)
                    
                    # Entropy visualization
                    ax2 = fig.add_subplot(222)
                    max_entropy = np.log2(unique_chars) if unique_chars > 0 else 1
                    entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0
                    
                    ax2.pie([entropy_ratio, 1-entropy_ratio], 
                           labels=['Actual Entropy', 'Unused Entropy'],
                           colors=['lightcoral', 'lightgray'],
                           autopct='%1.1f%%',
                           startangle=90)
                    ax2.set_title('Entropy Efficiency')
                    
                    # Character distribution histogram
                    ax3 = fig.add_subplot(223)
                    if isinstance(stats, dict) and stats:
                        frequencies = list(stats.values())
                        ax3.hist(frequencies, bins=min(20, len(frequencies)), 
                                color='lightgreen', alpha=0.7, edgecolor='black')
                        ax3.set_xlabel('Character Count')
                        ax3.set_ylabel('Number of Characters')
                        ax3.set_title('Character Count Distribution')
                    
                    # Information content visualization
                    ax4 = fig.add_subplot(224)
                    if isinstance(stats, dict) and stats:
                        # Calculate information content for each character
                        total_chars = sum(stats.values())
                        info_content = []
                        char_labels = []
                        
                        for char, count in sorted(stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                            prob = count / total_chars
                            info = -np.log2(prob) if prob > 0 else 0
                            info_content.append(info)
                            char_labels.append(repr(char))
                        
                        ax4.bar(range(len(char_labels)), info_content, color='gold', alpha=0.7)
                        ax4.set_xlabel('Characters')
                        ax4.set_ylabel('Information Content (bits)')
                        ax4.set_title('Information Content by Character')
                        ax4.set_xticks(range(len(char_labels)))
                        ax4.set_xticklabels(char_labels, rotation=45)
                    
                    fig.tight_layout()
                    
                except Exception as e:
                    fig.clear()
                    ax = fig.add_subplot(111)
                    ax.text(0.5, 0.5, f'Error creating entropy charts:\n{str(e)}', 
                           ha='center', va='center', transform=ax.transAxes, 
                           fontsize=12, color='red')
                    ax.set_title('Search Result Entropy Analysis - Error')
            
            self.create_analytics_window("Search Result Entropy Analysis", data_text, create_entropy_chart)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing search result entropy: {str(e)}")

    def show_bookmark_entropy_analysis(self):
        sel = self.bookmarks_list.curselection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a bookmark to analyze.")
            return
        idx = sel[0]
        result = self.bookmarks[idx]
        
        try:
            page = result.get('page', generate_page(result['seed'], length=PAGE_LENGTH))
            entropy = compute_entropy(page)
            stats = get_page_statistics(page)
            
            # Generate detailed data text
            data_text = f"BOOKMARK ENTROPY ANALYSIS\n{'='*50}\n\n"
            data_text += f"Bookmark: '{result['phrase']}'\n"
            data_text += f"Seed: {result['seed']}\n"
            data_text += f"Index: {result['index']}\n"
            data_text += f"Page Length: {len(page)} characters\n\n"
            
            data_text += f"ENTROPY ANALYSIS\n{'-'*30}\n"
            data_text += f"Shannon Entropy: {entropy:.4f} bits\n"
            
            # Add safety check for division by zero
            unique_chars = len(set(page))
            if unique_chars > 1:
                max_entropy = np.log2(unique_chars)
                efficiency = (entropy / max_entropy * 100) if max_entropy > 0 else 0
                data_text += f"Maximum Possible Entropy: {max_entropy:.4f} bits\n"
                data_text += f"Entropy Efficiency: {efficiency:.1f}%\n\n"
            else:
                data_text += f"Maximum Possible Entropy: N/A (only {unique_chars} unique character)\n"
                data_text += f"Entropy Efficiency: N/A\n\n"
            
            data_text += f"CHARACTER STATISTICS\n{'-'*30}\n"
            if isinstance(stats, dict):
                try:
                    # Ensure all values are numeric
                    numeric_stats = {}
                    for char, count in stats.items():
                        if isinstance(count, (int, float)):
                            numeric_stats[char] = int(count)
                        else:
                            print(f"Warning: Non-numeric count for character '{char}': {count}")
                            continue
                    
                    if numeric_stats:
                        total_chars = sum(numeric_stats.values())
                        if total_chars > 0:
                            for char, count in sorted(numeric_stats.items(), key=lambda x: x[1], reverse=True):
                                percentage = (count / total_chars) * 100
                                data_text += f"'{char}': {count} occurrences ({percentage:.1f}%)\n"
                        else:
                            data_text += "No valid character statistics available.\n"
                    else:
                        data_text += "No valid character statistics available.\n"
                except Exception as e:
                    data_text += f"Error processing character statistics: {str(e)}\n"
                    data_text += f"Raw stats: {stats}\n"
            else:
                data_text += f"Character Statistics: {stats}\n"
            
            # Add some additional analysis
            data_text += f"\nADDITIONAL METRICS\n{'-'*30}\n"
            data_text += f"Unique Characters: {unique_chars}\n"
            if len(page) > 0:
                data_text += f"Character Diversity: {(unique_chars / len(page) * 100):.2f}%\n"
            else:
                data_text += f"Character Diversity: N/A (empty page)\n"
            
            # Find most common substrings
            try:
                substrings = {}
                if len(page) >= 3:
                    for i in range(len(page) - 2):
                        substr = page[i:i+3]
                        substrings[substr] = substrings.get(substr, 0) + 1
                
                if substrings:
                    most_common = sorted(substrings.items(), key=lambda x: x[1], reverse=True)[:5]
                    data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\n"
                    for substr, count in most_common:
                        data_text += f"'{substr}': {count} occurrences\n"
                else:
                    data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\nPage too short for 3-character analysis.\n"
            except Exception as e:
                data_text += f"\nMOST COMMON 3-CHAR SEQUENCES\n{'-'*30}\nError: {str(e)}\n"
            
            def create_entropy_chart(fig):
                try:
                    # Create multiple subplots
                    fig.clear()
                    
                    # Character frequency chart
                    ax1 = fig.add_subplot(221)
                    if isinstance(stats, dict) and stats:
                        # Filter to only numeric values
                        numeric_stats = {k: v for k, v in stats.items() if isinstance(v, (int, float))}
                        
                        if numeric_stats:
                            chars = list(numeric_stats.keys())
                            counts = [int(v) for v in numeric_stats.values()]
                            
                            # Limit to top 20 characters for readability
                            if len(chars) > 20:
                                sorted_items = sorted(zip(chars, counts), key=lambda x: x[1], reverse=True)[:20]
                                chars, counts = zip(*sorted_items)
                            
                            bars = ax1.bar(range(len(chars)), counts, color='lightblue', alpha=0.7)
                            ax1.set_xlabel('Characters')
                            ax1.set_ylabel('Frequency')
                            ax1.set_title('Character Frequency Distribution')
                            ax1.set_xticks(range(len(chars)))
                            ax1.set_xticklabels([repr(c) for c in chars], rotation=45)
                            
                            # Add value labels on bars
                            for bar, count in zip(bars, counts):
                                height = bar.get_height()
                                ax1.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                       f'{count}', ha='center', va='bottom', fontsize=8)
                        else:
                            ax1.text(0.5, 0.5, 'No valid character data', ha='center', va='center', 
                                   transform=ax1.transAxes, fontsize=12)
                            ax1.set_title('Character Frequency - No Data')
                    
                    # Entropy visualization
                    ax2 = fig.add_subplot(222)
                    if unique_chars > 1:
                        max_entropy = np.log2(unique_chars)
                        entropy_ratio = entropy / max_entropy if max_entropy > 0 else 0
                        
                        ax2.pie([entropy_ratio, 1-entropy_ratio], 
                               labels=['Actual Entropy', 'Unused Entropy'],
                               colors=['lightcoral', 'lightgray'],
                               autopct='%1.1f%%',
                               startangle=90)
                        ax2.set_title('Entropy Efficiency')
                    else:
                        ax2.text(0.5, 0.5, 'Insufficient unique characters\nfor entropy analysis', 
                               ha='center', va='center', transform=ax2.transAxes, fontsize=10)
                        ax2.set_title('Entropy Efficiency - N/A')
                    
                    # Character distribution histogram
                    ax3 = fig.add_subplot(223)
                    if isinstance(stats, dict) and stats:
                        numeric_stats = {k: v for k, v in stats.items() if isinstance(v, (int, float))}
                        if numeric_stats:
                            frequencies = [int(v) for v in numeric_stats.values()]
                            ax3.hist(frequencies, bins=min(20, len(frequencies)), 
                                    color='lightgreen', alpha=0.7, edgecolor='black')
                            ax3.set_xlabel('Character Count')
                            ax3.set_ylabel('Number of Characters')
                            ax3.set_title('Character Count Distribution')
                        else:
                            ax3.text(0.5, 0.5, 'No valid frequency data', ha='center', va='center', 
                                   transform=ax3.transAxes, fontsize=12)
                            ax3.set_title('Character Count Distribution - No Data')
                    
                    # Information content visualization
                    ax4 = fig.add_subplot(224)
                    if isinstance(stats, dict) and stats:
                        numeric_stats = {k: v for k, v in stats.items() if isinstance(v, (int, float))}
                        if numeric_stats:
                            # Calculate information content for each character
                            total_chars = sum(numeric_stats.values())
                            info_content = []
                            char_labels = []
                            
                            for char, count in sorted(numeric_stats.items(), key=lambda x: x[1], reverse=True)[:10]:
                                if total_chars > 0:
                                    prob = count / total_chars
                                    info = -np.log2(prob) if prob > 0 else 0
                                    info_content.append(info)
                                    char_labels.append(repr(char))
                            
                            if info_content:
                                ax4.bar(range(len(char_labels)), info_content, color='gold', alpha=0.7)
                                ax4.set_xlabel('Characters')
                                ax4.set_ylabel('Information Content (bits)')
                                ax4.set_title('Information Content by Character')
                                ax4.set_xticks(range(len(char_labels)))
                                ax4.set_xticklabels(char_labels, rotation=45)
                            else:
                                ax4.text(0.5, 0.5, 'No information content data', ha='center', va='center', 
                                       transform=ax4.transAxes, fontsize=12)
                                ax4.set_title('Information Content - No Data')
                        else:
                            ax4.text(0.5, 0.5, 'No valid character data', ha='center', va='center', 
                                   transform=ax4.transAxes, fontsize=12)
                            ax4.set_title('Information Content - No Data')
                    
                    fig.tight_layout()
                    
                except Exception as e:
                    fig.clear()
                    ax = fig.add_subplot(111)
                    ax.text(0.5, 0.5, f'Error creating entropy charts:\n{str(e)}', 
                           ha='center', va='center', transform=ax.transAxes, 
                           fontsize=12, color='red')
                    ax.set_title('Bookmark Entropy Analysis - Error')
            
            self.create_analytics_window("Bookmark Entropy Analysis", data_text, create_entropy_chart)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error analyzing bookmark entropy: {str(e)}\n\nDetailed error: {type(e).__name__}")

    def start_evolution_search(self):
        phrase = self.evolution_phrase_var.get().strip().lower()
        try:
            validate_phrase(phrase)
        except Exception as e:
            messagebox.showerror("Invalid Phrase", str(e))
            return
        self.evolution_results.clear()
        self.evolution_running = True
        self.evolution_btn.config(state="disabled")
        self.stop_evolution_btn.config(state="normal")
        self.evolution_thread = threading.Thread(target=self.run_evolution_search, args=(phrase,), daemon=True)
        self.evolution_thread.start()

    def stop_evolution_search(self):
        self.evolution_running = False
        self.evolution_btn.config(state="normal")
        self.stop_evolution_btn.config(state="disabled")

    def run_evolution_search(self, base_phrase):
        try:
            generations = self.generations_var.get()
            population_size = self.population_size_var.get()
            mutation_rate = self.mutation_rate_var.get()
            mutation_types = {
                'substitute': self.mutation_substitute.get(),
                'insert': self.mutation_insert.get(),
                'delete': self.mutation_delete.get(),
                'swap': self.mutation_swap.get()
            }
            population = [base_phrase] * population_size
            for gen in range(generations):
                if not self.evolution_running:
                    break
                new_population = []
                for phrase in population:
                    mutations = generate_phrase_mutations(phrase, mutation_rate, mutation_types)
                    new_population.extend(mutations[:population_size // len(population)])
                population = new_population[:population_size]
                self.evolution_results.append(population)
                self.result_queue.put({
                    'type': 'evolution_update',
                    'data': {
                        'status': f"Generation {gen+1}/{generations}: {len(population)} phrases",
                        'progress': (gen+1) / generations * 100
                    }
                })
            self.result_queue.put({
                'type': 'evolution_complete',
                'data': {'message': f"Evolution completed with {len(self.evolution_results)} generations."}
            })
        except Exception as e:
            self.result_queue.put({
                'type': 'evolution_complete',
                'data': {'message': f"Evolution failed: {str(e)}"}
            })

    def show_evolution_analysis(self):
        if not self.evolution_results:
            messagebox.showwarning("No Data", "No evolution results to analyze.")
            return
        analysis = []
        for gen, population in enumerate(self.evolution_results, 1):
            unique_phrases = len(set(population))
            analysis.append(f"Generation {gen}: {unique_phrases} unique phrases")
        messagebox.showinfo("Evolution Analysis", "\n".join(analysis))

    def show_twin_page_dialog(self):
        dialog = tk.Toplevel(self)
        dialog.title("Find Twin Pages")
        dialog.geometry("300x150")
        ttk.Label(dialog, text="Enter Seed:").pack(pady=5)
        seed_var = tk.IntVar(value=0)
        ttk.Entry(dialog, textvariable=seed_var).pack(pady=5)
        ttk.Label(dialog, text="Offset (±N):").pack(pady=5)
        offset_var = tk.IntVar(value=1)
        ttk.Entry(dialog, textvariable=offset_var).pack(pady=5)
        ttk.Button(dialog, text="Find Twins", command=lambda: self.find_twin_pages(seed_var.get(), offset_var.get(), dialog)).pack(pady=5)

    def find_twin_pages(self, seed, offset, dialog):
        twin_results = find_echo_pages(seed, offset, length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200)
        self.results.extend(twin_results)
        self.results_list.delete(0, tk.END)
        for i, r in enumerate(self.results, 1):
            self.results_list.insert(tk.END, f"Match {i}: Seed={r['seed']}, Index={r['index']}")
        dialog.destroy()
        messagebox.showinfo("Twin Pages", f"Found {len(twin_results)} twin pages.")

    def compare_pages(self):
        seed1 = self.compare_seed1_var.get()
        seed2 = self.compare_seed2_var.get()
        page1 = generate_page(seed1, length=PAGE_LENGTH)
        page2 = generate_page(seed2, length=PAGE_LENGTH)
        
        # Clear previous content
        self.compare_text1.delete(1.0, tk.END)
        self.compare_text2.delete(1.0, tk.END)
        self.comparison_results_text.delete(1.0, tk.END)
        
        # Format pages for display with word wrapping
        formatted_page1 = format_page_output(page1, width=80)
        formatted_page2 = format_page_output(page2, width=80)
        
        # Display the pages
        self.compare_text1.insert(tk.END, formatted_page1)
        self.compare_text2.insert(tk.END, formatted_page2)
        
        # Calculate and display comparison statistics
        similarity = similarity_percentage(page1, page2)
        differences = highlight_differences(page1, page2)
        common_substrings = find_common_substrings(page1, page2)
        
        # Display comparison results
        comparison_info = f"Similarity: {similarity:.2f}%\n"
        comparison_info += f"Page 1 Length: {len(page1)} characters\n"
        comparison_info += f"Page 2 Length: {len(page2)} characters\n"
        comparison_info += f"Common substrings found: {len(common_substrings)}\n"
        comparison_info += f"Character differences: {abs(len(page1) - len(page2))}\n"
        
        self.comparison_results_text.insert(tk.END, comparison_info)
        
        # Highlight differences in both text widgets
        self._highlight_page_differences(page1, page2)

    def _highlight_page_differences(self, page1, page2):
        """Highlight character differences between two pages in the comparison text widgets."""
        # Configure tags for highlighting differences
        self.compare_text1.tag_configure('diff', background='lightcoral', foreground='black')
        self.compare_text2.tag_configure('diff', background='lightcoral', foreground='black')
        self.compare_text1.tag_configure('same', background='lightgreen', foreground='black')
        self.compare_text2.tag_configure('same', background='lightgreen', foreground='black')
        
        # Clear existing tags
        self.compare_text1.tag_remove('diff', '1.0', tk.END)
        self.compare_text1.tag_remove('same', '1.0', tk.END)
        self.compare_text2.tag_remove('diff', '1.0', tk.END)
        self.compare_text2.tag_remove('same', '1.0', tk.END)
        
        # Compare character by character and highlight differences
        min_length = min(len(page1), len(page2))
        line_length = 80  # Same as format_page_output width
        
        for i in range(min_length):
            if page1[i] != page2[i]:
                # Calculate line and column position
                line_num = i // line_length + 1
                col_num = i % line_length
                start_idx = f"{line_num}.{col_num}"
                end_idx = f"{line_num}.{col_num + 1}"
                
                # Highlight differences
                self.compare_text1.tag_add('diff', start_idx, end_idx)
                self.compare_text2.tag_add('diff', start_idx, end_idx)
        
        # Highlight any extra characters if pages have different lengths
        if len(page1) != len(page2):
            longer_page = page1 if len(page1) > len(page2) else page2
            text_widget = self.compare_text1 if len(page1) > len(page2) else self.compare_text2
            
            for i in range(min_length, len(longer_page)):
                line_num = i // line_length + 1
                col_num = i % line_length
                start_idx = f"{line_num}.{col_num}"
                end_idx = f"{line_num}.{col_num + 1}"
                text_widget.tag_add('diff', start_idx, end_idx)

    def show_seed_distribution(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        seeds = [r['seed'] for r in self.results]
        
        # Generate detailed data text
        seed_counts = {}
        for seed in seeds:
            seed_counts[seed] = seed_counts.get(seed, 0) + 1
        
        data_text = f"SEED DISTRIBUTION ANALYSIS\n{'='*50}\n\n"
        data_text += f"Total Results: {len(seeds)}\n"
        data_text += f"Unique Seeds: {len(seed_counts)}\n"
        data_text += f"Seed Range: {min(seeds)} - {max(seeds)}\n"
        data_text += f"Average Seed: {sum(seeds)/len(seeds):.1f}\n\n"
        
        data_text += "Most Frequent Seeds:\n"
        sorted_seeds = sorted(seed_counts.items(), key=lambda x: x[1], reverse=True)
        for i, (seed, count) in enumerate(sorted_seeds[:10]):
            data_text += f"{i+1:2d}. Seed {seed}: {count} occurrences\n"
        
        def create_seed_chart(fig):
            ax = fig.add_subplot(111)
            
            # Create histogram
            ax.hist(seeds, bins=min(50, len(set(seeds))), alpha=0.7, color='skyblue', edgecolor='black')
            ax.set_xlabel('Seed Values')
            ax.set_ylabel('Frequency')
            ax.set_title('Distribution of Seeds in Search Results')
            ax.grid(True, alpha=0.3)
            fig.tight_layout()
        
        self.create_analytics_window("Seed Distribution", data_text, create_seed_chart)

    def show_phrase_frequency(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        phrases = {}
        for r in self.results:
            phrases[r['phrase']] = phrases.get(r['phrase'], 0) + 1
        
        # Generate detailed data text
        data_text = f"PHRASE FREQUENCY ANALYSIS\n{'='*50}\n\n"
        data_text += f"Total Results: {len(self.results)}\n"
        data_text += f"Unique Phrases: {len(phrases)}\n\n"
        
        data_text += "Phrase Frequency Breakdown:\n"
        sorted_phrases = sorted(phrases.items(), key=lambda x: x[1], reverse=True)
        for i, (phrase, count) in enumerate(sorted_phrases):
            percentage = (count / len(self.results)) * 100
            data_text += f"{i+1:2d}. '{phrase}': {count} occurrences ({percentage:.1f}%)\n"
        
        def create_phrase_chart(fig):
            ax = fig.add_subplot(111)
            
            # Get top 15 phrases for readability
            top_phrases = sorted_phrases[:15]
            phrases_list = [p[0][:20] + ('...' if len(p[0]) > 20 else '') for p in top_phrases]
            counts = [p[1] for p in top_phrases]
            
            bars = ax.bar(range(len(phrases_list)), counts, color='lightcoral', alpha=0.7)
            ax.set_xlabel('Phrases')
            ax.set_ylabel('Frequency')
            ax.set_title('Phrase Frequency Distribution')
            ax.set_xticks(range(len(phrases_list)))
            ax.set_xticklabels(phrases_list, rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                       f'{count}', ha='center', va='bottom')
            
            fig.tight_layout()
        
        self.create_analytics_window("Phrase Frequency", data_text, create_phrase_chart)

    def show_timeline(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        timestamps = []
        for r in self.results:
            try:
                ts = datetime.datetime.fromisoformat(r['timestamp'])
                timestamps.append(ts)
            except:
                continue
        
        if not timestamps:
            messagebox.showwarning("No Data", "No valid timestamps found in results.")
            return
        
        # Generate detailed data text
        data_text = f"TIMELINE ANALYSIS\n{'='*50}\n\n"
        data_text += f"Total Results with Timestamps: {len(timestamps)}\n"
        data_text += f"Time Range: {min(timestamps)} to {max(timestamps)}\n"
        data_text += f"Duration: {max(timestamps) - min(timestamps)}\n\n"
        
        # Group by hour
        hourly_counts = {}
        for ts in timestamps:
            hour_key = ts.replace(minute=0, second=0, microsecond=0)
            hourly_counts[hour_key] = hourly_counts.get(hour_key, 0) + 1
        
        data_text += "Results by Hour:\n"
        sorted_hours = sorted(hourly_counts.items())
        for hour, count in sorted_hours:
            data_text += f"{hour.strftime('%Y-%m-%d %H:%M')}: {count} results\n"
        
        def create_timeline_chart(fig):
            ax = fig.add_subplot(111)
            
            if hourly_counts:
                hours = list(sorted(hourly_counts.keys()))
                counts = [hourly_counts[h] for h in hours]
                
                ax.plot(hours, counts, marker='o', linewidth=2, markersize=6, color='green', alpha=0.7)
                ax.fill_between(hours, counts, alpha=0.3, color='green')
                ax.set_xlabel('Time')
                ax.set_ylabel('Number of Results')
                ax.set_title('Search Results Timeline')
                ax.grid(True, alpha=0.3)
                
                # Format x-axis
                if len(hours) > 10:
                    ax.tick_params(axis='x', rotation=45)
            
            fig.tight_layout()
        
        self.create_analytics_window("Timeline Analysis", data_text, create_timeline_chart)

    def show_match_density_heatmap(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        indices = [r['index'] for r in self.results]
        
        # Generate detailed data text
        data_text = f"MATCH DENSITY ANALYSIS\n{'='*50}\n\n"
        data_text += f"Total Matches: {len(indices)}\n"
        data_text += f"Index Range: {min(indices)} - {max(indices)}\n"
        data_text += f"Average Position: {sum(indices)/len(indices):.1f}\n\n"
        
        # Create position bins
        max_index = max(indices)
        bin_size = max(1, max_index // 20)  # 20 bins
        bins = {}
        for idx in indices:
            bin_key = (idx // bin_size) * bin_size
            bins[bin_key] = bins.get(bin_key, 0) + 1
        
        data_text += "Position Distribution (by ranges):\n"
        for bin_start in sorted(bins.keys()):
            bin_end = bin_start + bin_size - 1
            count = bins[bin_start]
            data_text += f"Positions {bin_start}-{bin_end}: {count} matches\n"
        
        def create_heatmap_chart(fig):
            ax = fig.add_subplot(111)
            
            if len(indices) == 0:
                ax.text(0.5, 0.5, 'No data to display', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=12)
                ax.set_title('Match Density Heatmap - No Data')
                return
            
            try:
                # Create histogram that looks like a heatmap
                n_bins = min(50, max(10, len(set(indices))))  # Ensure at least 10 bins
                n, bins_edges, patches = ax.hist(indices, bins=n_bins, 
                                               alpha=0.8, edgecolor='black')
                
                # Color gradient using matplotlib colormap
                import matplotlib.cm as cm
                import numpy as np
                
                if n.max() > 0:  # Check if we have any data
                    # Normalize colors
                    fracs = n / n.max()
                    norm = plt.Normalize(fracs.min(), fracs.max())
                    
                    for frac, patch in zip(fracs, patches):
                        color = cm.hot(norm(frac))
                        patch.set_facecolor(color)
                else:
                    # If no data, show message
                    ax.text(0.5, 0.5, 'Insufficient data for heatmap', ha='center', va='center', 
                           transform=ax.transAxes, fontsize=12)
                
                ax.set_xlabel('Position in Page')
                ax.set_ylabel('Match Count')
                ax.set_title('Match Density Heatmap')
                ax.grid(True, alpha=0.3)
                
                # Add statistics annotation
                if len(indices) > 0:
                    stats_text = f'Total: {len(indices)}\nRange: {min(indices)}-{max(indices)}\nAvg: {sum(indices)/len(indices):.1f}'
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                
                fig.tight_layout()
                
            except Exception as e:
                ax.text(0.5, 0.5, f'Error creating heatmap:\n{str(e)}', ha='center', va='center', 
                       transform=ax.transAxes, fontsize=10, color='red')
                ax.set_title('Match Density Heatmap - Error')
        
        self.create_analytics_window("Match Density Heatmap", data_text, create_heatmap_chart)

    def show_entropy_map(self):
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        try:
            entropies = []
            seeds = []
            for r in self.results:
                try:
                    page = r.get('page', generate_page(r['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200))
                    entropy = compute_entropy(page)
                    entropies.append(entropy)
                    seeds.append(r['seed'])
                except Exception as e:
                    print(f"Error processing result {r.get('seed', 'unknown')}: {e}")
                    continue
            
            if not entropies:
                messagebox.showerror("Error", "No valid entropy data could be calculated.")
                return
                
            # Generate detailed data text
            avg_entropy = sum(entropies) / len(entropies)
            min_entropy = min(entropies)
            max_entropy = max(entropies)
            
            data_text = f"ENTROPY ANALYSIS\n{'='*50}\n\n"
            data_text += f"Total Pages Analyzed: {len(entropies)}\n"
            data_text += f"Average Entropy: {avg_entropy:.4f} bits\n"
            data_text += f"Entropy Range: {min_entropy:.4f} - {max_entropy:.4f} bits\n"
            
            if len(entropies) > 1:
                std_dev = (sum((e - avg_entropy)**2 for e in entropies) / len(entropies))**0.5
                data_text += f"Standard Deviation: {std_dev:.4f}\n\n"
            else:
                data_text += "Standard Deviation: N/A (single data point)\n\n"
            
            # Entropy bins
            entropy_bins = {}
            for entropy in entropies:
                bin_key = round(entropy, 1)
                entropy_bins[bin_key] = entropy_bins.get(bin_key, 0) + 1
            
            data_text += "Entropy Distribution:\n"
            for entropy_val in sorted(entropy_bins.keys()):
                count = entropy_bins[entropy_val]
                data_text += f"{entropy_val:.1f} bits: {count} pages\n"
            
            def create_entropy_chart(fig):
                ax = fig.add_subplot(111)
                
                try:
                    if len(entropies) == 0:
                        ax.text(0.5, 0.5, 'No entropy data available', ha='center', va='center', 
                               transform=ax.transAxes, fontsize=12)
                        ax.set_title('Entropy Map - No Data')
                        return
                    
                    # Scatter plot of entropy vs seed
                    scatter = ax.scatter(seeds, entropies, alpha=0.6, c=entropies, 
                                       cmap='viridis', s=50)
                    ax.set_xlabel('Seed Value')
                    ax.set_ylabel('Entropy (bits)')
                    ax.set_title('Entropy Map: Page Information Content')
                    ax.grid(True, alpha=0.3)
                    
                    # Add colorbar
                    try:
                        cbar = fig.colorbar(scatter, ax=ax)
                        cbar.set_label('Entropy (bits)')
                    except Exception as e:
                        print(f"Could not create colorbar: {e}")
                    
                    # Add statistics annotation
                    stats_text = f'Count: {len(entropies)}\nAvg: {avg_entropy:.3f}\nRange: {min_entropy:.3f}-{max_entropy:.3f}'
                    ax.text(0.02, 0.98, stats_text, transform=ax.transAxes, 
                           verticalalignment='top', bbox=dict(boxstyle='round', facecolor='white', alpha=0.8))
                    
                    fig.tight_layout()
                    
                except Exception as e:
                    ax.text(0.5, 0.5, f'Error creating entropy chart:\n{str(e)}', ha='center', va='center', 
                           transform=ax.transAxes, fontsize=10, color='red')
                    ax.set_title('Entropy Map - Error')
            
            self.create_analytics_window("Entropy Map", data_text, create_entropy_chart)
            
        except Exception as e:
            messagebox.showerror("Error", f"Error generating entropy map: {str(e)}")

    def show_detailed_analytics_report(self):
        """Generate a comprehensive analytics report."""
        if not self.results:
            messagebox.showwarning("No Data", "No results to display.")
            return
        
        # Generate comprehensive report
        data_text = f"COMPREHENSIVE ANALYTICS REPORT\n{'='*60}\n"
        data_text += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        # Basic statistics
        total_results = len(self.results)
        unique_seeds = len(set(r['seed'] for r in self.results))
        unique_phrases = len(set(r['phrase'] for r in self.results))
        
        data_text += f"DATASET OVERVIEW\n{'-'*30}\n"
        data_text += f"Total Results: {total_results}\n"
        data_text += f"Unique Seeds: {unique_seeds}\n"
        data_text += f"Unique Phrases: {unique_phrases}\n"
        data_text += f"Duplicate Rate: {((total_results - unique_seeds) / total_results * 100):.1f}%\n\n"
        
        # Add more detailed statistics here...
        data_text += "This comprehensive report includes all available analytics data.\n"
        data_text += "Use the individual analytics buttons for detailed visualizations.\n"
        
        self.create_analytics_window("Detailed Analytics Report", data_text)

    def update_mutation_label(self, value):
        self.mutation_label.config(text=f"{float(value):.2f}")

    def update_analytics_preview(self):
        """Update the analytics preview with current data summary."""
        self.analytics_preview_text.config(state="normal")
        self.analytics_preview_text.delete(1.0, tk.END)
        
        if not self.results:
            self.analytics_preview_text.insert(tk.END, "No search results available for analytics.\n\nRun a search to generate analytics data.")
        else:
            # Generate summary statistics
            total_results = len(self.results)
            unique_seeds = len(set(r['seed'] for r in self.results))
            unique_phrases = len(set(r['phrase'] for r in self.results))
            
            if self.results:
                seed_range = f"{min(r['seed'] for r in self.results)} - {max(r['seed'] for r in self.results)}"
                avg_index = sum(r['index'] for r in self.results) / len(self.results)
            else:
                seed_range = "N/A"
                avg_index = 0
            
            preview_text = f"""ANALYTICS SUMMARY
{'='*50}

Dataset Overview:
• Total Results: {total_results}
• Unique Seeds: {unique_seeds}
• Unique Phrases: {unique_phrases}
• Seed Range: {seed_range}
• Average Match Index: {avg_index:.1f}

Available Analytics:
📊 Seed Distribution - Histogram of seed frequencies
📈 Phrase Frequency - Bar chart of phrase occurrences
⏰ Timeline Analysis - Time-based search patterns
🔥 Match Density Heatmap - Position distribution within pages
🌊 Entropy Map - Information content analysis
📋 Detailed Report - Comprehensive data analysis

Click any button above to open a detailed analytics window.
"""
            self.analytics_preview_text.insert(tk.END, preview_text)
        
        self.analytics_preview_text.config(state="disabled")

    def create_analytics_window(self, title, data_text, chart_function=None):
        """Create a dedicated analytics window with charts and data."""
        window = tk.Toplevel(self)
        window.title(f"Analytics: {title}")
        window.geometry("900x700")
        window.resizable(True, True)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(window)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Chart tab
        if chart_function:
            chart_frame = ttk.Frame(notebook)
            notebook.add(chart_frame, text="📊 Chart")
            
            try:
                # Create matplotlib figure
                fig = plt.Figure(figsize=(10, 6), dpi=100)
                canvas = FigureCanvasTkAgg(fig, chart_frame)
                canvas.get_tk_widget().pack(fill="both", expand=True, padx=5, pady=5)
                
                # Generate chart using provided function
                chart_function(fig)
                canvas.draw()
                
            except ImportError:
                # Fallback if matplotlib not available
                ttk.Label(chart_frame, text="Matplotlib not available. Install it for visual charts:\npip install matplotlib").pack(expand=True)
        
        # Data tab
        data_frame = ttk.Frame(notebook)
        notebook.add(data_frame, text="📋 Data")
        
        data_text_widget = tk.Text(data_frame, wrap="word", font=("Courier", 10))
        data_scrollbar = ttk.Scrollbar(data_frame, orient="vertical", command=data_text_widget.yview)
        data_text_widget.configure(yscrollcommand=data_scrollbar.set)
        data_text_widget.pack(side="left", fill="both", expand=True, padx=5, pady=5)
        data_scrollbar.pack(side="right", fill="y")
        
        data_text_widget.insert(tk.END, data_text)
        data_text_widget.config(state="disabled")
        
        # Export button
        export_frame = ttk.Frame(window)
        export_frame.pack(fill="x", padx=10, pady=5)
        ttk.Button(export_frame, text="Export Data", command=lambda: self.export_analytics_data(title, data_text)).pack(side="right", padx=5)
        
        return window

    def export_analytics_data(self, title, data):
        """Export analytics data to a file."""
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title=f"Export {title} Data"
        )
        if file_path:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(f"Analytics Report: {title}\n")
                f.write(f"Generated: {datetime.datetime.now().isoformat()}\n")
                f.write("="*60 + "\n\n")
                f.write(data)
            messagebox.showinfo("Export Complete", f"Analytics data exported to {file_path}")

if __name__ == "__main__":
    app = BabelGUI()
    app.mainloop()

