"""
ILR Statistics Panel Component

Displays ILR statistics including dual scenarios (In-UK vs Total) with progress tracking.
Part of the 2x2 grid layout system - occupies the top-left cell.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from typing import Optional, Callable

from calendar_app.model.ilr_statistics import ILRStatisticsEngine, ILRStatistics


class StatisticsPanel(tk.Frame):
    """
    ILR Statistics panel for the top-left cell of the 2x2 grid.
    
    Displays:
    - ILR requirement overview
    - In-UK scenario progress 
    - Total scenario progress
    - Clickable completion dates that navigate to specific dates
    """
    
    def __init__(self, parent: tk.Widget, config=None, timeline=None, 
                 on_date_click: Optional[Callable[[date], None]] = None):
        """
        Initialize the ILR Statistics panel.
        
        Args:
            parent: Parent widget
            config: AppConfig instance
            timeline: DateTimeline instance  
            on_date_click: Callback for when completion date is clicked
        """
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.config = config
        self.timeline = timeline
        self.on_date_click = on_date_click
        
        # ILR Statistics Engine
        self.ilr_engine = None
        if config and timeline:
            self.ilr_engine = ILRStatisticsEngine(timeline, config)
        
        # Current statistics
        self.current_stats: Optional[ILRStatistics] = None
        
        # UI Components
        self.setup_ui()
        
        # Load initial data
        self.refresh_statistics()
    
    def setup_ui(self):
        """Set up the UI components."""
        # Main title
        title = tk.Label(self, text="ILR Statistics", 
                        font=("Arial", 12, "bold"), fg="navy")
        title.pack(anchor=tk.W, pady=(0, 8))
        
        # Requirement info frame
        req_frame = tk.Frame(self)
        req_frame.pack(fill=tk.X, pady=(0, 10))
        
        self.req_label = tk.Label(req_frame, text="Loading requirement info...", 
                                 font=("Arial", 9), fg="gray")
        self.req_label.pack(anchor=tk.W)
        
        # Separator
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)
        
        # Total Scenario
        total_frame = tk.LabelFrame(self, text="Total Scenario (UK + Short Trips)", 
                                   font=("Arial", 10, "bold"), fg="darkgreen")
        total_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.total_progress_label = tk.Label(total_frame, text="Loading...", 
                                            font=("Arial", 9))
        self.total_progress_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.total_remaining_label = tk.Label(total_frame, text="", 
                                             font=("Arial", 9))
        self.total_remaining_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Total completion date (clickable)
        self.total_completion_button = tk.Button(total_frame, text="", 
                                                font=("Arial", 9, "underline"),
                                                relief=tk.FLAT, bd=0, cursor="hand2",
                                                fg="darkorange", bg=self.cget("bg"),
                                                command=self.on_total_completion_click)
        self.total_completion_button.pack(anchor=tk.W, padx=5, pady=2)
        
        # In-UK Scenario
        uk_frame = tk.LabelFrame(self, text="In-UK Scenario", 
                                font=("Arial", 10, "bold"), fg="darkblue")
        uk_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.uk_progress_label = tk.Label(uk_frame, text="Loading...", 
                                         font=("Arial", 9))
        self.uk_progress_label.pack(anchor=tk.W, padx=5, pady=2)
        
        self.uk_remaining_label = tk.Label(uk_frame, text="", 
                                          font=("Arial", 9))
        self.uk_remaining_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # UK completion date (clickable)
        self.uk_completion_button = tk.Button(uk_frame, text="", 
                                             font=("Arial", 9, "underline"),
                                             relief=tk.FLAT, bd=0, cursor="hand2",
                                             fg="orange", bg=self.cget("bg"),
                                             command=self.on_uk_completion_click)
        self.uk_completion_button.pack(anchor=tk.W, padx=5, pady=2)
        
        # Days since entry
        self.days_since_label = tk.Label(self, text="", 
                                        font=("Arial", 9), fg="gray")
        self.days_since_label.pack(anchor=tk.W, pady=(8, 0))
    
    def refresh_statistics(self, calculation_date: Optional[date] = None):
        """
        Refresh the statistics display.
        
        Args:
            calculation_date: Date to calculate statistics for (default: today)
        """
        if not self.ilr_engine:
            self.show_error_state()
            return
            
        try:
            # Get current statistics
            self.current_stats = self.ilr_engine.get_global_statistics(calculation_date)
            
            # Update requirement info
            req_info = self.ilr_engine.get_ilr_requirement_info()
            req_text = f"Requirement: {req_info['days_required']:,} days ({req_info['objective_years']} years)"
            req_text += f"\nFirst Entry: {req_info['first_entry_date']}"
            self.req_label.config(text=req_text)
            
            # Update In-UK scenario
            uk_scenario = self.current_stats.in_uk_scenario
            uk_progress_text = f"Progress: {uk_scenario.days_completed:,} / {uk_scenario.days_required:,} days ({uk_scenario.percentage_complete:.1f}%)"
            self.uk_progress_label.config(text=uk_progress_text)
            
            if uk_scenario.is_complete:
                self.uk_remaining_label.config(text="✅ Requirement Complete!", fg="green")
                self.uk_completion_button.config(text="", state=tk.DISABLED)
            else:
                self.uk_remaining_label.config(text=f"Remaining: {uk_scenario.days_remaining:,} days", fg="red")
                if uk_scenario.target_completion_date:
                    completion_text = f"📅 Target: {uk_scenario.target_completion_date.strftime('%d-%m-%Y')}"
                    self.uk_completion_button.config(text=completion_text, state=tk.NORMAL, bg="lightyellow")
                else:
                    self.uk_completion_button.config(text="", state=tk.DISABLED)
            
            # Update Total scenario
            total_scenario = self.current_stats.total_scenario
            total_progress_text = f"Progress: {total_scenario.days_completed:,} / {total_scenario.days_required:,} days ({total_scenario.percentage_complete:.1f}%)"
            self.total_progress_label.config(text=total_progress_text)
            
            if total_scenario.is_complete:
                self.total_remaining_label.config(text="✅ Requirement Complete!", fg="green")
                self.total_completion_button.config(text="", state=tk.DISABLED)
            else:
                self.total_remaining_label.config(text=f"Remaining: {total_scenario.days_remaining:,} days", fg="red")
                if total_scenario.target_completion_date:
                    completion_text = f"📅 Target: {total_scenario.target_completion_date.strftime('%d-%m-%Y')}"
                    self.total_completion_button.config(text=completion_text, state=tk.NORMAL, bg="moccasin")
                else:
                    self.total_completion_button.config(text="", state=tk.DISABLED)
            
            # Update days since entry
            days_since_text = f"Days since first entry: {self.current_stats.days_since_entry:,}"
            self.days_since_label.config(text=days_since_text)
            
        except Exception as e:
            self.show_error_state(str(e))
    
    def show_error_state(self, error_msg: str = "Configuration not available"):
        """Show error state when data cannot be loaded."""
        self.req_label.config(text=error_msg)
        self.uk_progress_label.config(text="Unable to load statistics")
        self.uk_remaining_label.config(text="")
        self.total_progress_label.config(text="Unable to load statistics")  
        self.total_remaining_label.config(text="")
        self.days_since_label.config(text="")
        self.uk_completion_button.config(text="", state=tk.DISABLED)
        self.total_completion_button.config(text="", state=tk.DISABLED)
    
    def on_uk_completion_click(self):
        """Handle click on UK completion date."""
        if (self.current_stats and 
            self.current_stats.in_uk_scenario.target_completion_date and 
            self.on_date_click):
            target_date = self.current_stats.in_uk_scenario.target_completion_date
            self.on_date_click(target_date)
    
    def on_total_completion_click(self):
        """Handle click on Total completion date."""
        if (self.current_stats and 
            self.current_stats.total_scenario.target_completion_date and 
            self.on_date_click):
            target_date = self.current_stats.total_scenario.target_completion_date
            self.on_date_click(target_date)
    
    def update_config_and_timeline(self, config, timeline):
        """Update configuration and timeline references."""
        self.config = config
        self.timeline = timeline
        if config and timeline:
            self.ilr_engine = ILRStatisticsEngine(timeline, config)
            self.refresh_statistics()
        else:
            self.show_error_state()