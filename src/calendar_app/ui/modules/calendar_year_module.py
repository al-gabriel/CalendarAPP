"""
Calendar Year Module - PLACEHOLDER

This is a placeholder for future implementation.
Currently not used in the ILR statistics focused interface.
"""

import tkinter as tk
from datetime import date
from typing import Optional, Callable

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline


class CalendarYearModule(tk.Frame):
    """
    Year calendar module - PLACEHOLDER.
    This will be implemented in future iterations.
    """
    
    def __init__(self, parent: tk.Widget, config: Optional[AppConfig] = None,
                 timeline: Optional[DateTimeline] = None,
                 month_selected_callback: Optional[Callable[[date], None]] = None):
        """Initialize placeholder year calendar module."""
        super().__init__(parent, bg="white")
        
        self.config = config
        self.timeline = timeline
        self.month_selected_callback = month_selected_callback
        self.current_date = date.today()
        
        # Placeholder UI
        placeholder_label = tk.Label(
            self, 
            text="Year Calendar Module\n(Future Implementation)", 
            font=("Arial", 12), 
            fg="gray",
            bg="white"
        )
        placeholder_label.pack(expand=True)
    
    def set_current_date(self, new_date: date):
        """Placeholder method."""
        self.current_date = new_date
    
    def refresh_display(self):
        """Placeholder method."""
        pass
    
    def update_timeline(self, timeline: DateTimeline):
        """Placeholder method."""
        self.timeline = timeline