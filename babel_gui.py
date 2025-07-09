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
import multiprocessing
from babel import generate_page, search_for_phrase, format_page_output, validate_phrase, ALPHABET
from babel_core import compute_entropy, get_page_statistics, similarity_percentage, compare_pages, highlight_differences, find_common_substrings
from babel_tools import generate_phrase_mutations, search_with_wildcards, LibraryCoordinates, find_echo_pages, search_for_similar_pages
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
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
        
        # Evolution mode variables
        self.evolution_results = []
        self.evolution_running = False
        self.evolution_thread = None
        self.current_generation = 0
        
        # Page comparison variables
        self.comparison_page1 = None
        self.comparison_page2 = None
        self.comparison_seed1 = None
        self.comparison_seed2 = None
        self.comparison_results = None
        
        self.create_widgets()

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

        # --- Manual Search Tab ---
        self._create_manual_search_widgets(self.search_tab)
        # --- Background Search Tab ---
        self._create_bg_search_widgets(self.bg_tab)
        # --- Bookmarks Tab ---
        self._create_bookmarks_widgets(self.bookmarks_tab)
        # --- Analytics Tab ---
        self._create_analytics_widgets(self.analytics_tab)
        # --- Coordinate Browser Tab ---
        self._create_coordinate_browser_widgets(self.coord_tab)
        # --- Page Comparison Tab ---
        self._create_page_comparison_widgets(self.compare_tab)

    def _create_manual_search_widgets(self, parent):
        # Input Frame
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

        # Evolution Mode Frame
        evolution_frame = ttk.LabelFrame(parent, text="Phrase Evolution Mode")
        evolution_frame.pack(fill="x", padx=10, pady=5)

        # Evolution controls row 1
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

        # Evolution controls row 2
        ttk.Label(evolution_frame, text="Generations:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.generations_var = tk.IntVar(value=5)
        ttk.Entry(evolution_frame, textvariable=self.generations_var, width=6).grid(row=1, column=1, sticky="w", padx=5, pady=5)

        ttk.Label(evolution_frame, text="Population Size:").grid(row=1, column=2, sticky="e", padx=5)
        self.population_size_var = tk.IntVar(value=20)
        ttk.Entry(evolution_frame, textvariable=self.population_size_var, width=6).grid(row=1, column=3, sticky="w", padx=5, pady=5)

        # Evolution buttons
        self.evolution_btn = ttk.Button(evolution_frame, text="Start Evolution", command=self.start_evolution_search)
        self.evolution_btn.grid(row=1, column=4, padx=10, pady=5)

        self.stop_evolution_btn = ttk.Button(evolution_frame, text="Stop Evolution", command=self.stop_evolution_search, state="disabled")
        self.stop_evolution_btn.grid(row=1, column=5, padx=5, pady=5)

        # Evolution mutation types
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

        # Evolution progress
        self.evolution_progress_var = tk.StringVar(value="Ready for evolution search")
        ttk.Label(evolution_frame, textvariable=self.evolution_progress_var).grid(row=3, column=0, columnspan=6, pady=5, sticky="w")

        # Progress Bar
        self.progress = ttk.Progressbar(parent, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", padx=10, pady=5)

        # Results Frame
        results_frame = ttk.LabelFrame(parent, text="Results")
        results_frame.pack(fill="both", expand=True, padx=10, pady=5)

        self.results_list = tk.Listbox(results_frame, height=10)
        self.results_list.pack(fill="x", padx=5, pady=5)
        self.results_list.bind('<<ListboxSelect>>', self.display_result)

        # Navigation + Bookmark Frame
        nav_bookmark_frame = ttk.Frame(results_frame)
        nav_bookmark_frame.pack(fill="x", padx=5, pady=2)
        ttk.Button(nav_bookmark_frame, text="Previous Result", command=self.prev_result, width=16).pack(side="left", padx=2, pady=2)
        ttk.Button(nav_bookmark_frame, text="Next Result", command=self.next_result, width=16).pack(side="left", padx=2, pady=2)
        ttk.Button(nav_bookmark_frame, text="Bookmark Selected Result", command=self.bookmark_current_result, width=24).pack(side="left", padx=10, pady=2)

        # Result Details
        self.result_text = tk.Text(results_frame, wrap="none", height=20, font=("Courier", 10))
        self.result_text.pack(fill="both", expand=True, padx=5, pady=5)
        ttk.Button(results_frame, text="Analyze Entropy/Noise", command=self.show_entropy_analysis).pack(fill="x", padx=5, pady=2)
        # Evolution Analysis Button
        ttk.Button(results_frame, text="Analyze Evolution Results", command=self.show_evolution_analysis).pack(fill="x", padx=5, pady=2)
        # Twin Page Discovery Button
        ttk.Button(results_frame, text="Find Twin Pages (±N)", command=self.show_twin_page_dialog).pack(fill="x", padx=5, pady=2)

        # Notes/Tags
        notes_frame = ttk.Frame(results_frame)
        notes_frame.pack(fill="x", padx=5, pady=2)
        ttk.Label(notes_frame, text="Notes/Tags:").pack(side="left")
        self.notes_var = tk.StringVar()
        self.notes_entry = ttk.Entry(notes_frame, textvariable=self.notes_var, width=60)
        self.notes_entry.pack(side="left", padx=5)
        self.save_note_btn = ttk.Button(notes_frame, text="Save Note", command=self.save_note)
        self.save_note_btn.pack(side="left", padx=5)

        # Export/Session/Performance Frame
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
        # Phrase management
        phrase_frame = ttk.LabelFrame(parent, text="Background Search Phrases")
        phrase_frame.pack(fill="x", padx=10, pady=5)
        self.bg_phrase_var = tk.StringVar()
        ttk.Entry(phrase_frame, textvariable=self.bg_phrase_var, width=40).pack(side="left", padx=5, pady=5)
        ttk.Button(phrase_frame, text="Add Phrase", command=self.add_bg_phrase).pack(side="left", padx=5)
        ttk.Button(phrase_frame, text="Remove Selected", command=self.remove_bg_phrase).pack(side="left", padx=5)
        self.bg_phrase_list = tk.Listbox(phrase_frame, height=5, selectmode=tk.MULTIPLE)
        self.bg_phrase_list.pack(fill="x", padx=5, pady=5)
        # Control buttons
        control_frame = ttk.Frame(parent)
        control_frame.pack(fill="x", padx=10, pady=5)
        self.bg_start_btn = ttk.Button(control_frame, text="Start Background Search", command=self.start_bg_search)
        self.bg_start_btn.pack(side="left", padx=5)
        self.bg_stop_btn = ttk.Button(control_frame, text="Stop", command=self.stop_bg_search, state="disabled")
        self.bg_stop_btn.pack(side="left", padx=5)
        # Log window
        log_frame = ttk.LabelFrame(parent, text="Background Search Log")
        log_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.bg_log_text = scrolledtext.ScrolledText(log_frame, height=20, font=("Courier", 10), state="disabled")
        self.bg_log_text.pack(fill="both", expand=True, padx=5, pady=5)
        # Add CPU core selection
        core_frame = ttk.Frame(parent)
        core_frame.pack(fill="x", padx=10, pady=2)
        ttk.Label(core_frame, text="CPU Cores:").pack(side="left")
        self.bg_cores_var = tk.IntVar(value=self.bg_num_cores)
        ttk.Spinbox(core_frame, from_=1, to=multiprocessing.cpu_count(), textvariable=self.bg_cores_var, width=4).pack(side="left", padx=5)
        # Load previous phrases if any
        self.load_bg_phrases()

    def _create_bookmarks_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        self.bookmarks_list = tk.Listbox(frame, height=15)
        self.bookmarks_list.pack(fill="x", padx=5, pady=5)
        self.bookmarks_list.bind('<<ListboxSelect>>', self.display_bookmark)
        self.bookmark_text = tk.Text(frame, wrap="none", height=20, font=("Courier", 10))
        self.bookmark_text.pack(fill="both", expand=True, padx=5, pady=5)
        # Entropy/Noise Analysis Button for Bookmarks
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
        ttk.Button(frame, text="Show Seed Distribution", command=self.show_seed_distribution).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Show Phrase Frequency", command=self.show_phrase_frequency).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Show Timeline", command=self.show_timeline).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Show Match Density Heatmap", command=self.show_match_density_heatmap).pack(side="left", padx=5, pady=5)
        ttk.Button(frame, text="Show Entropy Map Over Time", command=self.show_entropy_map).pack(side="left", padx=5, pady=5)
        self.analytics_canvas = None
        self.analytics_fig = None

    def _create_coordinate_browser_widgets(self, parent):
        frame = ttk.Frame(parent)
        frame.pack(fill="both", expand=True, padx=10, pady=10)
        # Coordinate input fields
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
        # Navigation buttons
        nav_frame = ttk.Frame(frame)
        nav_frame.pack(fill="x", padx=5, pady=5)
        for i, label in enumerate(labels):
            subframe = ttk.Frame(nav_frame)
            subframe.pack(side="left", padx=5)
            ttk.Label(subframe, text=label).pack()
            ttk.Button(subframe, text="-", width=2, command=lambda l=label.lower(): self.cb_adjust_coord(l, -1)).pack(side="left")
            ttk.Button(subframe, text="+", width=2, command=lambda l=label.lower(): self.cb_adjust_coord(l, 1)).pack(side="left")
        # Info display
        info_frame = ttk.Frame(frame)
        info_frame.pack(fill="x", padx=5, pady=5)
        self.cb_seed_label = ttk.Label(info_frame, text="Seed: 0")
        self.cb_seed_label.pack(side="left", padx=5)
        self.cb_coord_label = ttk.Label(info_frame, text="Coordinates: Hexagon 0, Wall 0, Shelf 0, Volume 0, Page 0")
        self.cb_coord_label.pack(side="left", padx=10)
        # Page display
        self.cb_page_text = tk.Text(frame, wrap="none", height=20, font=("Courier", 10))
        self.cb_page_text.pack(fill="both", expand=True, padx=5, pady=5)
        # Explorer Grid
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
        new_val = var.get() + delta
        if new_val < 0:
            new_val = 0
        var.set(new_val)
        self.cb_update_display()

    def cb_grid_jump(self, dr, dc):
        # Move to adjacent coordinate (page +/- 1, volume +/- 1, etc.)
        coords = list(self.cb_get_coords())
        # Only page coordinate is adjusted for grid (center is current)
        coords[4] += dr*1 + dc*1  # Diagonal/adjacent
        if coords[4] < 0:
            coords[4] = 0
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
        # Update explorer grid
        if hasattr(self, 'cb_grid_buttons'):
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
        except Exception as e:
            messagebox.showerror("Invalid Phrase", str(e))
            return
        if phrase not in self.bg_search_phrases:
            self.bg_search_phrases.append(phrase)
            self.bg_phrase_list.insert(tk.END, phrase)
            self.save_bg_phrases()
        self.bg_phrase_var.set("")

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

    def run_bg_search(self):
        # Load progress
        seed = 0
        if os.path.exists(BACKGROUND_PROGRESS_FILE):
            with open(BACKGROUND_PROGRESS_FILE, 'r', encoding='utf-8') as f:
                try:
                    data = json.load(f)
                    seed = data.get('last_seed', 0)
                except Exception:
                    seed = 0
        # Load previous results
        results = []
        if os.path.exists(BACKGROUND_RESULTS_FILE):
            with open(BACKGROUND_RESULTS_FILE, 'r', encoding='utf-8') as f:
                try:
                    results = json.load(f)
                except Exception:
                    results = []
        self.bg_search_running.set()
        while self.bg_search_running.is_set():
            page = generate_page(seed, length=PAGE_LENGTH)
            page_hash = self.compute_page_hash(page)
            for term in self.bg_search_phrases:
                idx = page.find(term)
                if idx != -1:
                    result = {
                        'phrase': term,
                        'seed': seed,
                        'index': idx,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'hash': page_hash
                    }
                    # Check for duplicates to avoid redundant storage
                    if not is_duplicate(result, results):
                        results.append(result)
                        self.append_bg_log(f"[FOUND] '{term}' at seed {seed}, index {idx}")
                        with open(BACKGROUND_RESULTS_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, indent=2)
            seed += 1
            with open(BACKGROUND_PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump({'last_seed': seed}, f)
        self.append_bg_log("[Background Search Stopped]")

    def run_bg_search_mp(self, num_cores):
        # Multiprocessing background search
        from multiprocessing import Process, Queue
        import queue as pyqueue
        def worker(start_seed, step, phrases, result_q, running_flag):
            seed = start_seed
            while running_flag.is_set():
                page = generate_page(seed, length=PAGE_LENGTH)
                page_hash = self.compute_page_hash(page)
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
        # Shared result queue and running flag
        result_q = multiprocessing.Queue()
        running_flag = multiprocessing.Event()
        running_flag.set()
        # Start worker processes
        workers = []
        for i in range(num_cores):
            p = Process(target=worker, args=(i, num_cores, self.bg_search_phrases, result_q, running_flag))
            p.start()
            workers.append(p)
        # Load previous results
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
        try:
            while self.bg_search_running.is_set():
                try:
                    result = result_q.get(timeout=0.5)
                    # Check for duplicates before adding
                    if not is_duplicate(result, results):
                        results.append(result)
                        self.append_bg_log(f"[FOUND] '{result['phrase']}' at seed {result['seed']}, index {result['index']}")
                        with open(BACKGROUND_RESULTS_FILE, 'w', encoding='utf-8') as f:
                            json.dump(results, f, indent=2)
                except pyqueue.Empty:
                    pass
                # Save progress (approximate)
                with open(BACKGROUND_PROGRESS_FILE, 'w', encoding='utf-8') as f:
                    json.dump({'last_seed': seed}, f)
        finally:
            running_flag.clear()
            for p in workers:
                p.terminate()
            self.append_bg_log("[Background Search Stopped]")

    def append_bg_log(self, msg):
        self.bg_log_text.config(state="normal")
        self.bg_log_text.insert(tk.END, msg + "\n")
        self.bg_log_text.see(tk.END)
        self.bg_log_text.config(state="disabled")

    def bookmark_current_result(self):
        sel = self.results_list.curselection()
        if not sel:
            return
        idx = sel[0]
        result = self.results[idx]
        if result not in self.bookmarks:
            self.bookmarks.append(result)
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
        page = result['page'] if 'page' in result else generate_page(result['seed'], length=PAGE_LENGTH)
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
                # Ensure hash is present
                if 'hash' not in r:
                    page = r.get('page') or generate_page(r['seed'], length=PAGE_LENGTH)
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
        # Ensure all hashes are present
        for r in self.bookmarks:
            if 'hash' not in r:
                page = r.get('page') or generate_page(r['seed'], length=PAGE_LENGTH)
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
        t = threading.Thread(target=self.run_search, args=(phrase,))
        t.start()

    def compute_page_hash(self, page):
        return hashlib.sha256(page.encode('utf-8')).hexdigest()

    def wildcard_match(self, text, pattern):
        """
        Returns True if text matches pattern with wildcards (*, ?).
        * matches any sequence, ? matches any single character.
        """
        import re
        # Escape regex special chars except * and ?
        pattern = re.escape(pattern)
        pattern = pattern.replace(r'\*', '.*').replace(r'\?', '.')
        regex = re.compile(pattern, re.IGNORECASE)
        return regex.search(text) is not None

    def find_wildcard_matches(self, page, pattern):
        """
        Returns list of (start, end) indices for all matches of pattern in page.
        """
        import re
        pattern_re = re.escape(pattern)
        pattern_re = pattern_re.replace(r'\*', '.*').replace(r'\?', '.')
        regex = re.compile(pattern_re, re.IGNORECASE)
        return [(m.start(), m.end()) for m in regex.finditer(page)]

    def longest_common_substring(self, s1, s2):
        """Returns (length, start_idx_in_s2) of the longest common substring between s1 and s2."""
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
        max_matches = self.max_matches_var.get()
        max_attempts = self.max_attempts_var.get()
        page_length = self.page_length_var.get()
        found = []
        is_wildcard = '*' in phrase or '?' in phrase
        start_time = time.time()
        last_update = start_time
        for i in range(max_attempts):
            page = generate_page(i, length=page_length)
            page_hash = self.compute_page_hash(page)
            if is_wildcard:
                matches = self.find_wildcard_matches(page, phrase)
                for idx, end in matches:
                    found.append({
                        'seed': i,
                        'index': idx,
                        'page': page,
                        'phrase': phrase,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'notes': '',
                        'hash': page_hash
                    })
                    self.results_list.insert(tk.END, f"Match {len(found)}: Seed={i}, Index={idx}")
                    if len(found) >= max_matches:
                        break
            else:
                idx = page.lower().find(phrase.lower())
                if idx != -1:
                    found.append({
                        'seed': i,
                        'index': idx,
                        'page': page,
                        'phrase': phrase,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'notes': '',
                        'hash': page_hash
                    })
                    self.results_list.insert(tk.END, f"Match {len(found)}: Seed={i}, Index={idx}")
                    if len(found) >= max_matches:
                        break
            if len(found) >= max_matches:
                break
            if i % 1000 == 0 or i == max_attempts - 1:
                elapsed = time.time() - start_time
                speed = (i+1) / elapsed if elapsed > 0 else 0
                matches_per_hour = (len(found) / elapsed * 3600) if elapsed > 0 else 0
                cpu = psutil.cpu_percent(interval=0.0)
                self.perf_label.config(text=f"Progress: {i+1}/{max_attempts} | Speed: {speed:.1f} pages/sec | Matches/hr: {matches_per_hour:.1f} | CPU: {cpu:.1f}%")
                self.progress['value'] = (i+1) / max_attempts * 100
                self.update_idletasks()
        # If no matches, try partial match scoring on last 1000 pages
        if not found:
            partials = []
            check_pages = min(1000, max_attempts)
            for i in range(max_attempts - check_pages, max_attempts):
                page = generate_page(i, length=page_length)
                score, idx = self.longest_common_substring(phrase, page)
                if score > 2:  # Only show if at least 3 chars match
                    partials.append({
                        'seed': i,
                        'index': idx,
                        'page': page,
                        'phrase': phrase,
                        'timestamp': datetime.datetime.now().isoformat(),
                        'notes': '',
                        'partial_score': score,
                        'hash': self.compute_page_hash(page)
                    })
            # Sort by score descending, take top N
            partials.sort(key=lambda r: -r['partial_score'])
            for j, r in enumerate(partials[:max_matches]):
                found.append(r)
                self.results_list.insert(tk.END, f"Partial Match {j+1}: Seed={r['seed']}, Index={r['index']}, Score={r['partial_score']}")
            if found:
                messagebox.showinfo("Partial Matches", "No exact matches found. Showing best partial matches.")
            else:
                messagebox.showinfo("No Matches", "No matches found in sample search range.")
        self.perf_label.config(text="Search complete.")
        self.results = found
        self.search_btn.config(state="normal")
        if not found:
            messagebox.showinfo("No Matches", "No matches found in sample search range.")

    def seed_to_coordinates(self, seed):
        # Example: symbolic mapping (hexagon, wall, shelf, volume, page)
        # You can adjust the base values for a more Borges-like library
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
        page = result['page'] if 'page' in result else generate_page(result['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200)
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
        if not hasattr(self, 'coord_label'):
            self.coord_label = ttk.Label(self.result_text.master, text="")
            self.coord_label.pack(anchor="w", padx=5, pady=2)
        hash_val = result.get('hash')
        if not hash_val:
            hash_val = self.compute_page_hash(page)
            result['hash'] = hash_val
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
        note = self.notes_var.get()
        self.results[idx]['notes'] = note
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
                # Ensure hash is present
                if 'hash' not in r:
                    page = r.get('page') or generate_page(r['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200)
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
        # Ensure all hashes are present
        for r in self.results:
            if 'hash' not in r:
                page = r.get('page') or generate_page(r['seed'], length=self.page_length_var.get() if hasattr(self, 'page_length_var') else 3200)
                r['hash'] = self.compute_page_hash(page)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, indent=2)
        messagebox.showinfo("Exported", f"Results exported to {file}")

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
                # Ensure hash is present
                if 'hash' not in r:
                    page = r.get('page') or generate_page(r['seed'], length=PAGE_LENGTH)
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
        # Ensure all hashes are present
        for r in self.bookmarks:
            if 'hash' not in r:
                page = r.get('page') or generate_page(r['seed'], length=PAGE_LENGTH)
                r['hash'] = self.compute_page_hash(page)
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(self.bookmarks, f, indent=2)
        messagebox.showinfo("Exported", f"Bookmarks exported to {file}")

    def _create_page_comparison_widgets(self, parent):
        """Create the page comparison interface."""
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Input section
        input_frame = ttk.LabelFrame(main_frame, text="Page Selection")
        input_frame.pack(fill="x", padx=5, pady=5)
        
        # Page 1 selection
        page1_frame = ttk.Frame(input_frame)
        page1_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Label(page1_frame, text="Page 1 Seed:").pack(side="left", padx=5)
        self.compare_seed1_var = tk.IntVar(value=0)
        ttk.Entry(page1_frame, textvariable=self.compare_seed1_var, width=12).pack(side="left", padx=5)
        ttk.Button(page1_frame, text="Load Page 1", command=self.load_comparison_page1).pack(side="left", padx=5)
        ttk.Button(page1_frame, text="From Current Result", command=self.load_page1_from_result).pack(side="left", padx=5)
        
        # Page 2 selection
        page2_frame = ttk.Frame(input_frame)
        page2_frame.grid(row=1, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Label(page2_frame, text="Page 2 Seed:").pack(side="left", padx=5)
        self.compare_seed2_var = tk.IntVar(value=1)
        ttk.Entry(page2_frame, textvariable=self.compare_seed2_var, width=12).pack(side="left", padx=5)
        ttk.Button(page2_frame, text="Load Page 2", command=self.load_comparison_page2).pack(side="left", padx=5)
        ttk.Button(page2_frame, text="From Current Result", command=self.load_page2_from_result).pack(side="left", padx=5)
        
        # Comparison controls
        control_frame = ttk.Frame(input_frame)
        control_frame.grid(row=2, column=0, columnspan=3, sticky="ew", padx=5, pady=5)
        ttk.Button(control_frame, text="Compare Pages", command=self.compare_loaded_pages).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Find Similar Pages", command=self.find_similar_pages_dialog).pack(side="left", padx=5)
        ttk.Button(control_frame, text="Analyze Neighborhood", command=self.analyze_page_neighborhood_dialog).pack(side="left", padx=5)
        
        # Comparison results notebook
        self.comparison_notebook = ttk.Notebook(main_frame)
        self.comparison_notebook.pack(fill="both", expand=True, pady=10)
        
        self._create_comparison_tabs()

    def _create_comparison_tabs(self):
        """Create tabs for the comparison notebook."""
        
        # Side-by-side view tab
        self.sidebyside_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(self.sidebyside_frame, text="Side-by-Side")
        
        # Create two text widgets side by side
        text_frame = ttk.Frame(self.sidebyside_frame)
        text_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Page 1 text widget
        page1_frame = ttk.LabelFrame(text_frame, text="Page 1")
        page1_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))
        self.compare_text1 = scrolledtext.ScrolledText(page1_frame, wrap="word", height=20, font=("Courier", 9))
        self.compare_text1.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Page 2 text widget
        page2_frame = ttk.LabelFrame(text_frame, text="Page 2")
        page2_frame.pack(side="right", fill="both", expand=True, padx=(5, 0))
        self.compare_text2 = scrolledtext.ScrolledText(page2_frame, wrap="word", height=20, font=("Courier", 9))
        self.compare_text2.pack(fill="both", expand=True, padx=5, pady=5)
        
        # Differences tab
        self.differences_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(self.differences_frame, text="Differences")
        
        self.differences_text = scrolledtext.ScrolledText(self.differences_frame, wrap="word", font=("Courier", 10))
        self.differences_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Common substrings tab
        self.common_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(self.common_frame, text="Common Substrings")
        
        self.common_text = scrolledtext.ScrolledText(self.common_frame, wrap="word", font=("Courier", 10))
        self.common_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Statistics tab
        self.stats_frame = ttk.Frame(self.comparison_notebook)
        self.comparison_notebook.add(self.stats_frame, text="Statistics")
        
        self.stats_text = scrolledtext.ScrolledText(self.stats_frame, wrap="word", font=("Courier", 10))
        self.stats_text.pack(fill="both", expand=True, padx=10, pady=10)

    def load_comparison_page1(self):
        """Load page 1 from the specified seed."""
        try:
            seed = self.compare_seed1_var.get()
            self.comparison_page1 = generate_page(seed, PAGE_LENGTH)
            self.comparison_seed1 = seed
            self.compare_text1.delete(1.0, tk.END)
            self.compare_text1.insert(1.0, self.comparison_page1)
            self.compare_text1.config(state="disabled")
            messagebox.showinfo("Success", f"Page 1 loaded from seed {seed}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page 1: {str(e)}")

    def load_comparison_page2(self):
        """Load page 2 from the specified seed."""
        try:
            seed = self.compare_seed2_var.get()
            self.comparison_page2 = generate_page(seed, PAGE_LENGTH)
            self.comparison_seed2 = seed
            self.compare_text2.delete(1.0, tk.END)
            self.compare_text2.insert(1.0, self.comparison_page2)
            self.compare_text2.config(state="disabled")
            messagebox.showinfo("Success", f"Page 2 loaded from seed {seed}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page 2: {str(e)}")

    def load_page1_from_result(self):
        """Load page 1 from the currently selected result."""
        try:
            selected = self.results_list.curselection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a result first")
                return
            
            result = self.results[selected[0]]
            seed = result['seed']
            self.compare_seed1_var.set(seed)
            self.load_comparison_page1()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page from result: {str(e)}")

    def load_page2_from_result(self):
        """Load page 2 from the currently selected result."""
        try:
            selected = self.results_list.curselection()
            if not selected:
                messagebox.showwarning("No Selection", "Please select a result first")
                return
            
            result = self.results[selected[0]]
            seed = result['seed']
            self.compare_seed2_var.set(seed)
            self.load_comparison_page2()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load page from result: {str(e)}")

    def compare_loaded_pages(self):
        """Compare the two loaded pages and display results."""
        if self.comparison_page1 is None or self.comparison_page2 is None:
            messagebox.showwarning("Missing Pages", "Please load both pages first")
            return
        
        try:
            # Run comprehensive comparison
            self.comparison_results = compare_pages(self.comparison_page1, self.comparison_page2)
            
            # Update all tabs with results
            self.update_comparison_displays()
            
            # Show summary
            similarity = self.comparison_results['similarity_percentage']
            messagebox.showinfo("Comparison Complete", 
                              f"Pages compared successfully!\nSimilarity: {similarity:.2f}%")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to compare pages: {str(e)}")

    def update_comparison_displays(self):
        """Update all comparison display tabs with results."""
        if not self.comparison_results:
            return
        
        # Update differences tab
        self.differences_text.delete(1.0, tk.END)
        differences = highlight_differences(self.comparison_page1, self.comparison_page2)
        if differences:
            self.differences_text.insert(tk.END, f"Found {len(differences)} differences:\n\n")
            for i, diff in enumerate(differences, 1):
                self.differences_text.insert(tk.END, f"Difference {i} at position {diff['position']}:\n")
                self.differences_text.insert(tk.END, f"  Page 1: '{diff['page1_text']}'\n")
                self.differences_text.insert(tk.END, f"  Page 2: '{diff['page2_text']}'\n")
                self.differences_text.insert(tk.END, f"  Context: '{diff['context1']}'\n\n")
        else:
            self.differences_text.insert(tk.END, "No differences found - pages are identical!")
        
        # Update similarities tab
        self.similarities_text.delete(1.0, tk.END)
        similarities = find_common_substrings(self.comparison_page1, self.comparison_page2)
        if similarities:
            self.similarities_text.insert(tk.END, f"Found {len(similarities)} common substrings:\n\n")
            for i, sim in enumerate(similarities[:20], 1):  # Show top 20
                self.similarities_text.insert(tk.END, f"{i}. '{sim['substring']}' (length: {sim['length']})\n")
                self.similarities_text.insert(tk.END, f"   Position in page 1: {sim['pos1']}\n")
                self.similarities_text.insert(tk.END, f"   Position in page 2: {sim['pos2']}\n\n")
        else:
            self.similarities_text.insert(tk.END, "No common substrings found")
        
        # Update statistics tab
        self.stats_text.delete(1.0, tk.END)
        stats = self.comparison_results
        stats_text = f"""Page Comparison Statistics

Seeds: {self.comparison_seed1} vs {self.comparison_seed2}
Pages identical: {stats['identical']}
Similarity percentage: {stats['similarity_percentage']:.2f}%
Edit distance: {stats['edit_distance']}
Length difference: {stats['length_diff']}

Content Analysis:
Longest common substring: '{stats['longest_common_substring'][:50]}...' (length: {stats['lcs_length']})
Entropy page 1: {stats['entropy1']:.4f}
Entropy page 2: {stats['entropy2']:.4f}
Entropy difference: {stats['entropy_difference']:.4f}
Frequency difference: {stats['frequency_difference']:.2f}%

Pattern Analysis:
Common patterns: {stats['common_patterns']}
Total patterns page 1: {stats['total_patterns1']}
Total patterns page 2: {stats['total_patterns2']}
Pattern overlap ratio: {stats['pattern_overlap_ratio']:.4f}

Hashes:
Page 1: {stats['hash1'][:16]}...
Page 2: {stats['hash2'][:16]}...
"""
        self.stats_text.insert(tk.END, stats_text)

    def sync_scroll(self, event):
        """Sync scrolling between the two comparison text widgets."""
        # Get the widget that triggered the event
        widget = event.widget
        
        # Calculate the scroll position
        if event.delta > 0:
            delta = -1
        else:
            delta = 1
        
        # Scroll both widgets
        self.compare_text1.yview_scroll(delta, "units")
        self.compare_text2.yview_scroll(delta, "units")
        
        return "break"  # Prevent default scrolling

    def find_similar_pages_dialog(self):
        """Open dialog to find pages similar to a selected page."""
        if not hasattr(self, 'comparison_seed1') or self.comparison_seed1 is None:
            messagebox.showwarning("No Page", "Please load page 1 first")
            return
        
        # Simple dialog for now - in a real implementation, this would be more sophisticated
        range_str = tk.simpledialog.askstring("Find Similar Pages", 
                                             "Enter search range (number of seeds to check):", 
                                             initialvalue="1000")
        if not range_str:
            return
        
        try:
            search_range = int(range_str)
            similar_pages = search_for_similar_pages(self.comparison_seed1, search_range)
            
            if similar_pages:
                result_text = f"Found {len(similar_pages)} similar pages:\n\n"
                for page in similar_pages:
                    result_text += f"Seed {page['similar_seed']}: {page['similarity']:.2f}% similar\n"
                
                # Show results in a new window
                result_window = tk.Toplevel(self)
                result_window.title("Similar Pages")
                result_window.geometry("600x400")
                
                text_widget = scrolledtext.ScrolledText(result_window, wrap="word")
                text_widget.pack(fill="both", expand=True, padx=10, pady=10)
                text_widget.insert(tk.END, result_text)
                
            else:
                messagebox.showinfo("No Results", "No similar pages found in the specified range")
                
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter a valid number")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to find similar pages: {str(e)}")

    def analyze_page_neighborhood_dialog(self):
        """Analyze the neighborhood around a selected page."""
        if not hasattr(self, 'comparison_seed1') or self.comparison_seed1 is None:
            messagebox.showwarning("No Page", "Please load page 1 first")
            return
        
        from babel_tools import analyze_page_neighborhood
        
        try:
            neighborhood = analyze_page_neighborhood(self.comparison_seed1, radius=10)
            
            result_text = f"Neighborhood Analysis for Seed {self.comparison_seed1}\n\n"
            result_text += f"Average similarity to center: {neighborhood['avg_similarity']:.2f}%\n"
            result_text += f"Max similarity: {neighborhood['max_similarity']:.2f}%\n"
            result_text += f"Min similarity: {neighborhood['min_similarity']:.2f}%\n"
            result_text += f"Average entropy: {neighborhood['avg_entropy']:.4f}\n"
            result_text += f"Entropy variation: {neighborhood['entropy_variation']:.4f}\n\n"
            
            result_text += "Neighborhood details:\n"
            for neighbor in neighborhood['neighborhood']:
                result_text += f"Seed {neighbor['seed']} (offset {neighbor['offset']:+d}): "
                result_text += f"similarity {neighbor['similarity_to_center']:.2f}%, "
                result_text += f"entropy {neighbor['entropy']:.4f}\n"
            
            # Show results in a new window
            result_window = tk.Toplevel(self)
            result_window.title("Neighborhood Analysis")
            result_window.geometry("700x500")
            
            text_widget = scrolledtext.ScrolledText(result_window, wrap="word")
            text_widget.pack(fill="both", expand=True, padx=10, pady=10)
            text_widget.insert(tk.END, result_text)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze neighborhood: {str(e)}")

    def update_mutation_label(self, value):
        """Update the mutation rate label when slider changes."""
        self.mutation_label.config(text=f"{float(value):.1f}")

    def start_evolution_search(self):
        """Start evolutionary phrase search."""
        messagebox.showinfo("Evolution Mode", "Evolution search functionality is being implemented. Please use manual search for now.")

    def stop_evolution_search(self):
        """Stop the evolution search."""
        messagebox.showinfo("Evolution Mode", "Evolution search functionality is being implemented.")

    def show_evolution_analysis(self):
        """Show analysis of evolution results."""
        messagebox.showinfo("Evolution Analysis", "Evolution analysis functionality is being implemented.")

    def show_entropy_analysis(self):
        """Show entropy analysis of selected result."""
        messagebox.showinfo("Entropy Analysis", "Entropy analysis functionality is being implemented.")

    def show_bookmark_entropy_analysis(self):
        """Show entropy analysis of bookmarked pages."""
        messagebox.showinfo("Bookmark Analysis", "Bookmark entropy analysis functionality is being implemented.")

    def show_twin_page_dialog(self):
        """Show dialog for finding twin pages."""
        messagebox.showinfo("Twin Pages", "Twin page discovery functionality is being implemented.")

    def load_background_results(self):
        """Load background search results."""
        messagebox.showinfo("Background Results", "Background results loading is being implemented.")

    def jump_to_seed_dialog(self):
        """Show dialog to jump to a specific seed."""
        messagebox.showinfo("Jump to Seed", "Seed jumping functionality is being implemented.")

    def show_seed_reverse_lookup(self):
        """Show seed reverse lookup dialog."""
        messagebox.showinfo("Reverse Lookup", "Seed reverse lookup is being implemented.")

    def show_entropy_map(self):
        """Show entropy map visualization."""
        messagebox.showinfo("Entropy Map", "Entropy mapping is being implemented.")

    def show_seed_distribution(self):
        """Show seed distribution analysis."""
        messagebox.showinfo("Seed Distribution", "Seed distribution analysis is being implemented.")

    def show_phrase_frequency(self):
        """Show phrase frequency analysis."""
        messagebox.showinfo("Phrase Frequency", "Phrase frequency analysis is being implemented.")

    def show_timeline(self):
        """Show timeline analysis."""
        messagebox.showinfo("Timeline", "Timeline analysis is being implemented.")

    def show_match_density_heatmap(self):
        """Show match density heatmap."""
        messagebox.showinfo("Heatmap", "Match density heatmap is being implemented.")

    def save_session(self):
        """Save current session."""
        messagebox.showinfo("Save Session", "Session saving is being implemented.")

    def load_session(self):
        """Load a saved session.""" 
        messagebox.showinfo("Load Session", "Session loading is being implemented.")

    def remove_selected_bookmark(self):
        """Remove selected bookmark."""
        messagebox.showinfo("Remove Bookmark", "Bookmark removal is being implemented.")

    # ...existing code...