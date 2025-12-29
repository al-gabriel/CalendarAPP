"""
Month/Year Info Panel Component

Displays current month/year information and timeline details.
Part of the 2x2 grid layout system - occupies the bottom-left cell.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
import calendar
from typing import Optional, Callable

from calendar_app.model.timeline import DateTimeline
from calendar_app.model.day import DayClassification
from calendar_app.model.day import DayClassification


class MonthYearInfoPanel(tk.Frame):
    """
    Month/Year information panel for the bottom-left cell of the 2x2 grid.
    
    Displays:
    - Current viewing date (month/year)
    - Timeline information for the current view
    - Classification counts for current month/year
    - Navigation context
    """
    
    def __init__(self, parent: tk.Widget, timeline: Optional[DateTimeline] = None):
        """
        Initialize the Month/Year info panel.
        
        Args:
            parent: Parent widget
            timeline: DateTimeline instance
        """
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.timeline = timeline
        self.current_date = date.today()
        self.view_mode = "month"  # "month" or "year"
        
        # UI Components
        self.setup_ui()
        
        # Load initial data
        self.refresh_info()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main title
        self.title_label = tk.Label(self, text="Timeline Info", 
                                   font=("Arial", 12, "bold"), fg="navy")
        self.title_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Current viewing info
        self.viewing_label = tk.Label(self, text="", 
                                     font=("Arial", 10, "bold"), fg="darkblue")
        self.viewing_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Separator
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)
        
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
        
        # Additional timeline info
        separator2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator2.pack(fill=tk.X, pady=5)
        
        # Timeline range info
        self.range_label = tk.Label(self, text="", 
                                   font=("Arial", 9), fg="gray")
        self.range_label.pack(anchor=tk.W, pady=(0, 4))
        
        # View context
        self.context_label = tk.Label(self, text="", 
                                     font=("Arial", 9), fg="purple")
        self.context_label.pack(anchor=tk.W)
    
    def set_current_date(self, new_date: date, view_mode: str = "month"):
        """
        Update the current viewing date and mode.
        
        Args:
            new_date: New date to display info for
            view_mode: "month" or "year"
        """
        self.current_date = new_date
        self.view_mode = view_mode
        self.refresh_info()
    
    def refresh_info(self):
        """Refresh the information display."""
        if not self.timeline:
            self.show_error_state()
            return
            
        try:
            # Update viewing label
            if self.view_mode == "month":
                viewing_text = f"📅 {calendar.month_name[self.current_date.month]} {self.current_date.year}"
                self.viewing_label.config(text=viewing_text)
                
                # Get month classification counts from backend
                counts = self.timeline.get_classification_counts_for_month(
                    self.current_date.year, self.current_date.month
                )
                
            else:  # year mode
                viewing_text = f"📅 Year {self.current_date.year}"
                self.viewing_label.config(text=viewing_text)
                
                # Get year classification counts from backend
                counts = self.timeline.get_classification_counts_for_year(self.current_date.year)
            
            # Extract counts from backend data
            uk_count = counts.get(DayClassification.UK_RESIDENCE, 0)
            short_trip_count = counts.get(DayClassification.SHORT_TRIP, 0)
            long_trip_count = counts.get(DayClassification.LONG_TRIP, 0)
            pre_entry_count = counts.get(DayClassification.PRE_ENTRY, 0)
            
            # Update count labels
            self.uk_days_label.config(text=f"🏠 UK Residence: {uk_count} days")
            self.short_trip_label.config(text=f"✈️  Short Trips: {short_trip_count} days")
            self.long_trip_label.config(text=f"🌍 Long Trips: {long_trip_count} days")
            self.pre_entry_label.config(text=f"⏳ Pre-Entry: {pre_entry_count} days")
            
            total_days = sum(counts.values())
            self.total_days_label.config(text=f"📊 Total: {total_days} days")
            
            # Update timeline range info
            range_info = self.timeline.get_date_range_info()
            range_text = f"Timeline: {range_info['start_date'].strftime('%d-%m-%Y')} to {range_info['end_date'].strftime('%d-%m-%Y')}"
            self.range_label.config(text=range_text)
            
            # Update context
            if self.view_mode == "month":
                context_text = f"Viewing month {self.current_date.month} of {range_info['total_days']:,} total days"
            else:
                context_text = f"Viewing year with {total_days} days of {range_info['total_days']:,} total days"
            
            self.context_label.config(text=context_text)
            
        except Exception as e:
            self.show_error_state(str(e))
    
    def show_error_state(self, error_msg: str = "Timeline not available"):
        """Show error state when data cannot be loaded."""
        self.viewing_label.config(text="Unable to load timeline info")
        self.uk_days_label.config(text="")
        self.short_trip_label.config(text="")
        self.long_trip_label.config(text="")
        self.pre_entry_label.config(text="")
        self.total_days_label.config(text="")
        self.range_label.config(text=error_msg)
        self.context_label.config(text="")
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference."""
        self.timeline = timeline
        self.refresh_info()