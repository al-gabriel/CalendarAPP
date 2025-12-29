"""
Day Info Module - PLACEHOLDER

This is a placeholder for future implementation.
Currently not used in the ILR statistics focused interface.
"""

import tkinter as tk
from datetime import date
from typing import Optional

from calendar_app.model.timeline import DateTimeline


class DayInfoModule(tk.Frame):
    """
    Day information module - PLACEHOLDER.
    This will be implemented in future iterations.
    """
    
    def __init__(self, parent: tk.Widget, timeline: Optional[DateTimeline] = None):
        """Initialize placeholder day info module."""
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.timeline = timeline
        self.selected_date = date.today()
        
        # Placeholder UI
        placeholder_label = tk.Label(
            self, 
            text="Day Info Module\n(Future Implementation)", 
            font=("Arial", 10), 
            fg="gray"
        )
        placeholder_label.pack(expand=True)
    
    def set_selected_date(self, selected_date: date):
        """Placeholder method."""
        self.selected_date = selected_date
    
    def refresh_info(self):
        """Placeholder method."""
        pass
    
    def update_timeline(self, timeline: DateTimeline):
        """Placeholder method."""
        self.timeline = timeline