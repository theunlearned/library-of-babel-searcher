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
from datetime import datetime
import time
import os
import random
import multiprocessing
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
    import hashlib
    from datetime import datetime
    from babel import generate_page
    
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
                        'timestamp': datetime.now().isoformat(),
                        'hash': page_hash
                    }
                    result_q.put(result)
            seed += step
        except Exception as e:
            # Skip this seed and continue
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
        
        # Initialize queue for thread-safe GUI updates
        self.result_queue = queue.Queue()
        self.update_queue = queue.Queue()
        
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
        
        # Start queue processing for thread-safe GUI updates
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

    def process_search_queue(self):
        """Process messages from the search thread queue."""
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
                    # Handle background search log messages
                    msg = message['data']
                    if hasattr(self, 'bg_log_text'):
                        self.bg_log_text.config(state="normal")
                        self.bg_log_text.insert(tk.END, msg + "\n")
                        self.bg_log_text.see(tk.END)
                        self.bg_log_text.config(state="disabled")
                        
        except queue.Empty:
            pass
        
        # Schedule next check
        self.after(100, self.process_search_queue)

    def start_queue_processing(self):
        """Start the queue processing loop."""
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
        
        # Shared result queue and running flag
        result_q = Queue()
        running_flag = multiprocessing.Event()
        running_flag.set()
        
        # Start worker processes
        workers = []
        for i in range(num_cores):
            p = Process(target=bg_search_worker, args=(i, num_cores, self.bg_search_phrases, result_q, running_flag))
            p.daemon = True
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
        
        self.append_bg_log(f"[STARTED] Background search with {num_cores} cores")
        
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
                
                # Save progress periodically
                seed += num_cores
                if seed % 10000 == 0:  # Save every 10000 seeds
                    with open(BACKGROUND_PROGRESS_FILE, 'w', encoding='utf-8') as f:
                        json.dump({'last_seed': seed}, f)
                        
        finally:
            running_flag.clear()
            for p in workers:
                p.terminate()
                p.join(timeout=1.0)
            self.append_bg_log("[Background Search Stopped]")

    def append_bg_log(self, msg):
        # Use the queue to safely update the GUI from any thread
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
        t = threading.Thread(target=self.run_search, args=(phrase,), daemon=True)
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
                            'timestamp': datetime.now().isoformat(),
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
                            'timestamp': datetime.now().isoformat(),
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
                    
                # Update progress every 1000 iterations
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
            
            # Send completion message
            self.result_queue.put({
                'type': 'search_complete',
                'data': {
                    'show_message': len(found) == 0,
                    'title': 'Search Complete' if found else 'No Matches',
                    'message': f'Found {len(found)} matches.' if found else 'No matches found.'
                }
            })
                
        except Exception as e:
            # Send error completion message to queue
            self.result_queue.put({
                'type': 'search_complete',
                'data': {
                    'show_message': True,
                    'title': 'Search Error',
                    'message': f'Search failed: {str(e)}'
                }
            })

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
        phrase = self.phrase_var.get().strip()
        if not phrase:
            messagebox.showwarning("Missing Input", "Please enter a phrase to search for.")
            return
        
        if not validate_phrase(phrase):
            messagebox.showerror("Invalid Phrase", "Phrase contains invalid characters.")
            return
        
        try:
            # Get evolution parameters
            mutation_rate = float(self.mutation_slider.get())
            generation_size = 50  # Fixed population size
            max_generations = 100  # Maximum generations
            
            # Create evolution dialog
            evolution_dialog = tk.Toplevel(self.root)
            evolution_dialog.title("Evolution Search Progress")
            evolution_dialog.geometry("600x400")
            evolution_dialog.transient(self.root)
            
            # Progress frame
            progress_frame = ttk.Frame(evolution_dialog, padding="20")
            progress_frame.pack(fill="both", expand=True)
            
            ttk.Label(progress_frame, text=f"Evolving search for: {phrase}", 
                     font=("Arial", 12, "bold")).pack(pady=(0, 10))
            
            # Progress bar
            progress_var = tk.DoubleVar()
            progress_bar = ttk.Progressbar(progress_frame, variable=progress_var, maximum=max_generations)
            progress_bar.pack(fill="x", pady=(0, 10))
            
            # Status labels
            generation_label = ttk.Label(progress_frame, text="Generation: 0")
            generation_label.pack(anchor="w")
            
            best_score_label = ttk.Label(progress_frame, text="Best Score: 0")
            best_score_label.pack(anchor="w")
            
            found_label = ttk.Label(progress_frame, text="Matches Found: 0")
            found_label.pack(anchor="w")
            
            # Results text
            results_text = tk.Text(progress_frame, height=10, wrap=tk.WORD)
            results_scrollbar = ttk.Scrollbar(progress_frame, orient="vertical", command=results_text.yview)
            results_text.configure(yscrollcommand=results_scrollbar.set)
            
            results_text.pack(side="left", fill="both", expand=True, pady=(10, 0))
            results_scrollbar.pack(side="right", fill="y", pady=(10, 0))
            
            # Stop button
            stop_button = ttk.Button(progress_frame, text="Stop Search")
            stop_button.pack(pady=(10, 0))
            
            # Evolution state
            self.evolution_running = True
            evolution_results = []
            
            def stop_evolution():
                self.evolution_running = False
                stop_button.config(text="Stopping...", state="disabled")
            
            stop_button.config(command=stop_evolution)
            
            def evolution_search_thread():
                try:
                    # Initialize population with random seeds
                    population = [random.randint(1, 2**31 - 1) for _ in range(generation_size)]
                    best_score = 0
                    
                    for generation in range(max_generations):
                        if not self.evolution_running:
                            break
                        
                        # Evaluate population
                        fitness_scores = []
                        generation_results = []
                        
                        for seed in population:
                            page = generate_page(seed)
                            
                            # Calculate fitness (similarity to target phrase)
                            fitness = 0
                            best_match_index = -1
                            
                            # Look for exact matches first
                            if phrase in page:
                                fitness = 1000  # High score for exact match
                                best_match_index = page.find(phrase)
                                
                                # Add this result
                                result = {
                                    'seed': seed,
                                    'page': 1,
                                    'index': best_match_index,
                                    'phrase': phrase,
                                    'timestamp': datetime.now().isoformat(),
                                    'generation': generation
                                }
                                generation_results.append(result)
                            else:
                                # Calculate similarity-based fitness
                                max_similarity = 0
                                for i in range(len(page) - len(phrase) + 1):
                                    substring = page[i:i+len(phrase)]
                                    similarity = similarity_percentage(phrase, substring)
                                    if similarity > max_similarity:
                                        max_similarity = similarity
                                        best_match_index = i
                                
                                fitness = max_similarity
                            
                            fitness_scores.append((seed, fitness, best_match_index))
                        
                        # Update best score
                        current_best = max(fitness_scores, key=lambda x: x[1])[1]
                        if current_best > best_score:
                            best_score = current_best
                        
                        # Add generation results to main results
                        evolution_results.extend(generation_results)
                        
                        # Update UI
                        evolution_dialog.after(0, lambda g=generation, bs=best_score, found=len(generation_results): (
                            progress_var.set(g + 1),
                            generation_label.config(text=f"Generation: {g + 1}"),
                            best_score_label.config(text=f"Best Score: {bs:.2f}"),
                            found_label.config(text=f"Matches Found: {len(evolution_results)}")
                        ))
                        
                        # Add results to text
                        if generation_results:
                            for result in generation_results:
                                result_text = f"Gen {generation}: Seed {result['seed']} -> Match at index {result['index']}\n"
                                evolution_dialog.after(0, lambda rt=result_text: (
                                    results_text.insert(tk.END, rt),
                                    results_text.see(tk.END)
                                ))
                        
                        # Selection and reproduction
                        if generation < max_generations - 1:
                            # Sort by fitness
                            fitness_scores.sort(key=lambda x: x[1], reverse=True)
                            
                            # Select top performers
                            elite_size = generation_size // 4
                            elite = [x[0] for x in fitness_scores[:elite_size]]
                            
                            # Create new population
                            new_population = elite[:]  # Keep elite
                            
                            # Fill rest with mutations and crossovers
                            while len(new_population) < generation_size:
                                if random.random() < 0.5 and len(elite) >= 2:
                                    # Crossover
                                    parent1, parent2 = random.sample(elite, 2)
                                    child = (parent1 + parent2) // 2  # Simple crossover
                                else:
                                    # Mutation
                                    parent = random.choice(elite)
                                    mutation_amount = int(parent * mutation_rate / 100)
                                    child = parent + random.randint(-mutation_amount, mutation_amount)
                                    child = max(1, min(2**31 - 1, child))  # Keep in valid range
                                
                                new_population.append(child)
                            
                            population = new_population
                    
                    # Evolution complete
                    evolution_dialog.after(0, lambda: (
                        stop_button.config(text="Close", state="normal", command=evolution_dialog.destroy),
                        results_text.insert(tk.END, f"\nEvolution complete! Found {len(evolution_results)} total matches.")
                    ))
                    
                    # Add all results to main results
                    for result in evolution_results:
                        if not is_duplicate(result, self.results):
                            self.results.append(result)
                    
                    # Refresh main display
                    self.root.after(0, self.refresh_results_display)
                    
                except Exception as e:
                    evolution_dialog.after(0, lambda: messagebox.showerror("Error", f"Evolution search failed: {str(e)}"))
            
            # Start evolution in separate thread
            thread = threading.Thread(target=evolution_search_thread)
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start evolution search: {str(e)}")

    def stop_evolution_search(self):
        """Stop the evolution search."""
        if hasattr(self, 'evolution_running'):
            self.evolution_running = False
            messagebox.showinfo("Evolution Stopped", "Evolution search has been stopped.")
        else:
            messagebox.showinfo("No Evolution", "No evolution search is currently running.")

    def show_evolution_analysis(self):
        """Show analysis of evolution results."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results available for evolution analysis.")
            return
        
        try:
            # Create analysis window
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Evolution Analysis")
            analysis_window.geometry("1000x800")
            
            # Main frame
            main_frame = ttk.Frame(analysis_window, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Create notebook for different analysis tabs
            notebook = ttk.Notebook(main_frame)
            notebook.pack(fill="both", expand=True)
            
            # Tab 1: Diversity Analysis
            diversity_frame = ttk.Frame(notebook)
            notebook.add(diversity_frame, text="Diversity Analysis")
            
            # Calculate diversity metrics
            unique_seeds = len(set(r['seed'] for r in self.results))
            unique_phrases = len(set(r.get('phrase', '') for r in self.results))
            total_results = len(self.results)
            
            # Seed entropy (diversity measure)
            seeds = [r['seed'] for r in self.results]
            seed_counts = {}
            for seed in seeds:
                seed_counts[seed] = seed_counts.get(seed, 0) + 1
            
            # Calculate Shannon entropy of seed distribution
            total_count = len(seeds)
            seed_entropy = 0
            for count in seed_counts.values():
                probability = count / total_count
                if probability > 0:
                    seed_entropy -= probability * np.log2(probability)
            
            # Create diversity visualization
            fig1, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
            
            # Seed distribution
            ax1.hist(seeds, bins=min(50, unique_seeds), alpha=0.7, color='lightblue', edgecolor='black')
            ax1.set_title(f'Seed Distribution (Entropy: {seed_entropy:.2f})')
            ax1.set_xlabel('Seed Value')
            ax1.set_ylabel('Frequency')
            ax1.grid(True, alpha=0.3)
            
            # Phrase length distribution
            phrase_lengths = [len(r.get('phrase', '')) for r in self.results if r.get('phrase')]
            if phrase_lengths:
                ax2.hist(phrase_lengths, bins=min(20, max(phrase_lengths) - min(phrase_lengths) + 1), 
                        alpha=0.7, color='lightgreen', edgecolor='black')
                ax2.set_title('Phrase Length Distribution')
                ax2.set_xlabel('Phrase Length')
                ax2.set_ylabel('Frequency')
                ax2.grid(True, alpha=0.3)
            else:
                ax2.text(0.5, 0.5, 'No phrase data available', ha='center', va='center', transform=ax2.transAxes)
            
            # Index distribution
            indices = [r.get('index', 0) for r in self.results]
            ax3.hist(indices, bins=min(50, len(indices)), alpha=0.7, color='lightcoral', edgecolor='black')
            ax3.set_title('Index Position Distribution')
            ax3.set_xlabel('Index Position')
            ax3.set_ylabel('Frequency')
            ax3.grid(True, alpha=0.3)
            
            # Diversity over time
            ax4.plot(range(len(self.results)), np.cumsum([1 if r['seed'] not in [res['seed'] for res in self.results[:i]] else 0 
                                                         for i, r in enumerate(self.results)]), 
                    'o-', markersize=3, color='purple')
            ax4.set_title('Unique Seeds Discovered Over Time')
            ax4.set_xlabel('Search Number')
            ax4.set_ylabel('Cumulative Unique Seeds')
            ax4.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Embed plot
            canvas1 = FigureCanvasTkAgg(fig1, diversity_frame)
            canvas1.draw()
            canvas1.get_tk_widget().pack(fill="both", expand=True)
            
            # Tab 2: Statistical Analysis
            stats_frame = ttk.Frame(notebook)
            notebook.add(stats_frame, text="Statistical Summary")
            
            # Create stats text
            stats_text = tk.Text(stats_frame, wrap=tk.WORD, padx=10, pady=10)
            stats_scrollbar = ttk.Scrollbar(stats_frame, orient="vertical", command=stats_text.yview)
            stats_text.configure(yscrollcommand=stats_scrollbar.set)
            
            # Calculate additional statistics
            if indices:
                avg_index = np.mean(indices)
                std_index = np.std(indices)
                min_index = min(indices)
                max_index = max(indices)
            else:
                avg_index = std_index = min_index = max_index = 0
            
            if phrase_lengths:
                avg_phrase_len = np.mean(phrase_lengths)
                std_phrase_len = np.std(phrase_lengths)
            else:
                avg_phrase_len = std_phrase_len = 0
            
            # Calculate page entropy statistics
            page_entropies = []
            for result in self.results[:min(100, len(self.results))]:  # Sample first 100 for performance
                try:
                    page = generate_page(result['seed'])
                    entropy = compute_entropy(page)
                    page_entropies.append(entropy)
                except:
                    continue
            
            if page_entropies:
                avg_entropy = np.mean(page_entropies)
                std_entropy = np.std(page_entropies)
                min_entropy = min(page_entropies)
                max_entropy = max(page_entropies)
            else:
                avg_entropy = std_entropy = min_entropy = max_entropy = 0
            
            # Format statistics
            stats_content = f"""EVOLUTION ANALYSIS SUMMARY
════════════════════════════

BASIC STATISTICS:
• Total Results: {total_results:,}
• Unique Seeds: {unique_seeds:,}
• Unique Phrases: {unique_phrases:,}
• Diversity Ratio: {(unique_seeds/total_results)*100:.1f}% (unique seeds/total results)

SEED ANALYSIS:
• Seed Entropy: {seed_entropy:.4f} bits
• Most Common Seed: {max(seed_counts.items(), key=lambda x: x[1])[0]} (appears {max(seed_counts.values())} times)
• Seed Range: {min(seeds):,} - {max(seeds):,}

INDEX POSITION STATISTICS:
• Average Index: {avg_index:.1f}
• Standard Deviation: {std_index:.1f}
• Range: {min_index} - {max_index}

PHRASE STATISTICS:
• Average Phrase Length: {avg_phrase_len:.1f} characters
• Phrase Length Std Dev: {std_phrase_len:.1f}
• Unique Phrase Ratio: {(unique_phrases/total_results)*100:.1f}%

PAGE ENTROPY ANALYSIS (sample of {len(page_entropies)} pages):
• Average Page Entropy: {avg_entropy:.4f}
• Entropy Standard Deviation: {std_entropy:.4f}
• Entropy Range: {min_entropy:.4f} - {max_entropy:.4f}

EVOLUTION METRICS:
• Search Efficiency: {(unique_seeds/total_results)*100:.1f}% (unique discoveries per search)
• Exploration Breadth: {len(set(str(r['seed'])[:3] for r in self.results))} different seed prefixes
• Temporal Diversity: {len(set(r.get('timestamp', '')[:10] for r in self.results))} different days

RECOMMENDATIONS:
"""
            
            # Add recommendations based on analysis
            if seed_entropy < 5:
                stats_content += "• Low seed entropy suggests clustering - consider broader search strategies\n"
            if unique_seeds / total_results < 0.5:
                stats_content += "• Many duplicate seeds found - evolution might be converging too quickly\n"
            if avg_entropy < 4:
                stats_content += "• Low page entropy indicates structured/repetitive content patterns\n"
            if unique_seeds / total_results > 0.9:
                stats_content += "• High diversity suggests good exploration of the search space\n"
            
            stats_text.insert("1.0", stats_content)
            stats_text.config(state=tk.DISABLED)
            
            stats_text.pack(side="left", fill="both", expand=True)
            stats_scrollbar.pack(side="right", fill="y")
            
            # Tab 3: Correlation Analysis
            corr_frame = ttk.Frame(notebook)
            notebook.add(corr_frame, text="Correlations")
            
            if len(self.results) > 10:  # Need enough data for correlations
                fig2, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
                
                # Seed vs Index correlation
                seeds_sample = seeds[:min(1000, len(seeds))]  # Sample for performance
                indices_sample = indices[:min(1000, len(indices))]
                
                if len(seeds_sample) == len(indices_sample):
                    ax1.scatter(seeds_sample, indices_sample, alpha=0.5, s=20)
                    ax1.set_title('Seed vs Index Position')
                    ax1.set_xlabel('Seed Value')
                    ax1.set_ylabel('Index Position')
                    ax1.grid(True, alpha=0.3)
                    
                    # Calculate correlation
                    correlation = np.corrcoef(seeds_sample, indices_sample)[0, 1]
                    ax1.text(0.05, 0.95, f'Correlation: {correlation:.3f}', 
                            transform=ax1.transAxes, bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
                
                # Phrase length vs Index
                if phrase_lengths and len(phrase_lengths) >= 10:
                    phrase_indices = [r.get('index', 0) for r in self.results if r.get('phrase')][:len(phrase_lengths)]
                    if len(phrase_lengths) == len(phrase_indices):
                        ax2.scatter(phrase_lengths, phrase_indices, alpha=0.5, s=20, color='green')
                        ax2.set_title('Phrase Length vs Index Position')
                        ax2.set_xlabel('Phrase Length')
                        ax2.set_ylabel('Index Position')
                        ax2.grid(True, alpha=0.3)
                        
                        correlation2 = np.corrcoef(phrase_lengths, phrase_indices)[0, 1]
                        ax2.text(0.05, 0.95, f'Correlation: {correlation2:.3f}', 
                                transform=ax2.transAxes, bbox=dict(boxstyle="round", facecolor='white', alpha=0.8))
                
                # Search order vs Seed (shows evolution pattern)
                order = list(range(len(seeds)))
                ax3.plot(order, seeds, 'o-', markersize=2, alpha=0.7, color='red')
                ax3.set_title('Seed Evolution Over Search Order')
                ax3.set_xlabel('Search Order')
                ax3.set_ylabel('Seed Value')
                ax3.grid(True, alpha=0.3)
                
                # Index evolution over time
                ax4.plot(order, indices, 'o-', markersize=2, alpha=0.7, color='orange')
                ax4.set_title('Index Position Evolution')
                ax4.set_xlabel('Search Order')
                ax4.set_ylabel('Index Position')
                ax4.grid(True, alpha=0.3)
                
                plt.tight_layout()
                
                canvas2 = FigureCanvasTkAgg(fig2, corr_frame)
                canvas2.draw()
                canvas2.get_tk_widget().pack(fill="both", expand=True)
            else:
                ttk.Label(corr_frame, text="Need at least 10 results for correlation analysis", 
                         font=("Arial", 12)).pack(expand=True)
            
            # Close button
            ttk.Button(main_frame, text="Close", command=analysis_window.destroy).pack(pady=(10, 0))
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate evolution analysis: {str(e)}")

    def show_entropy_analysis(self):
        """Show entropy analysis of selected result."""
        selection = self.results_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a result to analyze.")
            return
        
        try:
            item = self.results_tree.item(selection[0])
            values = item['values']
            if len(values) >= 3:
                seed = int(values[0])
                page_number = int(values[1])
                index = int(values[2])
                
                # Generate the page content
                page = generate_page(seed)
                
                # Calculate entropy
                entropy = compute_entropy(page)
                
                # Character frequency analysis
                char_counts = {}
                for char in page:
                    char_counts[char] = char_counts.get(char, 0) + 1
                
                # Create detailed analysis window
                analysis_window = tk.Toplevel(self.root)
                analysis_window.title(f"Entropy Analysis - Seed {seed}")
                analysis_window.geometry("800x600")
                
                # Create text widget for analysis
                text_widget = tk.Text(analysis_window, wrap=tk.WORD, padx=10, pady=10)
                text_widget.pack(fill="both", expand=True)
                
                # Display analysis
                analysis_text = f"""ENTROPY ANALYSIS
═══════════════════
Seed: {seed}
Page: {page_number}
Index: {index}
Total Entropy: {entropy:.4f}

CHARACTER FREQUENCY ANALYSIS:
"""
                
                # Sort characters by frequency
                sorted_chars = sorted(char_counts.items(), key=lambda x: x[1], reverse=True)
                for char, count in sorted_chars[:20]:  # Top 20 characters
                    char_display = repr(char) if char.isprintable() else f"'\\x{ord(char):02x}'"
                    percentage = (count / len(page)) * 100
                    analysis_text += f"{char_display}: {count} ({percentage:.2f}%)\n"
                
                analysis_text += f"\nPAGE CONTENT PREVIEW:\n{'='*50}\n{page[:500]}{'...' if len(page) > 500 else ''}"
                
                text_widget.insert("1.0", analysis_text)
                text_widget.config(state=tk.DISABLED)
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze entropy: {str(e)}")

    def show_bookmark_entropy_analysis(self):
        """Show entropy analysis of bookmarked pages."""
        if not self.bookmarks:
            messagebox.showwarning("No Bookmarks", "No bookmarks available for analysis.")
            return
        
        try:
            # Calculate entropy for all bookmarked pages
            bookmark_data = []
            for bookmark in self.bookmarks:
                seed = bookmark['seed']
                page = generate_page(seed)
                entropy = compute_entropy(page)
                bookmark_data.append({
                    'seed': seed,
                    'page': bookmark['page'],
                    'entropy': entropy,
                    'phrase': bookmark.get('phrase', 'unknown')
                })
            
            # Create analysis window
            analysis_window = tk.Toplevel(self.root)
            analysis_window.title("Bookmark Entropy Analysis")
            analysis_window.geometry("900x700")
            
            # Create notebook for tabs
            notebook = ttk.Notebook(analysis_window)
            notebook.pack(fill="both", expand=True, padx=10, pady=10)
            
            # Tab 1: Summary table
            summary_frame = ttk.Frame(notebook)
            notebook.add(summary_frame, text="Summary")
            
            # Create treeview for summary
            columns = ("Seed", "Page", "Phrase", "Entropy")
            tree = ttk.Treeview(summary_frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Sort by entropy (highest first)
            sorted_data = sorted(bookmark_data, key=lambda x: x['entropy'], reverse=True)
            
            for item in sorted_data:
                tree.insert("", "end", values=(
                    item['seed'],
                    item['page'],
                    item['phrase'][:30] + "..." if len(item['phrase']) > 30 else item['phrase'],
                    f"{item['entropy']:.4f}"
                ))
            
            tree.pack(fill="both", expand=True)
            
            # Tab 2: Visualization
            viz_frame = ttk.Frame(notebook)
            notebook.add(viz_frame, text="Visualization")
            
            # Create matplotlib plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Entropy distribution
            entropies = [item['entropy'] for item in bookmark_data]
            ax1.hist(entropies, bins=min(20, len(entropies)), alpha=0.7, color='lightcoral', edgecolor='black')
            ax1.set_title('Entropy Distribution of Bookmarked Pages')
            ax1.set_xlabel('Entropy Value')
            ax1.set_ylabel('Frequency')
            ax1.grid(True, alpha=0.3)
            
            # Entropy vs Seed
            seeds = [item['seed'] for item in bookmark_data]
            scatter = ax2.scatter(seeds, entropies, c=entropies, cmap='viridis', alpha=0.7, s=50)
            ax2.set_title('Entropy vs Seed for Bookmarked Pages')
            ax2.set_xlabel('Seed Value')
            ax2.set_ylabel('Entropy')
            ax2.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax2, label='Entropy')
            
            plt.tight_layout()
            
            # Embed plot in tkinter
            canvas = FigureCanvasTkAgg(fig, viz_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill="both", expand=True)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to analyze bookmark entropy: {str(e)}")

    def show_twin_page_dialog(self):
        """Show dialog for finding twin pages."""
        try:
            # Create twin page dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Twin Page Discovery")
            dialog.geometry("600x500")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Instructions
            instructions = ttk.Label(main_frame, 
                text="Find pages with identical content but different seeds:",
                font=("Arial", 12, "bold"))
            instructions.pack(pady=(0, 10))
            
            # Options frame
            options_frame = ttk.LabelFrame(main_frame, text="Search Options", padding="10")
            options_frame.pack(fill="x", pady=(0, 10))
            
            # Sample size
            ttk.Label(options_frame, text="Sample size:").pack(anchor="w")
            sample_var = tk.IntVar(value=1000)
            sample_spin = ttk.Spinbox(options_frame, from_=100, to=10000, textvariable=sample_var, width=10)
            sample_spin.pack(anchor="w", pady=(0, 10))
            
            # Minimum matches
            ttk.Label(options_frame, text="Minimum twin groups:").pack(anchor="w")
            min_matches_var = tk.IntVar(value=2)
            min_spin = ttk.Spinbox(options_frame, from_=2, to=20, textvariable=min_matches_var, width=10)
            min_spin.pack(anchor="w")
            
            # Results frame
            results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
            results_frame.pack(fill="both", expand=True, pady=(10, 0))
            
            # Results treeview
            columns = ("Group", "Seeds", "Page Preview")
            tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == "Page Preview":
                    tree.column(col, width=300)
                else:
                    tree.column(col, width=100)
            
            scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
            tree.configure(yscrollcommand=scrollbar.set)
            
            tree.pack(side="left", fill="both", expand=True)
            scrollbar.pack(side="right", fill="y")
            
            # Status label
            status_label = ttk.Label(results_frame, text="Click 'Find Twin Pages' to start search")
            status_label.pack(pady=(10, 0))
            
            # Progress bar
            progress = ttk.Progressbar(results_frame, mode='indeterminate')
            progress.pack(fill="x", pady=(5, 0))
            
            def find_twins():
                """Find twin pages in a separate thread."""
                def search_twins():
                    try:
                        progress.start()
                        status_label.config(text="Searching for twin pages...")
                        dialog.update()
                        
                        sample_size = sample_var.get()
                        min_matches = min_matches_var.get()
                        
                        # Generate random seeds and compute page hashes
                        page_hashes = {}
                        seeds_checked = 0
                        
                        for _ in range(sample_size):
                            seed = random.randint(1, 2**31 - 1)
                            page = generate_page(seed)
                            page_hash = hash(page)
                            
                            if page_hash not in page_hashes:
                                page_hashes[page_hash] = []
                            page_hashes[page_hash].append((seed, page))
                            
                            seeds_checked += 1
                            if seeds_checked % 100 == 0:
                                status_label.config(text=f"Checked {seeds_checked}/{sample_size} seeds...")
                                dialog.update()
                        
                        # Find groups with multiple seeds (twins)
                        twin_groups = []
                        group_num = 1
                        
                        for page_hash, seed_page_pairs in page_hashes.items():
                            if len(seed_page_pairs) >= min_matches:
                                seeds = [pair[0] for pair in seed_page_pairs]
                                page_preview = seed_page_pairs[0][1][:100] + "..."
                                twin_groups.append((group_num, seeds, page_preview))
                                group_num += 1
                        
                        # Display results
                        for item in tree.get_children():
                            tree.delete(item)
                        
                        for group_num, seeds, preview in twin_groups:
                            seeds_str = ", ".join(map(str, seeds[:5]))  # Show first 5 seeds
                            if len(seeds) > 5:
                                seeds_str += f" (+{len(seeds)-5} more)"
                            
                            tree.insert("", "end", values=(
                                f"Group {group_num}",
                                seeds_str,
                                preview
                            ))
                        
                        progress.stop()
                        status_label.config(text=f"Found {len(twin_groups)} twin page groups")
                        
                        if not twin_groups:
                            messagebox.showinfo("No Twins Found", 
                                f"No twin pages found in {sample_size} samples. Try increasing sample size.")
                        
                    except Exception as e:
                        progress.stop()
                        status_label.config(text="Error occurred during search")
                        messagebox.showerror("Error", f"Twin page search failed: {str(e)}")
                
                # Run in thread to prevent GUI freezing
                import threading
                thread = threading.Thread(target=search_twins)
                thread.daemon = True
                thread.start()
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=(10, 0))
            
            ttk.Button(buttons_frame, text="Find Twin Pages", command=find_twins).pack(side="left")
            ttk.Button(buttons_frame, text="Close", command=dialog.destroy).pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create twin page dialog: {str(e)}")

    def load_background_results(self):
        """Load background search results."""
        try:
            if not os.path.exists(BACKGROUND_RESULTS_FILE):
                messagebox.showinfo("No Results", "No background results file found.")
                return
            
            with open(BACKGROUND_RESULTS_FILE, 'r', encoding='utf-8') as f:
                bg_results = json.load(f)
            
            if not bg_results:
                messagebox.showinfo("No Results", "Background results file is empty.")
                return
            
            # Create results window
            results_window = tk.Toplevel(self.root)
            results_window.title("Background Search Results")
            results_window.geometry("1000x700")
            
            # Main frame
            main_frame = ttk.Frame(results_window, padding="10")
            main_frame.pack(fill="both", expand=True)
            
            # Info frame
            info_frame = ttk.Frame(main_frame)
            info_frame.pack(fill="x", pady=(0, 10))
            
            ttk.Label(info_frame, text=f"Total background results: {len(bg_results)}", 
                     font=("Arial", 12, "bold")).pack(anchor="w")
            
            # Results frame with treeview
            results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
            results_frame.pack(fill="both", expand=True)
            
            columns = ("Seed", "Page", "Index", "Phrase", "Timestamp")
            tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=20)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == "Phrase":
                    tree.column(col, width=300)
                elif col == "Timestamp":
                    tree.column(col, width=150)
                else:
                    tree.column(col, width=100)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            # Pack treeview and scrollbars
            tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            results_frame.grid_rowconfigure(0, weight=1)
            results_frame.grid_columnconfigure(0, weight=1)
            
            # Load results into tree
            for result in bg_results:
                timestamp = result.get('timestamp', 'Unknown')
                if timestamp != 'Unknown':
                    try:
                        # Format timestamp
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
                
                tree.insert("", "end", values=(
                    result.get('seed', 'N/A'),
                    result.get('page', 'N/A'),
                    result.get('index', 'N/A'),
                    result.get('phrase', 'N/A')[:50] + ('...' if len(str(result.get('phrase', ''))) > 50 else ''),
                    timestamp
                ))
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x", pady=(10, 0))
            
            def import_selected():
                """Import selected results to main results."""
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select results to import.")
                    return
                
                imported_count = 0
                for item_id in selection:
                    item = tree.item(item_id)
                    values = item['values']
                    
                    try:
                        result = {
                            'seed': int(values[0]),
                            'page': int(values[1]),
                            'index': int(values[2]),
                            'phrase': values[3].replace('...', ''),  # Remove truncation
                            'timestamp': values[4]
                        }
                        
                        # Find full phrase in bg_results
                        for bg_result in bg_results:
                            if (bg_result.get('seed') == result['seed'] and 
                                bg_result.get('page') == result['page'] and
                                bg_result.get('index') == result['index']):
                                result['phrase'] = bg_result.get('phrase', result['phrase'])
                                break
                        
                        # Check for duplicates
                        if not is_duplicate(result, self.results):
                            self.results.append(result)
                            imported_count += 1
                    except ValueError:
                        continue
                
                if imported_count > 0:
                    self.refresh_results_display()
                    messagebox.showinfo("Success", f"Imported {imported_count} results.")
                else:
                    messagebox.showinfo("No Import", "No new results imported (duplicates or errors).")
            
            def clear_background():
                """Clear background results file."""
                if messagebox.askyesno("Confirm", "Clear all background results? This cannot be undone."):
                    try:
                        with open(BACKGROUND_RESULTS_FILE, 'w') as f:
                            json.dump([], f)
                        messagebox.showinfo("Success", "Background results cleared.")
                        results_window.destroy()
                    except Exception as e:
                        messagebox.showerror("Error", f"Failed to clear results: {str(e)}")
            
            ttk.Button(buttons_frame, text="Import Selected", command=import_selected).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Clear All Background Results", command=clear_background).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Close", command=results_window.destroy).pack(side="right")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load background results: {str(e)}")

    def jump_to_seed_dialog(self):
        """Show dialog to jump to a specific seed."""
        try:
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Jump to Seed")
            dialog.geometry("500x300")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Jump to Specific Seed", 
                                  font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Seed input frame
            input_frame = ttk.LabelFrame(main_frame, text="Seed Information", padding="10")
            input_frame.pack(fill="x", pady=(0, 20))
            
            # Seed entry
            ttk.Label(input_frame, text="Seed:").pack(anchor="w")
            seed_var = tk.StringVar()
            seed_entry = ttk.Entry(input_frame, textvariable=seed_var, width=30)
            seed_entry.pack(anchor="w", pady=(0, 10))
            seed_entry.focus()
            
            # Page entry
            ttk.Label(input_frame, text="Page (optional):").pack(anchor="w")
            page_var = tk.StringVar(value="1")
            page_entry = ttk.Entry(input_frame, textvariable=page_var, width=30)
            page_entry.pack(anchor="w")
            
            # Preview frame
            preview_frame = ttk.LabelFrame(main_frame, text="Page Preview", padding="10")
            preview_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Preview text
            preview_text = tk.Text(preview_frame, height=8, wrap=tk.WORD, state=tk.DISABLED)
            preview_scrollbar = ttk.Scrollbar(preview_frame, orient="vertical", command=preview_text.yview)
            preview_text.configure(yscrollcommand=preview_scrollbar.set)
            
            preview_text.pack(side="left", fill="both", expand=True)
            preview_scrollbar.pack(side="right", fill="y")
            
            def preview_page():
                """Preview the page content."""
                try:
                    seed_str = seed_var.get().strip()
                    if not seed_str:
                        return
                    
                    seed = int(seed_str)
                    page_content = generate_page(seed)
                    
                    # Update preview
                    preview_text.config(state=tk.NORMAL)
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert("1.0", page_content[:1000] + "..." if len(page_content) > 1000 else page_content)
                    preview_text.config(state=tk.DISABLED)
                    
                except ValueError:
                    preview_text.config(state=tk.NORMAL)
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert("1.0", "Invalid seed number")
                    preview_text.config(state=tk.DISABLED)
                except Exception as e:
                    preview_text.config(state=tk.NORMAL)
                    preview_text.delete("1.0", tk.END)
                    preview_text.insert("1.0", f"Error: {str(e)}")
                    preview_text.config(state=tk.DISABLED)
            
            def jump_to_seed():
                """Jump to the specified seed."""
                try:
                    seed_str = seed_var.get().strip()
                    page_str = page_var.get().strip()
                    
                    if not seed_str:
                        messagebox.showwarning("Missing Input", "Please enter a seed number.")
                        return
                    
                    seed = int(seed_str)
                    page = int(page_str) if page_str else 1
                    
                    # Generate the page
                    page_content = generate_page(seed)
                    
                    # Create result entry
                    result = {
                        'seed': seed,
                        'page': page,
                        'index': 0,  # Start of page
                        'phrase': f"[Manual Jump to Seed {seed}]",
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    # Add to results if not duplicate
                    if not is_duplicate(result, self.results):
                        self.results.append(result)
                        self.refresh_results_display()
                    
                    # Update the main display
                    self.page_var.set(page)
                    self.index_var.set(0)
                    self.update_page_display()
                    
                    # Show success message
                    messagebox.showinfo("Success", f"Jumped to seed {seed}, page {page}")
                    dialog.destroy()
                    
                except ValueError:
                    messagebox.showerror("Invalid Input", "Please enter valid numbers for seed and page.")
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to jump to seed: {str(e)}")
            
            # Bind preview update to seed changes
            seed_var.trace('w', lambda *args: preview_page())
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x")
            
            ttk.Button(buttons_frame, text="Jump to Seed", command=jump_to_seed).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Preview", command=preview_page).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Cancel", command=dialog.destroy).pack(side="right")
            
            # Bind Enter key to jump
            dialog.bind('<Return>', lambda e: jump_to_seed())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create jump dialog: {str(e)}")

    def show_seed_reverse_lookup(self):
        """Show seed reverse lookup dialog."""
        try:
            # Create dialog
            dialog = tk.Toplevel(self.root)
            dialog.title("Seed Reverse Lookup")
            dialog.geometry("700x600")
            dialog.transient(self.root)
            dialog.grab_set()
            
            # Main frame
            main_frame = ttk.Frame(dialog, padding="20")
            main_frame.pack(fill="both", expand=True)
            
            # Title
            title_label = ttk.Label(main_frame, text="Seed Reverse Lookup", 
                                  font=("Arial", 14, "bold"))
            title_label.pack(pady=(0, 20))
            
            # Description
            desc_label = ttk.Label(main_frame, 
                text="Enter text content to find seeds that generate pages containing this text:",
                wraplength=600)
            desc_label.pack(pady=(0, 10))
            
            # Input frame
            input_frame = ttk.LabelFrame(main_frame, text="Search Parameters", padding="10")
            input_frame.pack(fill="x", pady=(0, 20))
            
            # Text input
            ttk.Label(input_frame, text="Text to find:").pack(anchor="w")
            text_var = tk.StringVar()
            text_entry = ttk.Entry(input_frame, textvariable=text_var, width=60)
            text_entry.pack(anchor="w", pady=(0, 10))
            text_entry.focus()
            
            # Search options
            options_frame = ttk.Frame(input_frame)
            options_frame.pack(fill="x", pady=(0, 10))
            
            ttk.Label(options_frame, text="Max seeds to check:").pack(side="left")
            max_seeds_var = tk.IntVar(value=10000)
            max_seeds_spin = ttk.Spinbox(options_frame, from_=1000, to=100000, 
                                       textvariable=max_seeds_var, width=10)
            max_seeds_spin.pack(side="left", padx=(5, 20))
            
            ttk.Label(options_frame, text="Max results:").pack(side="left")
            max_results_var = tk.IntVar(value=50)
            max_results_spin = ttk.Spinbox(options_frame, from_=10, to=1000, 
                                         textvariable=max_results_var, width=10)
            max_results_spin.pack(side="left", padx=(5, 0))
            
            # Results frame
            results_frame = ttk.LabelFrame(main_frame, text="Results", padding="10")
            results_frame.pack(fill="both", expand=True, pady=(0, 20))
            
            # Results treeview
            columns = ("Seed", "Page", "Index", "Context")
            tree = ttk.Treeview(results_frame, columns=columns, show="headings", height=15)
            
            for col in columns:
                tree.heading(col, text=col)
                if col == "Context":
                    tree.column(col, width=400)
                else:
                    tree.column(col, width=80)
            
            # Scrollbars
            v_scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=tree.yview)
            h_scrollbar = ttk.Scrollbar(results_frame, orient="horizontal", command=tree.xview)
            tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
            
            tree.grid(row=0, column=0, sticky="nsew")
            v_scrollbar.grid(row=0, column=1, sticky="ns")
            h_scrollbar.grid(row=1, column=0, sticky="ew")
            
            results_frame.grid_rowconfigure(0, weight=1)
            results_frame.grid_columnconfigure(0, weight=1)
            
            # Status label
            status_label = ttk.Label(results_frame, text="Enter text and click 'Search' to begin")
            status_label.grid(row=2, column=0, columnspan=2, pady=(10, 0))
            
            # Progress bar
            progress = ttk.Progressbar(results_frame, mode='determinate')
            progress.grid(row=3, column=0, columnspan=2, sticky="ew", pady=(5, 0))
            
            def search_seeds():
                """Search for seeds containing the text."""
                search_text = text_var.get().strip()
                if not search_text:
                    messagebox.showwarning("Missing Input", "Please enter text to search for.")
                    return
                
                if not validate_phrase(search_text):
                    messagebox.showerror("Invalid Text", "Text contains invalid characters.")
                    return
                
                # Clear previous results
                for item in tree.get_children():
                    tree.delete(item)
                
                max_seeds = max_seeds_var.get()
                max_results = max_results_var.get()
                
                def search_thread():
                    try:
                        found_results = []
                        seeds_checked = 0
                        
                        progress.configure(mode='determinate', maximum=max_seeds)
                        
                        for _ in range(max_seeds):
                            if len(found_results) >= max_results:
                                break
                            
                            seed = random.randint(1, 2**31 - 1)
                            page = generate_page(seed)
                            
                            # Search for text in page
                            index = page.find(search_text)
                            if index != -1:
                                # Found the text, create context
                                context_start = max(0, index - 30)
                                context_end = min(len(page), index + len(search_text) + 30)
                                context = page[context_start:context_end]
                                
                                # Highlight the found text
                                highlighted_context = context.replace(search_text, f"[{search_text}]")
                                
                                found_results.append({
                                    'seed': seed,
                                    'page': 1,  # Assuming page 1 for now
                                    'index': index,
                                    'context': highlighted_context
                                })
                                
                                # Update tree in main thread
                                dialog.after(0, lambda r=found_results[-1]: tree.insert("", "end", values=(
                                    r['seed'], r['page'], r['index'], r['context']
                                )))
                            
                            seeds_checked += 1
                            
                            # Update progress
                            if seeds_checked % 100 == 0:
                                progress_value = seeds_checked
                                status_text = f"Checked {seeds_checked}/{max_seeds} seeds, found {len(found_results)} matches"
                                dialog.after(0, lambda: (
                                    progress.configure(value=progress_value),
                                    status_label.config(text=status_text)
                                ))
                        
                        # Final update
                        dialog.after(0, lambda: (
                            progress.configure(value=max_seeds),
                            status_label.config(text=f"Search complete: {len(found_results)} matches found")
                        ))
                        
                        if not found_results:
                            dialog.after(0, lambda: messagebox.showinfo("No Results", 
                                f"No seeds found containing '{search_text}' in {max_seeds} seeds checked."))
                        
                    except Exception as e:
                        dialog.after(0, lambda: (
                            status_label.config(text="Search failed"),
                            messagebox.showerror("Error", f"Search failed: {str(e)}")
                        ))
                
                # Start search in separate thread
                thread = threading.Thread(target=search_thread)
                thread.daemon = True
                thread.start()
            
            def import_selected():
                """Import selected results to main results."""
                selection = tree.selection()
                if not selection:
                    messagebox.showwarning("No Selection", "Please select results to import.")
                    return
                
                search_text = text_var.get().strip()
                imported_count = 0
                
                for item_id in selection:
                    item = tree.item(item_id)
                    values = item['values']
                    
                    try:
                        result = {
                            'seed': int(values[0]),
                            'page': int(values[1]),
                            'index': int(values[2]),
                            'phrase': search_text,
                            'timestamp': datetime.now().isoformat()
                        }
                        
                        if not is_duplicate(result, self.results):
                            self.results.append(result)
                            imported_count += 1
                    except ValueError:
                        continue
                
                if imported_count > 0:
                    self.refresh_results_display()
                    messagebox.showinfo("Success", f"Imported {imported_count} results.")
                else:
                    messagebox.showinfo("No Import", "No new results imported.")
            
            # Buttons frame
            buttons_frame = ttk.Frame(main_frame)
            buttons_frame.pack(fill="x")
            
            ttk.Button(buttons_frame, text="Search", command=search_seeds).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Import Selected", command=import_selected).pack(side="left", padx=(0, 10))
            ttk.Button(buttons_frame, text="Close", command=dialog.destroy).pack(side="right")
            
            # Bind Enter key to search
            dialog.bind('<Return>', lambda e: search_seeds())
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to create reverse lookup dialog: {str(e)}")

    def show_entropy_map(self):
        """Show entropy map visualization."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results to analyze. Please perform some searches first.")
            return
        
        try:
            seeds = []
            entropies = []
            
            # Calculate entropy for each result
            for result in self.results:
                seed = result['seed']
                page = generate_page(seed)
                entropy = compute_entropy(page)
                seeds.append(seed)
                entropies.append(entropy)
            
            # Create the plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Entropy vs Seed scatter plot
            scatter = ax1.scatter(seeds, entropies, c=entropies, cmap='viridis', alpha=0.7)
            ax1.set_title('Page Entropy by Seed')
            ax1.set_xlabel('Seed Value')
            ax1.set_ylabel('Entropy')
            ax1.grid(True, alpha=0.3)
            plt.colorbar(scatter, ax=ax1, label='Entropy')
            
            # Entropy distribution histogram
            ax2.hist(entropies, bins=20, alpha=0.7, color='lightblue', edgecolor='black')
            ax2.set_title('Entropy Distribution')
            ax2.set_xlabel('Entropy Value')
            ax2.set_ylabel('Frequency')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Display in analytics tab
            self._show_matplotlib_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate entropy map: {str(e)}")

    def show_seed_distribution(self):
        """Show seed distribution analysis with real matplotlib visualization."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results to analyze. Please perform some searches first.")
            return
        
        try:
            # Extract seeds from results
            seeds = [result['seed'] for result in self.results]
            
            # Create the plot
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
            
            # Histogram of seed distribution
            ax1.hist(seeds, bins=min(50, len(seeds)), alpha=0.7, color='skyblue', edgecolor='black')
            ax1.set_title('Distribution of Found Seeds')
            ax1.set_xlabel('Seed Value')
            ax1.set_ylabel('Frequency')
            ax1.grid(True, alpha=0.3)
            
            # Seed value over time (order found)
            ax2.plot(range(len(seeds)), seeds, 'o-', color='coral', markersize=4)
            ax2.set_title('Seeds Found Over Time')
            ax2.set_xlabel('Search Order')
            ax2.set_ylabel('Seed Value')
            ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            # Display in analytics tab
            self._show_matplotlib_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate seed distribution: {str(e)}")

    def show_phrase_frequency(self):
        """Show phrase frequency analysis with real visualization."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results to analyze. Please perform some searches first.")
            return
        
        try:
            # Count phrase frequencies
            phrase_counts = {}
            for result in self.results:
                phrase = result.get('phrase', 'unknown')
                phrase_counts[phrase] = phrase_counts.get(phrase, 0) + 1
            
            if not phrase_counts:
                messagebox.showinfo("No Data", "No phrases found in results.")
                return
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            phrases = list(phrase_counts.keys())
            counts = list(phrase_counts.values())
            
            bars = ax.bar(range(len(phrases)), counts, color='lightgreen', edgecolor='darkgreen')
            ax.set_title('Phrase Search Frequency')
            ax.set_xlabel('Phrases')
            ax.set_ylabel('Number of Matches Found')
            ax.set_xticks(range(len(phrases)))
            ax.set_xticklabels([p[:20] + '...' if len(p) > 20 else p for p in phrases], rotation=45, ha='right')
            
            # Add value labels on bars
            for bar, count in zip(bars, counts):
                ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1, 
                       str(count), ha='center', va='bottom')
            
            plt.tight_layout()
            
            # Display in analytics tab
            self._show_matplotlib_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate phrase frequency: {str(e)}")

    def show_timeline(self):
        """Show timeline analysis of searches."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results to analyze. Please perform some searches first.")
            return
        
        try:
            # Extract timestamps (if available)
            timestamps = []
            phrases = []
            
            for result in self.results:
                if 'timestamp' in result:
                    try:
                        # Try to parse timestamp
                        ts = datetime.fromisoformat(result['timestamp'].replace('Z', '+00:00'))
                        timestamps.append(ts)
                        phrases.append(result.get('phrase', 'unknown'))
                    except:
                        continue
            
            if not timestamps:
                messagebox.showinfo("No Data", "No timestamp data available for timeline analysis.")
                return
            
            # Create the plot
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Plot timeline
            colors = plt.cm.Set3(np.linspace(0, 1, len(set(phrases))))
            phrase_colors = {phrase: color for phrase, color in zip(set(phrases), colors)}
            
            for i, (ts, phrase) in enumerate(zip(timestamps, phrases)):
                ax.scatter(ts, i, c=[phrase_colors[phrase]], s=50, alpha=0.7)
            
            ax.set_title('Search Timeline')
            ax.set_xlabel('Time')
            ax.set_ylabel('Search Number')
            ax.grid(True, alpha=0.3)
            
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            # Display in analytics tab
            self._show_matplotlib_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate timeline: {str(e)}")

    def show_match_density_heatmap(self):
        """Show match density heatmap."""
        if not self.results:
            messagebox.showwarning("No Data", "No search results to analyze. Please perform some searches first.")
            return
        
        try:
            # Extract seed and index data
            seeds = [result['seed'] for result in self.results]
            indices = [result['index'] for result in self.results]
            
            if len(seeds) < 4:
                messagebox.showinfo("Insufficient Data", "Need at least 4 results for heatmap analysis.")
                return
            
            # Create 2D histogram
            fig, ax = plt.subplots(figsize=(10, 8))
            
            # Create heatmap
            heatmap, xedges, yedges = np.histogram2d(seeds, indices, bins=20)
            extent = [xedges[0], xedges[-1], yedges[0], yedges[-1]]
            
            im = ax.imshow(heatmap.T, origin='lower', extent=extent, cmap='YlOrRd', aspect='auto')
            
            ax.set_title('Match Density Heatmap')
            ax.set_xlabel('Seed Value')
            ax.set_ylabel('Index Position')
            
            # Add colorbar
            plt.colorbar(im, ax=ax, label='Match Density')
            
            plt.tight_layout()
            
            # Display in analytics tab
            self._show_matplotlib_plot(fig)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate heatmap: {str(e)}")

    def _show_matplotlib_plot(self, fig):
        """Display matplotlib plot in the analytics tab."""
        try:
            # Clear previous plot if exists
            if hasattr(self, 'analytics_canvas') and self.analytics_canvas:
                self.analytics_canvas.get_tk_widget().destroy()
            
            # Create canvas for the plot
            self.analytics_canvas = FigureCanvasTkAgg(fig, self.analytics_tab)
            self.analytics_canvas.draw()
            self.analytics_canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to display plot: {str(e)}")
            plt.close(fig)  # Clean up if display fails

    def save_session(self):
        """Save current session."""
        try:
            filename = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Session"
            )
            
            if filename:
                session_data = {
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results,
                    'bookmarks': self.bookmarks,
                    'current_phrase': self.phrase_var.get(),
                    'current_page': self.page_var.get(),
                    'current_index': self.index_var.get(),
                    'search_mode': self.search_mode_var.get(),
                    'stats': {
                        'total_searches': len(self.results),
                        'total_bookmarks': len(self.bookmarks),
                        'unique_phrases': len(set(r.get('phrase', '') for r in self.results)),
                        'unique_seeds': len(set(r.get('seed', 0) for r in self.results))
                    }
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(session_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Success", f"Session saved to {filename}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save session: {str(e)}")

    def load_session(self):
        """Load a saved session.""" 
        try:
            filename = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Session"
            )
            
            if filename:
                with open(filename, 'r', encoding='utf-8') as f:
                    session_data = json.load(f)
                
                # Restore session data
                self.results = session_data.get('results', [])
                self.bookmarks = session_data.get('bookmarks', [])
                
                # Restore UI state
                if 'current_phrase' in session_data:
                    self.phrase_var.set(session_data['current_phrase'])
                if 'current_page' in session_data:
                    self.page_var.set(session_data['current_page'])
                if 'current_index' in session_data:
                    self.index_var.set(session_data['current_index'])
                if 'search_mode' in session_data:
                    self.search_mode_var.set(session_data['search_mode'])
                
                # Refresh UI
                self.refresh_results_display()
                self.refresh_bookmarks_display()
                
                # Show stats
                stats = session_data.get('stats', {})
                timestamp = session_data.get('timestamp', 'Unknown')
                
                messagebox.showinfo("Session Loaded", 
                    f"Session loaded successfully!\n\n"
                    f"Saved: {timestamp}\n"
                    f"Results: {stats.get('total_searches', 0)}\n"
                    f"Bookmarks: {stats.get('total_bookmarks', 0)}\n"
                    f"Unique phrases: {stats.get('unique_phrases', 0)}\n"
                    f"Unique seeds: {stats.get('unique_seeds', 0)}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load session: {str(e)}")

    def remove_selected_bookmark(self):
        """Remove selected bookmark."""
        selection = self.bookmarks_tree.selection()
        if not selection:
            messagebox.showwarning("No Selection", "Please select a bookmark to remove.")
            return
        
        try:
            # Get selected item info
            item = self.bookmarks_tree.item(selection[0])
            values = item['values']
            
            if len(values) >= 2:
                seed = int(values[0])
                page_number = int(values[1])
                
                # Find and remove the bookmark
                for i, bookmark in enumerate(self.bookmarks):
                    if bookmark['seed'] == seed and bookmark['page'] == page_number:
                        removed_bookmark = self.bookmarks.pop(i)
                        break
                else:
                    messagebox.showwarning("Not Found", "Bookmark not found in list.")
                    return
                
                # Refresh the display
                self.refresh_bookmarks_display()
                
                # Save updated bookmarks
                self.save_bookmarks()
                
                messagebox.showinfo("Success", 
                    f"Removed bookmark: Seed {seed}, Page {page_number}")
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to remove bookmark: {str(e)}")

    # ...existing code...