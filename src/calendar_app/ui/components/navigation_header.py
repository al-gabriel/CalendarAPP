"""
Navigation Header Component

Reusable header component with navigation controls and date selection.
Used across different calendar views (month, year, day, stats).
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import date
from typing import Optional, Callable


class NavigationHeader:
    """
    Reusable navigation header component for calendar views.
    
    Provides:
    - Jump buttons (First Entry, Target Date)
    - Month/Year dropdowns
    - Navigation arrows (prev/next month/year)
    - Configurable callbacks for all actions
    """
    
    def __init__(self, parent: tk.Widget, config=None, timeline=None):
        """
        Initialize navigation header.
        
        Args:
            parent: Parent widget to contain the header
            config: AppConfig instance for date ranges and special dates
            timeline: DateTimeline instance (for future use)
        """
        self.parent = parent
        self.config = config
        self.timeline = timeline
        
        # Set date range from config
        if config:
            self.min_year = config.start_year
            self.max_year = config.end_year
        else:
            self.min_year = 2023
            self.max_year = 2040
        
        # Current date state
        self.current_date = date.today()
        
        # Callback functions (to be set by parent view)
        self.on_date_changed: Optional[Callable] = None
        self.on_first_entry_clicked: Optional[Callable] = None
        self.on_target_date_clicked: Optional[Callable] = None
        self.on_prev_month: Optional[Callable] = None
        self.on_next_month: Optional[Callable] = None
        self.on_prev_year: Optional[Callable] = None
        self.on_next_year: Optional[Callable] = None
        
        # UI components
        self.header_frame = None
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.month_dropdown = None
        self.year_dropdown = None
        
        # Navigation buttons
        self.jump_to_first_entry_button = None
        self.jump_to_objective_button = None
        self.prev_year_button = None
        self.prev_month_button = None
        self.next_month_button = None
        self.next_year_button = None
        
        self.create_header()
    
    def create_header(self):
        """Create the complete navigation header UI."""
        self.header_frame = tk.Frame(self.parent, bg="white")
        self.header_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Configure grid columns: side columns max 15% each, center takes remaining 70%
        self.header_frame.columnconfigure(0, weight=1, uniform="side")  # Left: ◀ First Entry - max 15%
        self.header_frame.columnconfigure(1, weight=7)                  # Center: dropdowns - 70%
        self.header_frame.columnconfigure(2, weight=1, uniform="side")  # Right: Target Date ▶ - max 15%
        
        # Configure grid rows: dynamic height based on content
        self.header_frame.rowconfigure(0, weight=0)  # Row 0: auto-size to content
        self.header_frame.rowconfigure(1, weight=0)  # Row 1: auto-size to content
        
        self.create_row_0()  # Jump buttons and date selectors
        self.create_row_1()  # Navigation arrows
        
        # Initialize display
        self.update_display()
    
    def create_row_0(self):
        """Create top row: jump buttons and month/year dropdowns."""
        # Cell 0,0: First Entry button
        self.jump_to_first_entry_button = tk.Button(
            self.header_frame,
            text="◀ First Entry",
            command=self._on_first_entry_clicked,
            bg="#28a745",
            fg="white",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            height=1
        )
        self.jump_to_first_entry_button.grid(row=0, column=0, sticky="ew", padx=2, pady=[1,0])
        
        # Cell 0,1: Month and Year dropdowns (centered)
        center_frame = tk.Frame(self.header_frame, bg="white")
        center_frame.grid(row=0, column=1, padx=10, pady=[1,0])
        
        center_content = tk.Frame(center_frame, bg="white")
        center_content.pack(expand=True)
        
        # Month dropdown
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        self.month_dropdown = ttk.Combobox(
            center_content,
            textvariable=self.month_var,
            values=month_names,
            state="readonly",
            font=("Arial", 10, "bold"),
            width=12
        )
        self.month_dropdown.pack(side=tk.LEFT, padx=5)
        self.month_dropdown.bind("<<ComboboxSelected>>", self._on_month_changed)
        
        # Year dropdown
        years = list(range(self.min_year, self.max_year + 1))
        self.year_dropdown = ttk.Combobox(
            center_content,
            textvariable=self.year_var,
            values=years,
            state="readonly",
            font=("Arial", 10, "bold"),
            width=6
        )
        self.year_dropdown.pack(side=tk.LEFT, padx=5)
        self.year_dropdown.bind("<<ComboboxSelected>>", self._on_year_changed)
        
        # Cell 0,2: Target Date button
        self.jump_to_objective_button = tk.Button(
            self.header_frame,
            text="Target Date ▶",
            command=self._on_target_date_clicked,
            bg="#ffd700",
            fg="black",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            height=1
        )
        self.jump_to_objective_button.grid(row=0, column=2, sticky="ew", padx=2, pady=[1,0])
    
    def create_row_1(self):
        """Create bottom row: navigation arrow buttons."""
        # Cell 1,0: Previous navigation
        left_nav = tk.Frame(self.header_frame, bg="white")
        left_nav.grid(row=1, column=0, sticky="ew", padx=2, pady=[1,1])
        
        self.prev_year_button = tk.Button(
            left_nav,
            text="◀◀",
            command=self._on_prev_year,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.prev_year_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        
        self.prev_month_button = tk.Button(
            left_nav,
            text="◀",
            command=self._on_prev_month,
            bg="#4dabf7",
            fg="white",
            font=("Arial", 8),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.prev_month_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=1)
        
        # Cell 1,1: Empty (center space)
        # Cell 1,2: Next navigation
        right_nav = tk.Frame(self.header_frame, bg="white")
        right_nav.grid(row=1, column=2, sticky="ew", padx=2, pady=[1,1])
        
        self.next_month_button = tk.Button(
            right_nav,
            text="▶",
            command=self._on_next_month,
            bg="#4dabf7",
            fg="white",
            font=("Arial", 8),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.next_month_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=1)
        
        self.next_year_button = tk.Button(
            right_nav,
            text="▶▶",
            command=self._on_next_year,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.next_year_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=1)
    
    def set_current_date(self, new_date: date):
        """Update the current date and refresh display."""
        if self.min_year <= new_date.year <= self.max_year:
            self.current_date = new_date
            self.update_display()
    
    def get_current_date(self) -> date:
        """Get the current date."""
        return self.current_date
    
    def update_display(self):
        """Update dropdown values and button states."""
        # Update dropdown displays
        self.month_var.set(calendar.month_name[self.current_date.month])
        self.year_var.set(str(self.current_date.year))
        
        # Update navigation button states
        self.update_button_states()
    
    def update_button_states(self):
        """Enable/disable navigation buttons based on date range limits."""
        year = self.current_date.year
        month = self.current_date.month
        
        # Check limits
        at_min_date = (year == self.min_year and month == 1)
        at_min_year = (year == self.min_year)
        at_max_date = (year == self.max_year and month == 12)
        at_max_year = (year == self.max_year)
        
        # Update button states
        self.prev_month_button.config(state="disabled" if at_min_date else "normal")
        self.prev_year_button.config(state="disabled" if at_min_year else "normal")
        self.next_month_button.config(state="disabled" if at_max_date else "normal")
        self.next_year_button.config(state="disabled" if at_max_year else "normal")
    
    # Internal event handlers (call parent callbacks)
    def _on_month_changed(self, event=None):
        """Handle month dropdown change."""
        selected_month_name = self.month_var.get()
        for i in range(1, 13):
            if calendar.month_name[i] == selected_month_name:
                new_date = date(self.current_date.year, i, 1)
                self.set_current_date(new_date)
                if self.on_date_changed:
                    self.on_date_changed(new_date)
                break
    
    def _on_year_changed(self, event=None):
        """Handle year dropdown change."""
        try:
            new_year = int(self.year_var.get())
            if self.min_year <= new_year <= self.max_year:
                new_date = date(new_year, self.current_date.month, 1)
                self.set_current_date(new_date)
                if self.on_date_changed:
                    self.on_date_changed(new_date)
        except ValueError:
            pass
    
    def _on_first_entry_clicked(self):
        """Handle first entry button click."""
        if self.on_first_entry_clicked:
            self.on_first_entry_clicked()
    
    def _on_target_date_clicked(self):
        """Handle target date button click."""
        if self.on_target_date_clicked:
            self.on_target_date_clicked()
    
    def _on_prev_month(self):
        """Handle previous month button."""
        if self.on_prev_month:
            self.on_prev_month()
    
    def _on_next_month(self):
        """Handle next month button."""
        if self.on_next_month:
            self.on_next_month()
    
    def _on_prev_year(self):
        """Handle previous year button."""
        if self.on_prev_year:
            self.on_prev_year()
    
    def _on_next_year(self):
        """Handle next year button."""
        if self.on_next_year:
            self.on_next_year()
    
    # Callback setters (used by parent views)
    def set_callbacks(self, **callbacks):
        """
        Set callback functions for navigation events.
        
        Available callbacks:
        - on_date_changed: Called when month/year selection changes
        - on_first_entry_clicked: Called when First Entry button clicked  
        - on_target_date_clicked: Called when Target Date button clicked
        - on_prev_month, on_next_month: Month navigation
        - on_prev_year, on_next_year: Year navigation
        """
        for name, callback in callbacks.items():
            if hasattr(self, name):
                setattr(self, name, callback)