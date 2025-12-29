"""
Month Info Module

Displays month-specific timeline information.
Occupies the bottom-left cell when in month view mode.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
import calendar
from typing import Optional

from calendar_app.model.timeline import DateTimeline
from calendar_app.model.day import DayClassification


class MonthInfoModule(tk.Frame):
    """
    Month information module for displaying month-specific timeline data.
    """
    
    def __init__(self, parent: tk.Widget, timeline: Optional[DateTimeline] = None):
        """
        Initialize the Month info module.
        
        Args:
            parent: Parent widget
            timeline: DateTimeline instance
        """
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.timeline = timeline
        self.current_date = date.today()
        
        # UI Components
        self.setup_ui()
        
        # Load initial data
        self.refresh_info()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main title
        self.title_label = tk.Label(self, text="Month Timeline", 
                                   font=("Arial", 12, "bold"), fg="navy")
        self.title_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Classification counts frame
        counts_frame = tk.LabelFrame(self, text="Day Classifications", 
                                    font=("Arial", 10, "bold"))
        counts_frame.pack(fill=tk.X, pady=(0, 8))
        
        # UK Residence days
        self.uk_days_label = tk.Label(counts_frame, text="", 
                                     font=("Arial", 9), fg="darkgreen")
        self.uk_days_label.pack(anchor=tk.W, padx=5, pady=1)
        
        # Short trip days  
        self.short_trip_label = tk.Label(counts_frame, text="", 
                                        font=("Arial", 9), fg="blue")
        self.short_trip_label.pack(anchor=tk.W, padx=5, pady=1)
        
        # Long trip days
        self.long_trip_label = tk.Label(counts_frame, text="", 
                                       font=("Arial", 9), fg="red")
        self.long_trip_label.pack(anchor=tk.W, padx=5, pady=1)
        
        # Pre-entry days
        self.pre_entry_label = tk.Label(counts_frame, text="", 
                                       font=("Arial", 9), fg="gray")
        self.pre_entry_label.pack(anchor=tk.W, padx=5, pady=1)
        
        # Total days
        self.total_days_label = tk.Label(counts_frame, text="", 
                                        font=("Arial", 9, "bold"))
        self.total_days_label.pack(anchor=tk.W, padx=5, pady=1)
    
    def set_current_date(self, new_date: date):
        """Update the current viewing date."""
        self.current_date = new_date
        self.refresh_info()
    
    def refresh_info(self):
        """Refresh the information display."""
        if not self.timeline:
            self._show_error_state()
            return
            
        try:
            # Get month classification counts from backend
            counts = self.timeline.get_classification_counts_for_month(
                self.current_date.year, self.current_date.month
            )
            
            # Extract counts from backend data
            uk_count = counts.get(DayClassification.UK_RESIDENCE, 0)
            short_trip_count = counts.get(DayClassification.SHORT_TRIP, 0)
            long_trip_count = counts.get(DayClassification.LONG_TRIP, 0)
            pre_entry_count = counts.get(DayClassification.PRE_ENTRY, 0)
            
            # Get trip statistics using existing trip classifier method
            from calendar import monthrange
            start_date = date(self.current_date.year, self.current_date.month, 1)
            end_date = date(self.current_date.year, self.current_date.month, monthrange(self.current_date.year, self.current_date.month)[1])
            trips_in_month = self.timeline.trip_classifier.get_trips_in_date_range(start_date, end_date)
            
            # Count trips by type
            short_trips = [trip for trip in trips_in_month if trip.get('is_short_trip', False)]
            long_trips = [trip for trip in trips_in_month if not trip.get('is_short_trip', False)]
            
            self.uk_days_label.config(text=f"UK Residence: {uk_count} days")
            self.short_trip_label.config(text=f"Short Trips: {len(short_trips)} trips - {short_trip_count} days")
            self.long_trip_label.config(text=f"Long Trips: {len(long_trips)} trips - {long_trip_count} days")
            self.pre_entry_label.config(text=f"Pre-Entry: {pre_entry_count} days")
            
            total_days = sum(counts.values())
            self.total_days_label.config(text=f"Total: {total_days} days")
            
        except Exception as e:
            self._show_error_state(str(e))
    
    def _show_error_state(self, error_msg: str = "Timeline not available"):
        """Show error state when data cannot be loaded."""
        self.uk_days_label.config(text="")
        self.short_trip_label.config(text="")
        self.long_trip_label.config(text="")
        self.pre_entry_label.config(text="")
        self.total_days_label.config(text="")
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference."""
        self.timeline = timeline
        self.refresh_info()