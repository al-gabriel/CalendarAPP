"""
Calendar Month Module

Displays a month calendar grid with day buttons and classification colors.
This replaces the old month_view.py from the views directory.
"""

import tkinter as tk
import calendar
from datetime import date, timedelta
from typing import Optional, Callable

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline


class CalendarMonthModule(tk.Frame):
    """
    Month calendar module displaying a monthly grid with day buttons.
    
    Features:
    - Monthly calendar grid with day classification colors
    - Day click handling
    - Visual classification of trips and residence
    - Special date highlighting (first entry, target completion)
    """
    
    def __init__(self, parent: tk.Widget, config: Optional[AppConfig] = None, 
                 timeline: Optional[DateTimeline] = None,
                 date_selected_callback: Optional[Callable[[date], None]] = None):
        """
        Initialize month calendar module.
        
        Args:
            parent: Parent widget
            config: Application configuration
            timeline: DateTimeline instance
            date_selected_callback: Callback when a day is clicked
        """
        super().__init__(parent, bg="white")
        
        self.config = config
        self.timeline = timeline
        self.date_selected_callback = date_selected_callback
        self.current_date = date.today()
        
        # Color definitions for day classifications
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
            self.CLASSIFICATION_COLORS = {}
        
        # Get first entry date from config (already parsed)
        self.first_entry_date = None
        if config and hasattr(config, 'first_entry_date_obj'):
            self.first_entry_date = config.first_entry_date_obj
                
        # Grid of day buttons
        self.day_buttons = {}
        
        # Target dates for highlighting - dictionary mapping date to type and color
        self.target_dates = {}
        
        # Create separate frames for weekdays and days
        self.weekdays_frame = None
        self.days_frame = None
        
        # Setup UI
        self.setup_calendar_grid()
        self.update_month_display()
    
    def setup_calendar_grid(self):
        """Set up the calendar grid structure with separate weekdays and days frames."""
        # Configure main frame layout - single column for stacking
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=0)  # Weekdays frame - fixed height
        self.grid_rowconfigure(1, weight=1)  # Days frame - expandable
        
        # Create weekdays header frame
        self.weekdays_frame = tk.Frame(self, bg="white")
        self.weekdays_frame.grid(row=0, column=0, sticky="ew", padx=0, pady=0)
        
        # Configure weekdays frame grid
        for i in range(7):  # 7 columns for days of week
            self.weekdays_frame.grid_columnconfigure(i, weight=1, minsize=60)
        self.weekdays_frame.grid_rowconfigure(0, weight=0)
        
        # Create weekday header labels
        weekdays = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
        
        for col, weekday in enumerate(weekdays):
            header_label = tk.Label(
                self.weekdays_frame, 
                text=weekday, 
                font=("Arial", 10, "bold"),
                bg="#e9ecef",
                relief=tk.RAISED,
                bd=1,
                width=8,  # Fixed width
                height=2  # Fixed height in text lines
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=1, pady=1)
        
        # Create days grid frame
        self.days_frame = tk.Frame(self, bg="white")
        self.days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure days frame grid
        for i in range(7):  # 7 columns for days of week
            self.days_frame.grid_columnconfigure(i, weight=1, minsize=60)
        for i in range(6):  # 6 rows maximum for weeks
            self.days_frame.grid_rowconfigure(i, weight=1, minsize=40)
    
    def set_current_date(self, new_date: date):
        """Set the current date and update display."""
        self.current_date = new_date
        self.update_month_display()
    
    def update_month_display(self):
        """Update the calendar display for the current month."""
        # Clear existing day buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Get calendar information
        cal = calendar.monthcalendar(self.current_date.year, self.current_date.month)
        
        # Create day buttons
        for week_num, week in enumerate(cal):
            for day_num, day in enumerate(week):
                if day == 0:
                    # Empty cell for days outside current month
                    continue
                
                button_date = date(self.current_date.year, self.current_date.month, day)
                
                # Create day button
                day_button = tk.Button(
                    self.days_frame,  # Use days_frame instead of self
                    text=str(day),
                    font=("Arial", 9),
                    command=lambda d=button_date: self.on_day_clicked(d),
                    relief=tk.RAISED,
                    bd=1
                )
                
                # Set button color based on day classification
                self._apply_day_styling(day_button, button_date)
                
                # Position button (no +1 offset since weekdays are in separate frame)
                row = week_num
                day_button.grid(row=row, column=day_num, sticky="nsew", padx=1, pady=1)
                
                # Store button reference
                self.day_buttons[button_date] = day_button
    
    def _apply_day_styling(self, button: tk.Button, button_date: date):
        """Apply styling to a day button based on classification and special dates."""
        default_color = "#ffffff"  # White default
        text_color = "black"
        
        # Get day classification color
        if self.timeline:
            day = self.timeline.get_day(button_date)
            if day and day.classification in self.CLASSIFICATION_COLORS:
                default_color = self.CLASSIFICATION_COLORS[day.classification]
        
        # Special date highlighting
        is_target_date = button_date in self.target_dates
        target_info = self.target_dates.get(button_date)
        
        if is_target_date and target_info:
            # Target completion date - use specific color based on target type, override classification color
            target_color = target_info.get('color', 'goldenrod')
            button.config(bg=target_color, fg="black", highlightbackground=target_color,
                         highlightcolor=target_color, highlightthickness=3, font=("Arial", 9, "bold"))
        elif button_date == date.today():
            # Today - red bold text with normal classification background
            button.config(bg=default_color, fg="red", font=("Arial", 9, "bold"))
        else:
            # Normal day (removed selected date highlighting)
            button.config(bg=default_color, fg=text_color)
        
        # Disable future dates beyond timeline
        if self.timeline:
            timeline_info = self.timeline.get_date_range_info()
            if button_date > timeline_info.get('end_date', date.today()):
                button.config(state=tk.DISABLED, bg="#f8f9fa", fg="gray")
    
    def on_day_clicked(self, clicked_date: date):
        """Handle day button click."""
        self.current_date = clicked_date
        
        # Update button styling to show selection
        self.update_month_display()
        
        # Notify parent via callback
        if self.date_selected_callback:
            self.date_selected_callback(clicked_date)
    
    def refresh_display(self):
        """Refresh the month calendar display."""
        self.update_month_display()
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference and refresh display."""
        self.timeline = timeline
        self.refresh_display()
    
    def set_target_dates(self, target_dates):
        """Set target dates for highlighting.
        
        Args:
            target_dates: Dictionary mapping date to {'type': str, 'color': str}
                         or list for backwards compatibility
        """
        if isinstance(target_dates, dict):
            self.target_dates = target_dates
        elif isinstance(target_dates, list):
            # Backwards compatibility - treat as generic targets
            self.target_dates = {date: {'type': 'generic', 'color': 'goldenrod'} for date in target_dates}
        else:
            self.target_dates = {}
        self.refresh_display()
    
    def _darken_color(self, color: str) -> str:
        """Darken a hex color by reducing RGB values."""
        if not color or not color.startswith('#'):
            return color
        
        try:
            # Remove # and convert to RGB
            hex_color = color[1:]
            r = int(hex_color[0:2], 16)
            g = int(hex_color[2:4], 16)
            b = int(hex_color[4:6], 16)
            
            # Reduce each component by 20%
            r = max(0, int(r * 0.8))
            g = max(0, int(g * 0.8))
            b = max(0, int(b * 0.8))
            
            # Convert back to hex
            return f"#{r:02x}{g:02x}{b:02x}"
        except (ValueError, IndexError):
            return color