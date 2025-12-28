"""
Month View

Month calendar view component using new architecture.
Refactored from original CalendarView to use BaseCalendarView and NavigationHeader.
"""

import tkinter as tk
import calendar
from datetime import date
from typing import Optional, Callable
from .base_view import BaseCalendarView


class MonthView(BaseCalendarView):
    """
    Month calendar view showing monthly grid with day buttons.
    
    Features:
    - Monthly calendar grid with day classification colors
    - Day click handling
    - Visual classification of trips and residence
    - Special date highlighting (first entry, target completion)
    """
    
    def __init__(self, parent: tk.Widget, current_date: Optional[date] = None, 
                 config=None, timeline=None):
        """Initialize month view."""
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
        
        # Parse first entry date from config
        self.first_entry_date = None
        if config and config.first_entry_date:
            try:
                from datetime import datetime
                self.first_entry_date = datetime.strptime(config.first_entry_date, "%d-%m-%Y").date()
            except (ValueError, AttributeError) as e:
                raise ValueError(f"Invalid first_entry_date in config: {config.first_entry_date}. Expected format: DD-MM-YYYY. Error: {e}")
        
        # Day click callback
        self.day_click_callback: Optional[Callable] = None
        
        # Calendar grid components
        self.grid_frame = None
        self.day_buttons = {}
        
        # Initialize base class
        super().__init__(parent, current_date, config, timeline)
    
    def create_content(self):
        """Create month view specific content (calendar grid)."""
        self.create_grid()
        self.update_display()
    
    def create_grid(self):
        """Create the calendar grid with day headers and date buttons."""
        self.grid_frame = tk.Frame(self.content_frame, bg="white")
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
                height=1  # Half height of day squares
            )
            header_label.grid(row=0, column=i, padx=1, pady=1, sticky="nsew")
        
        # Configure grid weights for responsive resizing
        for i in range(7):  # 7 columns for days of week
            self.grid_frame.columnconfigure(i, weight=1, minsize=70)
        
        # Configure rows: smaller header + 6 weeks of day buttons
        self.grid_frame.rowconfigure(0, weight=0, minsize=25)   # Header row - smaller
        for i in range(1, 7):  # 6 weeks of day buttons
            self.grid_frame.rowconfigure(i, weight=1, minsize=50)   # Day button rows - larger
        
        # Prevent grid from shrinking below minimum size requirements
        self.grid_frame.grid_propagate(False)
        self.grid_frame.config(width=500, height=400)
    
    def update_display(self):
        """Update the calendar grid for current month."""
        # Clear existing day buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Get calendar data for current month
        year = self.current_date.year
        month = self.current_date.month
        
        # Get first day of month and number of days
        first_day = date(year, month, 1)
        first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
        days_in_month = calendar.monthrange(year, month)[1]
        
        # Create day buttons
        current_row = 1  # Start after header row
        current_col = first_weekday  # Start at correct weekday
        
        for day in range(1, days_in_month + 1):
            # Create date for this day
            day_date = date(year, month, day)
            
            # Determine if this is today
            today = date.today()
            is_today = (day_date == today and 
                       self.config and
                       self.config.start_year <= today.year <= self.config.end_year)
            
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
            
            # Create button for this day
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
        
        # Future: Request switch to day detail view
        # self.request_view_switch("day", date=day_date)
    
    def set_day_click_callback(self, callback: Callable):
        """
        Set callback function for day click events.
        
        Args:
            callback: Function to call when day is clicked, receives date parameter
        """
        self.day_click_callback = callback