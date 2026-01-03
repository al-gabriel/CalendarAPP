"""
Day Info Module

Displays detailed information about a selected day including date, classification,
trip information, visa period information, and clickable navigation.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date
from typing import Optional, Callable

from calendar_app.model.timeline import DateTimeline
from calendar_app.model.day import DayClassification


class DayInfoModule(tk.Frame):
    """
    Day Info module for displaying detailed day information.
    
    Shows:
    - Date and day classification
    - Trip information (if day is part of a trip)
    - Visa period information (if day has visa coverage)  
    - Clickable dates for calendar navigation
    """
    
    def __init__(self, parent: tk.Widget, timeline: Optional[DateTimeline] = None,
                 on_date_click: Optional[Callable[[date], None]] = None,
                 on_back_click: Optional[Callable[[], None]] = None):
        """Initialize the Day Info module."""
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=5, pady=4)
        
        self.timeline = timeline
        self.selected_date: Optional[date] = None
        self.on_date_click = on_date_click
        self.on_back_click = on_back_click
        
        # Setup UI
        self.setup_ui()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Header frame with title and back button
        header_frame = tk.Frame(self)
        header_frame.pack(fill=tk.X, pady=(0, 4))
        
        # Main title with integrated date - will be updated when date is selected
        self.title_label = tk.Label(header_frame, text="Day Information", 
                                   font=("Arial", 12, "bold"), fg="navy")
        self.title_label.pack(side=tk.LEFT, anchor=tk.W)
        
        # Back button in top right corner
        if self.on_back_click:
            back_button = tk.Button(header_frame, text="Back", 
                                   font=("Arial", 10), relief=tk.RAISED, bd=1,
                                   cursor="hand2", fg="black", bg="#e0e0e0",
                                   command=self.on_back_click)
            back_button.pack(side=tk.RIGHT)
        
        # Main content frame
        self.content_frame = tk.Frame(self)
        self.content_frame.pack(fill=tk.BOTH, expand=True, anchor=tk.W)
        
        # Initial message
        self.setup_empty_state()
    
    def setup_empty_state(self):
        """Show message when no date is selected."""
        self.clear_content()
        
        empty_label = tk.Label(self.content_frame, 
                              text="Select a day from the calendar to view details", 
                              font=("Arial", 11), fg="gray")
        empty_label.pack(anchor=tk.W, pady=5)
    
    def clear_content(self):
        """Clear all content from the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()
    
    def set_selected_date(self, selected_date: date):
        """
        Set the selected date for this module.
        
        Args:
            selected_date: The date to display information for
        """
        self.selected_date = selected_date
        self.refresh_info()
    
    def refresh_info(self):
        """Refresh the day information display."""
        if self.selected_date is None or self.timeline is None:
            self.setup_empty_state()
            return
        
        # Get day information from timeline
        day_obj = self.timeline.days.get(self.selected_date)
        if day_obj is None:
            self.show_date_not_found()
            return
        
        # Clear previous content and show day details
        self.clear_content()
        self.show_day_details(day_obj)
    
    def show_date_not_found(self):
        """Show message when selected date is not found in timeline."""
        self.clear_content()
        
        error_label = tk.Label(self.content_frame, 
                              text=f"Date {self.selected_date.strftime('%d-%m-%Y')} not found in timeline", 
                              font=("Arial", 11), fg="red")
        error_label.pack(anchor=tk.W, pady=5)
    
    def show_day_details(self, day_obj):
        """
        Show detailed information for a day.
        
        Args:
            day_obj: Day object containing all day information
        """
        # Update title with date
        date_str = day_obj.date.strftime('%d %B %Y')
        self.title_label.config(text=f"Day Information - {date_str}")
        
        # Classification section - simplified
        self.show_classification_section(day_obj)
        
        # Trip information section (if applicable)
        if day_obj.trip_info is not None:
            self.show_trip_section(day_obj)
        
        # Visa period information section (if applicable)
        if day_obj.visaPeriod_info is not None:
            self.show_visa_section(day_obj)
    
    def show_classification_section(self, day_obj):
        """Show the day classification information."""
        # Create frame for classification with mixed colors
        class_frame = tk.Frame(self.content_frame)
        class_frame.pack(fill=tk.X, anchor=tk.W, pady=(0, 3))
        
        # "Classification:" label in black
        class_label_text = tk.Label(class_frame, text="Classification: ",
                                   font=("Arial", 11, "bold"), fg="black")
        class_label_text.pack(side=tk.LEFT)
        
        # Classification value with color coding
        classification_text = self.get_classification_display_text(day_obj.classification)
        classification_color = self.get_classification_color(day_obj.classification)
        
        class_value = tk.Label(class_frame, text=classification_text,
                              font=("Arial", 11, "bold"), fg=classification_color)
        class_value.pack(side=tk.LEFT)
    
    def show_trip_section(self, day_obj):
        """Show trip information if day is part of a trip."""
        trip_info = day_obj.trip_info
        
        # Frame title with trip type and length
        trip_type = "Short trip" if trip_info.get("is_short_trip", False) else "Long trip"
        length_days = trip_info.get('trip_length_days', 'Unknown')
        frame_title = f"{trip_type} - {length_days} days"
        
        trip_frame = tk.LabelFrame(self.content_frame, text=frame_title, 
                                  font=("Arial", 11, "bold"), fg="blue")
        trip_frame.pack(fill=tk.X, pady=(0, 3))
        
        # Departure date with flight route
        departure_date = trip_info.get("departure_date")
        outbound_flight = trip_info.get("outbound_flight", "???")
        if departure_date:
            dep_frame = tk.Frame(trip_frame)
            dep_frame.pack(fill=tk.X, padx=3, pady=1)
            
            # Use fixed width for "Outbound:" label for alignment
            dep_label = tk.Label(dep_frame, text="Out:", font=("Arial", 10), fg="black", width=5, anchor="w")
            dep_label.pack(side=tk.LEFT)
            
            flight_label = tk.Label(dep_frame, text=f"{outbound_flight} - ", font=("Courier New", 10), fg="black")
            flight_label.pack(side=tk.LEFT)
            
            dep_button = tk.Button(dep_frame, text=departure_date.strftime('%d-%m-%Y'),
                                  font=("Arial", 10), relief=tk.FLAT, bd=0, 
                                  cursor="hand2", fg="darkblue", bg=self.cget("bg"),
                                  command=lambda: self._on_date_button_click(departure_date))
            dep_button.pack(side=tk.LEFT)
        
        # Return date with flight route
        return_date = trip_info.get("return_date")
        inbound_flight = trip_info.get("inbound_flight", "???")
        if return_date:
            ret_frame = tk.Frame(trip_frame)
            ret_frame.pack(fill=tk.X, padx=3, pady=1)
            
            # Use fixed width for "Inbound:" label for alignment  
            ret_label = tk.Label(ret_frame, text="In:", font=("Arial", 10), fg="black", width=5, anchor="w")
            ret_label.pack(side=tk.LEFT)
            
            flight_label = tk.Label(ret_frame, text=f"{inbound_flight} - ", font=("Courier New", 10), fg="black")
            flight_label.pack(side=tk.LEFT)
            
            ret_button = tk.Button(ret_frame, text=return_date.strftime('%d-%m-%Y'),
                                  font=("Arial", 10), relief=tk.FLAT, bd=0,
                                  cursor="hand2", fg="darkblue", bg=self.cget("bg"),
                                  command=lambda: self._on_date_button_click(return_date))
            ret_button.pack(side=tk.LEFT)
    
    def show_visa_section(self, day_obj):
        """Show visa period information if day has visa coverage."""
        visa_info = day_obj.visaPeriod_info
        
        # Frame title with visa label or ID
        visa_label = visa_info.get("visaPeriod_label")
        visa_id = visa_info.get("visaPeriod_id")
        frame_title = visa_label if visa_label else (visa_id if visa_id else "Visa period")
        
        visa_frame = tk.LabelFrame(self.content_frame, text=frame_title, 
                                  font=("Arial", 11, "bold"), fg="purple")
        visa_frame.pack(fill=tk.X, pady=(0, 3))
        
        # Start date with better alignment
        start_date = visa_info.get("start_date")
        if start_date:
            start_frame = tk.Frame(visa_frame)
            start_frame.pack(fill=tk.X, padx=3, pady=1)
            
            # Use fixed width for "From:" label for alignment
            start_label = tk.Label(start_frame, text="From:", font=("Arial", 10), fg="black", width=5, anchor="w")
            start_label.pack(side=tk.LEFT)
            
            start_button = tk.Button(start_frame, text=visa_info['start_date'].strftime('%d-%m-%Y'),
                                    font=("Arial", 10), relief=tk.FLAT, bd=0,
                                    cursor="hand2", fg="darkblue", bg=self.cget("bg"),
                                    command=lambda: self._on_date_button_click(start_date))
            start_button.pack(side=tk.LEFT)
        
        # End date with better alignment
        end_date = visa_info.get("end_date")
        if end_date:
            end_frame = tk.Frame(visa_frame)
            end_frame.pack(fill=tk.X, padx=3, pady=1)
            
            # Use fixed width for "To:" label for alignment
            end_label = tk.Label(end_frame, text="To:", font=("Arial", 10), fg="black", width=5, anchor="w")
            end_label.pack(side=tk.LEFT)
            
            end_button = tk.Button(end_frame, text=visa_info['end_date'].strftime('%d-%m-%Y'),
                                  font=("Arial", 10), relief=tk.FLAT, bd=0,
                                  cursor="hand2", fg="darkblue", bg=self.cget("bg"),
                                  command=lambda: self._on_date_button_click(end_date))
            end_button.pack(side=tk.LEFT)
    
    def get_classification_display_text(self, classification: DayClassification) -> str:
        """Get human-readable text for day classification."""
        classification_names = {
            DayClassification.UK_RESIDENCE: "UK Residence Day",
            DayClassification.SHORT_TRIP: "Short Trip Day",
            DayClassification.LONG_TRIP: "Long Trip Day", 
            DayClassification.NO_VISA_COVERAGE: "No Visa Coverage Day",
            DayClassification.PRE_ENTRY: "Pre-Entry Day",
            DayClassification.UNKNOWN: "Unknown Classification"
        }
        return classification_names.get(classification, "Unknown")
    
    def get_classification_color(self, classification: DayClassification) -> str:
        """Get color coding for day classification."""
        classification_colors = {
            DayClassification.UK_RESIDENCE: "darkgreen",
            DayClassification.SHORT_TRIP: "darkblue",
            DayClassification.LONG_TRIP: "red",
            DayClassification.NO_VISA_COVERAGE: "darkred",
            DayClassification.PRE_ENTRY: "gray", 
            DayClassification.UNKNOWN: "black"
        }
        return classification_colors.get(classification, "black")
    
    def get_classification_description(self, classification: DayClassification) -> str:
        """Get description for day classification."""
        descriptions = {
            DayClassification.UK_RESIDENCE: "Counts toward ILR requirement",
            DayClassification.SHORT_TRIP: "Trip <14 days - counts toward ILR",
            DayClassification.LONG_TRIP: "Trip ≥14 days - does not count toward ILR",
            DayClassification.NO_VISA_COVERAGE: "Counts toward ILR but needs visa coverage",
            DayClassification.PRE_ENTRY: "Before first UK entry date",
            DayClassification.UNKNOWN: "Classification not determined"
        }
        return descriptions.get(classification, "")
    
    def _on_date_button_click(self, clicked_date: date):
        """Handle click on any date button."""
        if self.on_date_click:
            self.on_date_click(clicked_date)
    
    def update_config_and_timeline(self, config, timeline):
        """Update configuration and timeline references."""
        self.timeline = timeline
        self.refresh_info()