"""
Calendar Month Module

Displays a month calendar grid with day buttons and classification colors.
This replaces the old month_view.py from the views directory.
"""

import tkinter as tk
import calendar
from datetime import date, timedelta, timedelta
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
                relief=tk.RIDGE,
                bd=1,
                width=8,  # Fixed width
                height=1  # Single line height
            )
            header_label.grid(row=0, column=col, sticky="ew", padx=0, pady=0)
        
        # Create days grid frame
        self.days_frame = tk.Frame(self, bg="white")
        self.days_frame.grid(row=1, column=0, sticky="nsew", padx=0, pady=0)
        
        # Configure days frame grid
        for i in range(7):  # 7 columns for days of week
            self.days_frame.grid_columnconfigure(i, weight=1, minsize=60)
        for i in range(6):  # 6 rows maximum for weeks
            self.days_frame.grid_rowconfigure(i, weight=1, minsize=40)
    
    def set_current_date(self, new_date: date):
        """Set the current date and update display only if month/year changed."""
        if (new_date.year != self.current_date.year or 
            new_date.month != self.current_date.month):
            self.current_date = new_date
            self.update_month_display()
        else:
            # Same month, just update current_date without full refresh
            self.current_date = new_date
            # Could add day highlighting logic here if needed in the future
    
    def update_month_display(self):
        """Update the calendar display for the current month."""
        # Clear existing day buttons
        for button in self.day_buttons.values():
            button.destroy()
        self.day_buttons.clear()
        
        # Get calendar data using itermonthdates (like year view)
        cal = calendar.Calendar(0)  # Monday as first day
        month_days = list(cal.itermonthdates(self.current_date.year, self.current_date.month))
        
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
                
                # Create day button
                if day_date.month == self.current_date.month:
                    # Day belongs to current month
                    day_text = str(day_date.day)
                    state = "normal"
                    command = lambda d=day_date: self.on_day_clicked(d)
                else:
                    # Day belongs to adjacent month (show as disabled without number)
                    day_text = ""
                    state = "disabled"
                    command = None
                
                day_button = tk.Button(
                    self.days_frame,
                    text=day_text,
                    font=("Arial", 9),
                    command=command,
                    relief=tk.RIDGE,
                    bd=1,
                    state=state
                )
                
                # Apply styling
                if day_date.month == self.current_date.month:
                    # Current month day - apply normal styling
                    self._apply_day_styling(day_button, day_date)
                    self.day_buttons[day_date] = day_button
                else:
                    # Adjacent month day - gray background, no interaction
                    day_button.config(bg="#f8f9fa", fg="#dee2e6")
                
                # Position button
                day_button.grid(row=week_idx, column=day_idx, sticky="nsew", padx=0, pady=0)
    
    def _apply_day_styling(self, button: tk.Button, button_date: date):
        """Apply styling to a day button based on classification and special dates."""
        default_color = "#ffffff"  # White default
        text_color = "black"
        
        # Get day classification color
        if self.timeline:
            day = self.timeline.get_day(button_date)
            if day and day.classification in self.CLASSIFICATION_COLORS:
                default_color = self.CLASSIFICATION_COLORS[day.classification]
        
        # Check for visa period start/end dates - override background color
        if self.timeline:
            visa_border = self.timeline.get_visa_border_info(button_date)
            if visa_border['is_visa_start']:
                default_color = self.VISA_BORDER_COLORS['start']  # Light purple
            elif visa_border['is_visa_end']:
                default_color = self.VISA_BORDER_COLORS['end']    # Dark purple
                text_color = "white"  # White text for better contrast on dark purple
        
        # Special date highlighting
        is_target_date = button_date in self.target_dates
        target_info = self.target_dates.get(button_date)
        
        if is_target_date and target_info:
            # Target completion date - use specific color based on target type, override classification color
            target_color = target_info.get('color', 'goldenrod')
            button.config(bg=target_color, fg="black", highlightbackground=target_color,
                         highlightcolor=target_color, highlightthickness=3, font=("Arial", 9, "bold"))
        elif button_date == date.today():
            # Today - red bold text with background (could be visa color or classification color)
            button.config(bg=default_color, fg="red", font=("Arial", 9, "bold"))
        else:
            # Normal day - use background color (could be visa color or classification color)
            button.config(bg=default_color, fg=text_color)
        
        # Disable future dates beyond timeline
        if self.timeline:
            timeline_info = self.timeline.get_date_range_info()
            if button_date > timeline_info.get('end_date', date.today()):
                button.config(state=tk.DISABLED, bg="#f8f9fa", fg="gray")
    
    def on_day_clicked(self, clicked_date: date):
        """Handle day button click."""
        old_date = self.current_date
        self.current_date = clicked_date
        
        # Only update display if we changed to a different month/year
        if (old_date.year != clicked_date.year or 
            old_date.month != clicked_date.month):
            self.update_month_display()
        
        # Notify parent via callback
        if self.date_selected_callback:
            self.date_selected_callback(clicked_date)
    
    def refresh_display(self):
        """Refresh the month calendar display."""
        self.update_month_display()
    
    def refresh_colors_only(self):
        """Refresh only the colors of existing buttons (more efficient than full rebuild)."""
        if not self.timeline:
            return
            
        for day, button in self.day_buttons.items():
            try:
                button_date = date(self.current_date.year, self.current_date.month, day)
                bg_color = self.get_day_color(button_date)
                button.config(bg=bg_color)
                
                # Update target date styling if applicable
                if button_date in self.target_dates:
                    target_info = self.target_dates[button_date]
                    button.config(fg=target_info.get('color', 'goldenrod'), font=("Arial", 8, "bold"))
                else:
                    button.config(fg="black", font=("Arial", 8))
                    
            except (ValueError, KeyError):
                continue
    
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