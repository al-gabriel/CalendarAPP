"""
Calendar Year Module

Displays a year calendar grid with 12 mini-month views in a 3x4 layout.
Similar to calendar_month_module.py but shows all 12 months of a year.
"""

import tkinter as tk
import calendar
from datetime import date, timedelta, timedelta
from typing import Optional, Callable

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline


class CalendarYearModule(tk.Frame):
    """
    Year calendar module displaying a 3x4 grid of mini-month calendars.
    
    Features:
    - 3x4 grid showing all 12 months of the year
    - Each month shows small day squares with classification colors
    - Clickable month names to switch to month view
    - Clickable days to show day info
    - Same color scheme as month view
    """
    
    def __init__(self, parent: tk.Widget, config: Optional[AppConfig] = None,
                 timeline: Optional[DateTimeline] = None,
                 date_selected_callback: Optional[Callable[[date], None]] = None,
                 month_selected_callback: Optional[Callable[[date], None]] = None):
        """
        Initialize year calendar module.
        
        Args:
            parent: Parent widget
            config: Application configuration
            timeline: DateTimeline instance
            date_selected_callback: Callback when a day is clicked
            month_selected_callback: Callback when a month name is clicked
        """
        super().__init__(parent, bg="white")
        
        self.config = config
        self.timeline = timeline
        self.date_selected_callback = date_selected_callback
        self.month_selected_callback = month_selected_callback
        self.current_date = date.today()
        
        # Color definitions for day classifications (same as month module)
        try:
            from calendar_app.model.day import DayClassification
            self.CLASSIFICATION_COLORS = {
                DayClassification.UK_RESIDENCE: "#adffc3",     # Light green
                DayClassification.SHORT_TRIP: "#74c0fc",       # Light blue  
                DayClassification.LONG_TRIP: "#ffa8a8",        # Light red
                DayClassification.NO_VISA_COVERAGE: "#ffcccc", # Light red (same tone as ILR uncovered)
                DayClassification.PRE_ENTRY: "#e9ecef",        # Disabled gray
                DayClassification.UNKNOWN: "#fff3cd"           # Warning yellow
            }
        except ImportError:
            self.CLASSIFICATION_COLORS = {}
        
        # Visa border colors for visa period boundaries
        self.VISA_BORDER_COLORS = {
            'start': '#cc99ff',  # Light purple (for visa start dates)
            'end': '#800080'     # Dark purple (for visa end dates)
        }
        
        # Get first entry date from config (already parsed)
        self.first_entry_date = None
        if config and hasattr(config, 'first_entry_date_obj'):
            self.first_entry_date = config.first_entry_date_obj
                
        # Grid of day buttons for all months
        self.day_buttons = {}  # month_num -> {day_num: button}
        self.month_labels = {}  # month_num -> label
        
        # Target dates for highlighting
        self.target_dates = {}
        
        # Performance optimizations
        self.resize_timer = None  # For resize debouncing
        self.year_color_cache = {}  # Cache for year color data
        
        # Setup UI
        self.setup_year_grid()
        self.update_year_display()
    
    def setup_year_grid(self):
        """Set up the 3x4 grid structure for 12 months."""
        # Configure main frame layout - fixed sizes for better resize performance
        for col in range(3):
            self.grid_columnconfigure(col, weight=0, minsize=250)
        for row in range(4):
            self.grid_rowconfigure(row, weight=0, minsize=150)
        
        # Bind resize debouncing
        self.bind('<Configure>', self.on_configure_debounced)
        
        # Create frames for each month (3x4 = 12 months)
        self.month_frames = {}
        for month_num in range(1, 13):  # 1-12 for January-December
            row = (month_num - 1) // 3
            col = (month_num - 1) % 3
            
            # Create month container frame
            month_frame = tk.Frame(self, bg="white", relief=tk.FLAT, bd=1)
            month_frame.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            self.month_frames[month_num] = month_frame
            
            # Configure month frame layout - fixed sizes
            month_frame.grid_columnconfigure(0, weight=0, minsize=250)
            month_frame.grid_rowconfigure(0, weight=0, minsize=25)  # Month name header - fixed
            month_frame.grid_rowconfigure(1, weight=0, minsize=125)  # Days grid - fixed
            
            # Create month name header (clickable)
            month_name = calendar.month_name[month_num]
            month_label = tk.Label(
                month_frame,
                text=month_name,
                font=("Arial", 10, "bold"),
                bg="#e9ecef",
                fg="black",
                relief=tk.RIDGE,
                bd=1,
                width=8,  # Fixed width
                height=1,  # Single line height
                cursor="hand2"
            )
            month_label.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            self.month_labels[month_num] = month_label
            
            # Bind click event to month name
            month_label.bind("<Button-1>", lambda e, m=month_num: self.on_month_clicked(m))
            
            # Create days grid frame
            days_frame = tk.Frame(month_frame, bg="white")
            days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            
            # Configure days grid (7 columns for days, 6 rows for weeks)
            for day_col in range(7):
                days_frame.grid_columnconfigure(day_col, weight=1, minsize=20)
            for day_row in range(6):
                days_frame.grid_rowconfigure(day_row, weight=1, minsize=15)
            
            # Store days frame reference for later use
            month_frame.days_frame = days_frame
            
            # Initialize day buttons dictionary for this month
            self.day_buttons[month_num] = {}
    
    def update_year_display(self):
        """Update the year display with current year's months using batch data fetching."""
        year = self.current_date.year
        
        # Batch fetch all colors for the year (major performance improvement)
        if year not in self.year_color_cache and self.timeline:
            self.year_color_cache[year] = self.timeline.get_year_day_colors(
                year, 
                self.CLASSIFICATION_COLORS,
                self.first_entry_date,
                self.CLASSIFICATION_COLORS.get('PRE_ENTRY', '#e9ecef'),
                'white'
            )
        
        for month_num in range(1, 13):
            self.update_month_display(year, month_num)
    
    def update_month_display(self, year: int, month_num: int):
        """Update display for a specific month."""
        month_frame = self.month_frames[month_num]
        days_frame = month_frame.days_frame
        
        # Bulk destroy and recreate days_frame for better performance
        # Instead of destroying 42 individual widgets, destroy the container
        days_frame.destroy()
        self.day_buttons[month_num].clear()
        
        # Recreate days grid frame
        days_frame = tk.Frame(month_frame, bg="white")
        days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure days grid (7 columns for days, 6 rows for weeks)
        for day_col in range(7):
            days_frame.grid_columnconfigure(day_col, weight=1, minsize=20)
        for day_row in range(6):
            days_frame.grid_rowconfigure(day_row, weight=1, minsize=15)
        
        # Update frame reference
        month_frame.days_frame = days_frame
        
        # Get calendar data for this month
        cal = calendar.Calendar(0)  # Monday as first day
        month_days = list(cal.itermonthdates(year, month_num))
        
        # Ensure exactly 42 days (6 weeks x 7 days) for consistent 7x6 grid
        if len(month_days) < 42:
            # If less than 42 days, add more days from next month
            while len(month_days) < 42:
                last_date = month_days[-1]
                next_date = last_date + timedelta(days=1)
                month_days.append(next_date)
        elif len(month_days) > 42:
            # If more than 42 days, trim to exactly 42
            month_days = month_days[:42]
        
        # Create day buttons in 6x7 grid (exactly 42 buttons)
        for week_idx in range(6):  # Always 6 rows
            for day_idx in range(7):  # Always 7 columns
                button_idx = week_idx * 7 + day_idx
                day_date = month_days[button_idx]
                
                # Create small day button
                if day_date.month == month_num:
                    # Day belongs to current month
                    day_text = str(day_date.day)
                    # Use cached color data instead of individual timeline lookups
                    cached_colors = self.year_color_cache.get(year, {})
                    bg_color = cached_colors.get(day_date, self.get_day_color(day_date))
                    text_color = "black" if bg_color != "#e9ecef" else "gray"
                    state = "normal"
                else:
                    # Day belongs to adjacent month (show as disabled without number)
                    day_text = ""
                    bg_color = "#f8f9fa"
                    text_color = "#dee2e6"
                    state = "disabled"
                
                day_button = tk.Button(
                    days_frame,
                    text=day_text,
                    font=("Arial", 7),
                    bg=bg_color,
                    fg=text_color,
                    relief=tk.RIDGE,
                    bd=1,
                    state=state,
                    width=2,
                    height=1
                )
                
                day_button.grid(row=week_idx, column=day_idx, sticky="nsew", padx=0, pady=0)
                
                # Apply special styling for current month days (target dates and today)
                if day_date.month == month_num and state == "normal":
                    self._apply_special_day_styling(day_button, day_date, bg_color, text_color)
                
                # Bind click event if day is in current month
                if day_date.month == month_num and state == "normal":
                    day_button.bind("<Button-1>", lambda e, d=day_date: self.on_day_clicked(d))
                    self.day_buttons[month_num][day_date.day] = day_button
    
    def _apply_special_day_styling(self, button: tk.Button, button_date: date, bg_color: str, text_color: str):
        """Apply special styling for target dates, today's date, and visa background colors (similar to month view)."""
        # Check for visa period start/end dates - override background color
        if self.timeline:
            visa_border = self.timeline.get_visa_border_info(button_date)
            if visa_border['is_visa_start']:
                bg_color = self.VISA_BORDER_COLORS['start']  # Light purple
            elif visa_border['is_visa_end']:
                bg_color = self.VISA_BORDER_COLORS['end']    # Dark purple
                text_color = "white"  # White text for better contrast on dark purple
        
        # Special date highlighting - target completion dates
        is_target_date = button_date in self.target_dates
        target_info = self.target_dates.get(button_date)
        
        if is_target_date and target_info:
            # Target completion date - use specific color based on target type, override classification color
            target_color = target_info.get('color', 'goldenrod')
            button.config(bg=target_color, fg="black", highlightbackground=target_color,
                         highlightcolor=target_color, highlightthickness=2, font=("Arial", 7, "bold"))
        elif button_date == date.today():
            # Today - red bold text with background (could be visa color or classification color)
            button.config(bg=bg_color, fg="red", font=("Arial", 7, "bold"))
        else:
            # Normal day - use background color (could be visa color or classification color)
            button.config(bg=bg_color, fg=text_color, font=("Arial", 7))
    
    def create_all_month_frames(self):
        """Create all 12 month frames at once for better performance."""
        self.month_frames = {}
        self.day_buttons = {}
        self.month_labels = {}
        
        for month_num in range(1, 13):  # 1-12 for January-December
            row = (month_num - 1) // 3
            col = (month_num - 1) % 3
            
            # Create month container frame
            month_frame = tk.Frame(self, bg="white", relief=tk.FLAT, bd=0)
            month_frame.grid(row=row, column=col, sticky="nsew", padx=0, pady=0)
            self.month_frames[month_num] = month_frame
            
            # Configure month frame layout - fixed sizes
            month_frame.grid_columnconfigure(0, weight=0, minsize=250)
            month_frame.grid_rowconfigure(0, weight=0, minsize=25)  # Month name header - fixed
            month_frame.grid_rowconfigure(1, weight=0, minsize=125)  # Days grid - fixed
            
            # Create month name header (clickable)
            month_name = calendar.month_name[month_num]
            month_label = tk.Label(
                month_frame,
                text=month_name,
                font=("Arial", 10, "bold"),
                bg="#e9ecef",
                fg="black",
                relief=tk.RIDGE,
                bd=1,
                width=8,  # Fixed width
                height=1,  # Single line height
                cursor="hand2"
            )
            month_label.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
            self.month_labels[month_num] = month_label
            
            # Bind click event to month name
            month_label.bind("<Button-1>", lambda e, m=month_num: self.on_month_clicked(m))
            
            # Create days grid frame
            days_frame = tk.Frame(month_frame, bg="white")
            days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
            
            # Configure days grid (7 columns for days, 6 rows for weeks)
            for day_col in range(7):
                days_frame.grid_columnconfigure(day_col, weight=1, minsize=20)
            for day_row in range(6):
                days_frame.grid_rowconfigure(day_row, weight=1, minsize=15)
            
            # Store days frame reference for later use
            month_frame.days_frame = days_frame
            
            # Initialize day buttons dictionary for this month
            self.day_buttons[month_num] = {}
    
    def populate_month_display(self, year: int, month_num: int):
        """Update display for a specific month."""
        month_frame = self.month_frames[month_num]
        days_frame = month_frame.days_frame
        
        # Bulk destroy and recreate days_frame for better performance
        # Instead of destroying 42 individual widgets, destroy the container
        days_frame.destroy()
        self.day_buttons[month_num].clear()
        
        # Recreate days grid frame
        days_frame = tk.Frame(month_frame, bg="white")
        days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure days grid (7 columns for days, 6 rows for weeks)
        for day_col in range(7):
            days_frame.grid_columnconfigure(day_col, weight=1, minsize=20)
        for day_row in range(6):
            days_frame.grid_rowconfigure(day_row, weight=1, minsize=15)
        
        # Update frame reference
        month_frame.days_frame = days_frame
        
        # Get calendar data for this month
        cal = calendar.Calendar(0)  # Monday as first day
        month_days = list(cal.itermonthdates(year, month_num))
        
        # Ensure exactly 42 days (6 weeks x 7 days) for consistent 7x6 grid
        if len(month_days) < 42:
            # If less than 42 days, add more days from next month
            while len(month_days) < 42:
                last_date = month_days[-1]
                next_date = last_date + timedelta(days=1)
                month_days.append(next_date)
        elif len(month_days) > 42:
            # If more than 42 days, trim to exactly 42
            month_days = month_days[:42]
        # Create day buttons in 6x7 grid (exactly 42 buttons)
        for week_idx in range(6):  # Always 6 rows
            for day_idx in range(7):  # Always 7 columns
                button_idx = week_idx * 7 + day_idx
                day_date = month_days[button_idx]
                
                # Create small day button
                if day_date.month == month_num:
                    # Day belongs to current month
                    day_text = str(day_date.day)
                    # Use cached color data instead of individual timeline lookups
                    cached_colors = self.year_color_cache.get(year, {})
                    bg_color = cached_colors.get(day_date, self.get_day_color(day_date))
                    text_color = "black" if bg_color != "#e9ecef" else "gray"
                    state = "normal"
                else:
                    # Day belongs to adjacent month (show as disabled without number)
                    day_text = ""
                    bg_color = "#f8f9fa"
                    text_color = "#dee2e6"
                    state = "disabled"
                
                day_button = tk.Button(
                    days_frame,
                    text=day_text,
                    font=("Arial", 7),
                    bg=bg_color,
                    fg=text_color,
                    relief=tk.RIDGE,
                    bd=1,
                    state=state,
                    width=2,
                    height=1
                )
                
                day_button.grid(row=week_idx, column=day_idx, sticky="nsew", padx=0, pady=0)
                
                # Bind click event if day is in current month
                if day_date.month == month_num and state == "normal":
                    day_button.bind("<Button-1>", lambda e, d=day_date: self.on_day_clicked(d))
                    self.day_buttons[month_num][day_date.day] = day_button
    
    def get_day_color(self, day_date: date) -> str:
        """Get the background color for a day based on its classification."""
        if not self.timeline:
            return "white"
        
        # Check if date is before first entry
        if self.first_entry_date and day_date < self.first_entry_date:
            return self.CLASSIFICATION_COLORS.get("PRE_ENTRY", "#e9ecef")
        
        try:
            day_obj = self.timeline.get_day(day_date)
            if day_obj and hasattr(day_obj, 'classification'):
                return self.CLASSIFICATION_COLORS.get(day_obj.classification, "white")
        except (KeyError, AttributeError):
            pass
        
        return "white"
    
    def on_day_clicked(self, day_date: date):
        """Handle day click event."""
        if self.date_selected_callback:
            self.date_selected_callback(day_date)
    
    def on_month_clicked(self, month_num: int):
        """Handle month name click event."""
        if self.month_selected_callback:
            # Create date for first day of clicked month
            target_date = date(self.current_date.year, month_num, 1)
            self.month_selected_callback(target_date)
    
    def on_configure_debounced(self, event):
        """Handle resize events with debouncing for smooth performance."""
        # Only handle events for this widget, not child widgets
        if event.widget == self:
            # Cancel any existing timer
            if self.resize_timer:
                self.after_cancel(self.resize_timer)
            # Set new timer - only update after 100ms of no resize events
            self.resize_timer = self.after(100, self.on_resize_complete)
    
    def on_resize_complete(self):
        """Called after resize is complete - can add layout optimizations here if needed."""
        self.resize_timer = None
        # For now, tkinter handles the layout automatically
        # Future optimization: manual layout calculation could go here
    
    def set_current_date(self, new_date: date):
        """Set the current date and update display only if year changed."""
        if new_date.year != self.current_date.year:
            # Clear cache for old year to save memory
            self.year_color_cache.clear()
            self.current_date = new_date
            self.update_year_display()
        else:
            # Same year, just update current_date without full refresh
            self.current_date = new_date
            # Could add highlighting logic here if needed in the future
    
    def refresh_display(self):
        """Refresh the display without full rebuild."""
        self.update_year_display()
    
    def set_target_dates(self, target_dates: dict):
        """Set target dates for highlighting."""
        self.target_dates = target_dates or {}
        self.refresh_display()
    
    def highlight_dates(self, dates_to_highlight: list):
        """Highlight specific dates (for target completion dates, etc.)."""
        # Implementation similar to month module if needed
        pass
    
    def update_timeline(self, timeline: DateTimeline):
        """Update the timeline and refresh display."""
        self.timeline = timeline
        self.refresh_display()
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline data and refresh display."""
        self.timeline = timeline
        self.refresh_display()
    
    def update_timeline(self, timeline: DateTimeline):
        """Placeholder method."""
        self.timeline = timeline