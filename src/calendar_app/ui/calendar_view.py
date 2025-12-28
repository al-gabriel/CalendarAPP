"""
Calendar View Module

Handles the main calendar display with month grid and navigation.
Shows dates in a traditional calendar layout with Previous/Next controls.
"""

import tkinter as tk
from tkinter import ttk
import calendar
from datetime import datetime, date
from typing import Optional, Callable

class CalendarView:
    """
    Main calendar widget showing month view with navigation.
    
    Displays current month in a grid format with day numbers.
    Supports navigation between months within configurable date range.
    """
    
    def __init__(self, parent: tk.Widget, current_date: Optional[date] = None, config=None, timeline=None):
        """
        Initialize calendar view.
        
        Args:
            parent: Parent widget to contain the calendar
            current_date: Starting date to display (defaults to today)
            config: AppConfig instance for date ranges and first entry date
            timeline: DateTimeline instance for day classification data
        """
        self.parent = parent
        self.config = config
        self.timeline = timeline  # Store timeline for day classification lookup
        
        # Color definitions for day classifications (per ROADMAP specs)
        try:
            from calendar_app.model.day import DayClassification
            self.CLASSIFICATION_COLORS = {
                DayClassification.UK_RESIDENCE: "#adffc3",     # Light green
                DayClassification.SHORT_TRIP: "#74c0fc",       # Light blue
                DayClassification.LONG_TRIP: "#ffa8a8",        # Light red
                DayClassification.PRE_ENTRY: "#e9ecef",        # Disabled gray
                DayClassification.UNKNOWN: "#fff3cd"           # Warning yellow
            }
        except ImportError:
            # Fallback if imports fail
            self.CLASSIFICATION_COLORS = {}
        
        # Set date range from config if available, otherwise use safe defaults
        if config:
            self.min_year = config.start_year
            self.max_year = config.end_year
            # Parse first entry date from config - let errors propagate up
            try:
                self.first_entry_date = datetime.strptime(config.first_entry_date, "%d-%m-%Y").date()
            except (ValueError, AttributeError) as e:
                # Re-raise with more context, following our error handling pattern
                raise ValueError(f"Invalid first_entry_date in config: {config.first_entry_date}. Expected format: DD-MM-YYYY. Error: {e}")
        else:
            # Date range validation (as per roadmap requirements)
            self.min_year = 2023
            self.max_year = 2040
            self.first_entry_date = None
        
        # Handle current_date safely - ensure it's within valid range
        if current_date:
            self.current_date = current_date
        else:
            today = date.today()
            # If today is outside valid range, use start of valid range
            if today.year < self.min_year:
                self.current_date = date(self.min_year, 1, 1)
            elif today.year > self.max_year:
                self.current_date = date(self.max_year, 12, 1)
            else:
                self.current_date = today
        
        # Callback for when a day is clicked (will be set later)
        self.day_click_callback: Optional[Callable] = None
        
        # Create the main calendar frame
        self.calendar_frame = None
        self.header_frame = None
        self.grid_frame = None
        
        # Navigation controls
        self.prev_year_button = None
        self.prev_month_button = None
        self.next_month_button = None
        self.next_year_button = None
        
        # Month/Year selection dropdowns
        self.month_var = tk.StringVar()
        self.year_var = tk.StringVar()
        self.month_dropdown = None
        self.year_dropdown = None
        
        self.day_buttons = {}  # Store day buttons for later reference
        
        self.create_calendar()
        
    def get_day_classification_color(self, date):
        """
        Get the background color for a day based on its classification and special dates.
        
        Args:
            date (datetime.date): The date to get the classification for.
            
        Returns:
            tuple: (background_color, text_color) for the day
        """
        # Check for special dates first
        if self.config and self.config.first_entry_date:
            first_entry = self.config.first_entry_date
            if isinstance(first_entry, str):
                from datetime import datetime
                first_entry = datetime.strptime(first_entry, "%d-%m-%Y").date()
            
            # First entry date - bright green
            if date == first_entry:
                return "#28a745", "white"  # Bright green with white text
            
            # Target completion date - prize yellow
            if hasattr(self.config, 'target_completion_date') and date == self.config.target_completion_date:
                return "#ffd700", "black"  # Prize yellow with black text
        
        # Regular classification colors
        if self.timeline:
            try:
                day_obj = self.timeline.get_day(date)
                classification = day_obj.classification
                color = self.CLASSIFICATION_COLORS.get(classification, "#FFFF99")  # Default to warning yellow
                return color, "black"
            except:
                # Timeline might not have data for this date
                return "#FFFF99", "gray"  # Warning yellow for unknown
        
        # Default if no timeline
        return "white", "black"

    def create_calendar(self):
        """
        Create the complete calendar widget with header and grid.
        """
        # Main container frame
        self.calendar_frame = tk.Frame(self.parent, bg="white", relief="ridge", bd=2)
        self.calendar_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create header with navigation and month/year display
        self.create_header()
        
        # Create the calendar grid
        self.create_grid()
        
        # Initial display of current month
        self.update_calendar()
        
    def create_header(self):
        """
        Create calendar header with navigation buttons and month/year dropdowns.
        """
        self.header_frame = tk.Frame(self.calendar_frame, bg="white")
        self.header_frame.pack(fill=tk.X, pady=(10, 5))
        
        # Configure grid columns: side columns max 15% each, center takes remaining 70%
        self.header_frame.columnconfigure(0, weight=1, uniform="side")  # Left: ◀ First Entry - max 15%
        self.header_frame.columnconfigure(1, weight=7)                  # Center: dropdowns - 70%
        self.header_frame.columnconfigure(2, weight=1, uniform="side")  # Right: Target Date ▶ - max 15%
        
        # Configure grid rows: dynamic height based on content
        self.header_frame.rowconfigure(0, weight=0)  # Row 0: auto-size to content
        self.header_frame.rowconfigure(1, weight=0)  # Row 1: auto-size to content
        
        # ROW 0: Skip buttons and month/year dropdowns
        # Cell 0,0: First Entry button with left arrow
        self.jump_to_first_entry_button = tk.Button(
            self.header_frame,
            text="◀ First Entry",  # Arrow before text
            command=self.jump_to_first_entry,
            bg="#28a745",  # Bright green
            fg="white",
            font=("Arial", 8, "bold"),  # Standardized font
            relief="raised",
            bd=2,
            height=1  # Consistent height
        )
        self.jump_to_first_entry_button.grid(row=0, column=0, sticky="ew", padx=2, pady=[1,0])
        
        # Cell 0,1: Month and Year dropdowns (centered)
        center_frame = tk.Frame(self.header_frame, bg="white")
        center_frame.grid(row=0, column=1, padx=10, pady=[1,0])
        
        # Center the frame content
        center_content = tk.Frame(center_frame, bg="white")
        center_content.pack(expand=True)
        
        # Month dropdown
        month_names = [calendar.month_name[i] for i in range(1, 13)]
        self.month_var.set(calendar.month_name[self.current_date.month])
        self.month_dropdown = ttk.Combobox(
            center_content,  # Use centered content frame
            textvariable=self.month_var,
            values=month_names,
            state="readonly",
            font=("Arial", 12, "bold"),  # Standardized font
            width=12
        )
        self.month_dropdown.pack(side=tk.LEFT, padx=5)
        self.month_dropdown.bind("<<ComboboxSelected>>", self.on_month_changed)
        
        # Year dropdown
        years = list(range(self.min_year, self.max_year + 1))
        self.year_var.set(str(self.current_date.year))
        self.year_dropdown = ttk.Combobox(
            center_content,  # Use centered content frame
            textvariable=self.year_var,
            values=years,
            state="readonly", 
            font=("Arial", 12, "bold"),  # Standardized font
            width=6
        )
        self.year_dropdown.pack(side=tk.LEFT, padx=5)
        self.year_dropdown.bind("<<ComboboxSelected>>", self.on_year_changed)
        
        # Cell 0,2: Target Date button with right arrow
        self.jump_to_objective_button = tk.Button(
            self.header_frame,
            text="Target Date ▶",  # Arrow after text
            command=self.jump_to_objective_date,
            bg="#ffd700",  # Prize yellow
            fg="black",
            font=("Arial", 8, "bold"),  # Standardized font
            relief="raised",
            bd=2,
            height=1  # Consistent height
        )
        self.jump_to_objective_button.grid(row=0, column=2, sticky="ew", padx=2, pady=[1,0])
        
        # ROW 1: Navigation buttons
        # Cell 1,0: Previous navigation (fills cell)
        left_nav = tk.Frame(self.header_frame, bg="white")
        left_nav.grid(row=1, column=0, sticky="ew", padx=2, pady=[1,1])
        
        self.prev_year_button = tk.Button(
            left_nav,
            text="◀◀",
            command=self.previous_year,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.prev_year_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=[0,1])
        
        self.prev_month_button = tk.Button(
            left_nav,
            text="◀",
            command=self.previous_month,
            bg="#4dabf7",
            fg="white",
            font=("Arial", 8),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.prev_month_button.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=[1,0])
        
        # Cell 1,1: Empty (center)
        # No content needed - creates visual balance
        
        # Cell 1,2: Next navigation (fills cell)
        right_nav = tk.Frame(self.header_frame, bg="white")
        right_nav.grid(row=1, column=2, sticky="ew", padx=2, pady=[1,1])
        
        self.next_month_button = tk.Button(
            right_nav,
            text="▶",
            command=self.next_month,
            bg="#4dabf7",
            fg="white",
            font=("Arial", 8),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.next_month_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=[0,1])
        
        self.next_year_button = tk.Button(
            right_nav,
            text="▶▶",
            command=self.next_year,
            bg="#ff6b6b",
            fg="white",
            font=("Arial", 8, "bold"),
            relief="raised",
            bd=2,
            width=3,
            height=1
        )
        self.next_year_button.pack(side=tk.RIGHT, expand=True, fill=tk.X, padx=[1,0])
        
    def create_grid(self):
        """
        Create the calendar grid with day headers and date buttons.
        """
        self.grid_frame = tk.Frame(self.calendar_frame, bg="white")
        self.grid_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Day of week headers - half height of day squares
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        for i, day_name in enumerate(day_names):
            header_label = tk.Label(
                self.grid_frame,
                text=day_name,
                font=("Arial", 10, "bold"),
                bg="#e8e8e8",
                relief="raised",
                bd=1,
                width=8,
                height=1  # Half height of day squares (day squares are height=3)
            )
            header_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
            
        # Configure grid weights for responsive resizing
        for i in range(7):  # 7 columns for days of week
            self.grid_frame.columnconfigure(i, weight=1, minsize=70)  # Minimum column width
        
        # Configure rows: smaller header + 6 weeks of day buttons
        self.grid_frame.rowconfigure(0, weight=0, minsize=25)   # Header row - smaller
        for i in range(1, 7):  # 6 weeks of day buttons  
            self.grid_frame.rowconfigure(i, weight=1, minsize=50)   # Day button rows - larger
        
        # Prevent grid from shrinking below minimum size requirements
        # Header: 25px + 6 weeks * 50px = 25 + 300 = 325px + padding = 400px total height
        self.grid_frame.grid_propagate(False)
        self.grid_frame.config(width=500, height=400)
            
    def update_calendar(self):
        """
        Update calendar display for current month/year and navigation button states.
        """
        # Update dropdown values
        self.month_var.set(calendar.month_name[self.current_date.month])
        self.year_var.set(str(self.current_date.year))
        
        # Update navigation button states
        self.update_button_states()
        
        # Clear existing day buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Get calendar data for current month
        year = self.current_date.year
        month = self.current_date.month
        
        # Get first day of month and number of days
        first_day = date(year, month, 1)
        # Python calendar uses 0=Monday, but we want 0=Monday too, so no adjustment needed
        first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Create day buttons
        current_row = 1  # Start after header row
        current_col = first_weekday  # Start at correct weekday
        
        for day in range(1, days_in_month + 1):
            # Create date for this day
            day_date = date(year, month, day)
            
            # Determine if this is today (safe check for out-of-range dates)
            today = date.today()
            is_today = (day_date == today and 
                       self.min_year <= today.year <= self.max_year)
            
            # Check if this day is before first entry date
            is_before_entry = (self.first_entry_date and 
                              day_date < self.first_entry_date)
            
            # Set styling based on day type and classification
            if is_before_entry:
                text_color = "gray"
                bg_color = "#f5f5f5"
                font = ("Arial", 9)
                state = "disabled"
            elif is_today:
                # Get classification color but keep today highlighting
                classification_bg, _ = self.get_day_classification_color(day_date)
                text_color = "red"
                bg_color = classification_bg
                font = ("Arial", 9, "bold")
                state = "normal"
            else:
                # Use classification color for regular days
                bg_color, text_color = self.get_day_classification_color(day_date)
                font = ("Arial", 9)
                state = "normal"
            
            # Create button for this day with proper state
            # Fixed sizing to ensure consistency across all months
            day_button = tk.Button(
                self.grid_frame,
                text=str(day),
                font=font,
                fg=text_color,
                bg=bg_color,
                relief="raised",
                bd=1,
                width=8,
                height=3,
                state=state,
                command=lambda d=day_date: self.day_clicked(d) if state == "normal" else None
            )
            
            # Add hover effect only for enabled buttons
            if state == "normal":
                def on_enter(event, btn=day_button, orig_bg=bg_color):
                    btn.config(bg="#f0f0f0")
                        
                def on_leave(event, btn=day_button, orig_bg=bg_color):
                    btn.config(bg=orig_bg)
                        
                day_button.bind("<Enter>", on_enter)
                day_button.bind("<Leave>", on_leave)
            
            # Position button in grid
            day_button.grid(row=current_row, column=current_col, padx=1, pady=1, sticky="nsew")
            
            # Store button reference
            self.day_buttons[day_date] = day_button
            
            # Move to next position
            current_col += 1
            if current_col >= 7:  # Start new row
                current_col = 0
                current_row += 1
    
    def update_button_states(self):
        """
        Enable/disable navigation buttons based on date range limits.
        """
        year = self.current_date.year
        month = self.current_date.month
        
        # Check if at minimum date (January min_year)
        at_min_date = (year == self.min_year and month == 1)
        at_min_year = (year == self.min_year)
        
        # Check if at maximum date (December max_year)  
        at_max_date = (year == self.max_year and month == 12)
        at_max_year = (year == self.max_year)
        
        # Update button states
        self.prev_month_button.config(state="disabled" if at_min_date else "normal")
        self.prev_year_button.config(state="disabled" if at_min_year else "normal")
        self.next_month_button.config(state="disabled" if at_max_date else "normal")
        self.next_year_button.config(state="disabled" if at_max_year else "normal")
                
    def previous_month(self):
        """
        Navigate to previous month (with date range validation).
        """
        # Calculate previous month
        if self.current_date.month == 1:
            new_year = self.current_date.year - 1
            new_month = 12
        else:
            new_year = self.current_date.year
            new_month = self.current_date.month - 1
            
        # Validate date range
        if new_year >= self.min_year:
            self.current_date = date(new_year, new_month, 1)
            self.update_calendar()
            
    def next_month(self):
        """
        Navigate to next month (with date range validation).
        """
        # Calculate next month
        if self.current_date.month == 12:
            new_year = self.current_date.year + 1
            new_month = 1
        else:
            new_year = self.current_date.year
            new_month = self.current_date.month + 1
            
        # Validate date range  
        if new_year <= self.max_year:
            self.current_date = date(new_year, new_month, 1)
            self.update_calendar()
            
    def previous_year(self):
        """
        Navigate to previous year (with date range validation).
        """
        new_year = self.current_date.year - 1
        if new_year >= self.min_year:
            self.current_date = date(new_year, self.current_date.month, 1)
            self.update_calendar()
            
    def next_year(self):
        """
        Navigate to next year (with date range validation).
        """
        new_year = self.current_date.year + 1
        if new_year <= self.max_year:
            self.current_date = date(new_year, self.current_date.month, 1)
            self.update_calendar()
            
    def on_month_changed(self, event=None):
        """
        Handle month dropdown selection change.
        """
        selected_month_name = self.month_var.get()
        # Find month number from name
        for i in range(1, 13):
            if calendar.month_name[i] == selected_month_name:
                new_month = i
                break
        else:
            return  # Invalid month name
            
        self.current_date = date(self.current_date.year, new_month, 1)
        self.update_calendar()
        
    def on_year_changed(self, event=None):
        """
        Handle year dropdown selection change.
        """
        try:
            new_year = int(self.year_var.get())
            if self.min_year <= new_year <= self.max_year:
                self.current_date = date(new_year, self.current_date.month, 1)
                self.update_calendar()
        except ValueError:
            pass  # Invalid year value
            
    def day_clicked(self, day_date: date):
        """
        Handle day button click.
        
        Args:
            day_date: The date that was clicked
        """
        print(f"Day clicked: {day_date.strftime('%d-%m-%Y')}")
        
        # Call registered callback if available
        if self.day_click_callback:
            self.day_click_callback(day_date)
            
    def set_day_click_callback(self, callback: Callable):
        """
        Set callback function for day click events.
        
        Args:
            callback: Function to call when day is clicked, receives date parameter
        """
        self.day_click_callback = callback
        
    def get_current_date(self) -> date:
        """
        Get currently displayed date.
        
        Returns:
            Currently displayed month/year as date object
        """
        return self.current_date
        
    def set_current_date(self, new_date: date):
        """
        Set current date and update display.
        
        Args:
            new_date: New date to display
        """
        # Validate date range
        if self.min_year <= new_date.year <= self.max_year:
            self.current_date = new_date
            self.update_calendar()
        else:
            print(f"Date {new_date} is outside valid range ({self.min_year}-{self.max_year})")
    
    def jump_to_first_entry(self):
        """
        Navigate to the first entry date month.
        """
        if self.config and self.config.first_entry_date:
            first_entry = self.config.first_entry_date
            if isinstance(first_entry, str):
                from datetime import datetime
                first_entry = datetime.strptime(first_entry, "%d-%m-%Y").date()
            
            # Navigate to the month containing first entry date
            self.set_current_date(date(first_entry.year, first_entry.month, 1))
    
    def jump_to_objective_date(self):
        """
        Navigate to the target completion date month.
        """
        if self.config and hasattr(self.config, 'target_completion_date'):
            target_date = self.config.target_completion_date
            # Navigate to the month containing target completion date
            self.set_current_date(date(target_date.year, target_date.month, 1))