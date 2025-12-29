"""
Year Info Module - PLACEHOLDER

This is a placeholder for future implementation.
Currently not used in the ILR statistics focused interface.
"""

import tkinter as tk
from datetime import date
from typing import Optional

from calendar_app.model.timeline import DateTimeline
from calendar_app.model.day import DayClassification


class YearInfoModule(tk.Frame):
    """
    Year information module - PLACEHOLDER.
    This will be implemented in future iterations.
    """
    
    def __init__(self, parent: tk.Widget, timeline: Optional[DateTimeline] = None):
        """Initialize placeholder year info module."""
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.timeline = timeline
        self.current_date = date.today()
        
        # Placeholder UI
        placeholder_label = tk.Label(
            self, 
            text="Year Info Module\n(Future Implementation)", 
            font=("Arial", 10), 
            fg="gray"
        )
        placeholder_label.pack(expand=True)
    
    def set_current_date(self, current_date: date):
        """Placeholder method."""
        self.current_date = current_date
    
    def refresh_info(self):
        """Placeholder method."""
        pass
    
    def update_timeline(self, timeline: DateTimeline):
        """Placeholder method."""
        self.timeline = timeline
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main title
        self.title_label = tk.Label(self, text="Year Timeline", 
                                   font=("Arial", 12, "bold"), fg="navy")
        self.title_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Current year info
        self.year_label = tk.Label(self, text="", 
                                  font=("Arial", 10, "bold"), fg="darkblue")
        self.year_label.pack(anchor=tk.W, pady=(0, 8))
        
        # Separator
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)
        
        # Classification counts frame
        counts_frame = tk.LabelFrame(self, text="Year Classifications", 
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
        
        # Additional info separator
        separator2 = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator2.pack(fill=tk.X, pady=5)
        
        # Leap year info
        self.leap_year_label = tk.Label(self, text="", 
                                       font=("Arial", 9), fg="orange")
        self.leap_year_label.pack(anchor=tk.W, pady=2)
        
        # Context info
        self.context_label = tk.Label(self, text="", 
                                     font=("Arial", 9), fg="purple")
        self.context_label.pack(anchor=tk.W)
    
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
            # Update year label
            year_text = f"📅 Year {self.current_date.year}"
            self.year_label.config(text=year_text)
            
            # Get year classification counts from backend
            counts = self.timeline.get_classification_counts_for_year(self.current_date.year)
            
            # Extract counts from backend data
            uk_count = counts.get(DayClassification.UK_RESIDENCE, 0)
            short_trip_count = counts.get(DayClassification.SHORT_TRIP, 0)
            long_trip_count = counts.get(DayClassification.LONG_TRIP, 0)
            pre_entry_count = counts.get(DayClassification.PRE_ENTRY, 0)
            
            # Get trip statistics using existing trip classifier method
            start_date = date(self.current_date.year, 1, 1)
            end_date = date(self.current_date.year, 12, 31)
            trips_in_year = self.timeline.trip_classifier.get_trips_in_date_range(start_date, end_date)
            
            # Count trips by type
            short_trips = [trip for trip in trips_in_year if trip.get('is_short_trip', False)]
            long_trips = [trip for trip in trips_in_year if not trip.get('is_short_trip', False)]
            
            self.uk_days_label.config(text=f"UK Residence: {uk_count} days")
            self.short_trip_label.config(text=f"Short Trips: {len(short_trips)} trips - {short_trip_count} days")
            self.long_trip_label.config(text=f"Long Trips: {len(long_trips)} trips - {long_trip_count} days")
            self.pre_entry_label.config(text=f"Pre-Entry: {pre_entry_count} days")
            
            total_days = sum(counts.values())
            self.total_days_label.config(text=f"Total: {total_days} days")
            
            # Leap year info
            import calendar
            is_leap = calendar.isleap(self.current_date.year)
            leap_text = f"🗓️  {'Leap year' if is_leap else 'Regular year'} ({total_days} days)"
            self.leap_year_label.config(text=leap_text)
            
            # Update context
            timeline_info = self.timeline.get_date_range_info()
            context_text = f"Year {self.current_date.year} of timeline ({timeline_info['total_days']:,} total days)"
            self.context_label.config(text=context_text)
            
        except Exception as e:
            self._show_error_state(str(e))
    
    def _show_error_state(self, error_msg: str = "Timeline not available"):
        """Show error state when data cannot be loaded."""
        self.year_label.config(text="Unable to load year info")
        self.uk_days_label.config(text="")
        self.short_trip_label.config(text="")
        self.long_trip_label.config(text="")
        self.pre_entry_label.config(text="")
        self.total_days_label.config(text="")
        self.leap_year_label.config(text="")
        self.context_label.config(text=error_msg)
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference."""
        self.timeline = timeline
        self.refresh_info()