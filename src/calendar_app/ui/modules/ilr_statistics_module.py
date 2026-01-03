"""
ILR Statistics Module

Displays ILR statistics and progress tracking.
Occupies the top-left cell of the 2x2 grid layout.
"""

import tkinter as tk
from tkinter import ttk
from datetime import date, timedelta
from typing import Optional, Callable

from calendar_app.model.ilr_statistics import ILRStatisticsEngine, ILRStatistics


class ILRStatisticsModule(tk.Frame):
    """
    ILR Statistics module for displaying ILR progress and statistics.
    """
    
    def __init__(self, parent: tk.Widget, config=None, timeline=None, 
                 on_completion_date_click: Optional[Callable[[date], None]] = None,
                 on_highlight_target_dates: Optional[Callable[[list], None]] = None,
                 on_view_toggle: Optional[Callable[[str], None]] = None):
        """
        Initialize the ILR Statistics module.
        
        Args:
            parent: Parent widget
            config: AppConfig instance
            timeline: DateTimeline instance  
            on_completion_date_click: Callback for completion date clicks
            on_highlight_target_dates: Callback for highlighting target dates
            on_view_toggle: Callback for calendar view toggle (month/year)
        """
        super().__init__(parent, relief=tk.RAISED, bd=1, padx=10, pady=8)
        
        self.config = config
        self.timeline = timeline
        self.on_completion_date_click = on_completion_date_click
        self.on_highlight_target_dates = on_highlight_target_dates
        self.on_view_toggle = on_view_toggle
        
        # Current view mode
        self.current_view = "year"  # Default to year view
        
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
        # Main title and view toggle
        header_frame = tk.Frame(self, bg=self.cget("bg"))
        header_frame.pack(anchor=tk.W, fill=tk.X, pady=(0, 8))
        
        # Title on left
        title = tk.Label(header_frame, text="ILR Progress Tracking", 
                        font=("Arial", 12, "bold"), fg="navy",
                        bg=header_frame.cget("bg"))
        title.pack(side=tk.LEFT)
        
        # View toggle on right
        toggle_frame = tk.Frame(header_frame, bg=header_frame.cget("bg"))
        toggle_frame.pack(side=tk.RIGHT)
        
        self.month_toggle_btn = tk.Button(
            toggle_frame,
            text="Month",
            font=("Arial", 8),
            relief=tk.FLAT,
            bd=2,
            bg="white",
            fg="gray",
            width=6,
            command=lambda: self.toggle_view("month")
        )
        self.month_toggle_btn.pack(side=tk.LEFT, padx=(0, 2))
        
        self.year_toggle_btn = tk.Button(
            toggle_frame,
            text="Year",
            font=("Arial", 8),
            relief=tk.RAISED,
            bd=2,
            bg="#e3f2fd",
            fg="black",
            width=6,
            command=lambda: self.toggle_view("year")
        )
        self.year_toggle_btn.pack(side=tk.LEFT)
        
        # Configuration info section
        self.setup_config_info()
        
        # Separator
        separator = ttk.Separator(self, orient=tk.HORIZONTAL)
        separator.pack(fill=tk.X, pady=5)
        
        # Best Scenario - ORANGE title
        total_frame = tk.LabelFrame(self, text="Best Scenario (UK + Short Trips)", 
                                   font=("Arial", 10, "bold"), fg="darkorange")
        total_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.total_progress_label = tk.Label(total_frame, text="Loading...", 
                                            font=("Arial", 9))
        self.total_progress_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # Total remaining frame for combined display
        self.total_remaining_frame = tk.Frame(total_frame, bg=total_frame.cget("bg"))
        self.total_remaining_frame.pack(anchor=tk.W, padx=5, pady=2)
        
        self.total_remaining_label = tk.Label(self.total_remaining_frame, text="", 
                                             font=("Arial", 9), fg="darkgreen", bg=total_frame.cget("bg"))
        self.total_remaining_label.pack(side=tk.LEFT)
        
        self.total_covered_label = tk.Label(self.total_remaining_frame, text="", 
                                           font=("Arial", 9), fg="darkgreen", bg=total_frame.cget("bg"))
        self.total_covered_label.pack(side=tk.LEFT)
        
        self.total_plus_label = tk.Label(self.total_remaining_frame, text="", 
                                        font=("Arial", 9), fg="black", bg=total_frame.cget("bg"))
        self.total_plus_label.pack(side=tk.LEFT)
        
        self.total_uncovered_label = tk.Label(self.total_remaining_frame, text="", 
                                             font=("Arial", 9), fg="#cc7a7a", bg=total_frame.cget("bg"))
        self.total_uncovered_label.pack(side=tk.LEFT)
        
        # Total completion date (clickable) - Link styling with orange text
        self.total_completion_button = tk.Button(total_frame, text="", 
                                                font=("Arial", 9),
                                                relief=tk.FLAT, bd=0, cursor="hand2",
                                                fg="darkorange", bg=self.cget("bg"),
                                                command=self._on_total_completion_click)
        self.total_completion_button.pack(anchor=tk.W, padx=5, pady=2)
        
        # In-UK Scenario - YELLOW title
        uk_frame = tk.LabelFrame(self, text="Total Scenario", 
                                font=("Arial", 10, "bold"), fg="goldenrod")
        uk_frame.pack(fill=tk.X, pady=(0, 8))
        
        self.uk_progress_label = tk.Label(uk_frame, text="Loading...", 
                                         font=("Arial", 9))
        self.uk_progress_label.pack(anchor=tk.W, padx=5, pady=2)
        
        # UK remaining frame for combined display
        self.uk_remaining_frame = tk.Frame(uk_frame, bg=uk_frame.cget("bg"))
        self.uk_remaining_frame.pack(anchor=tk.W, padx=5, pady=2)
        
        self.uk_remaining_label = tk.Label(self.uk_remaining_frame, text="", 
                                          font=("Arial", 9), fg="darkgreen", bg=uk_frame.cget("bg"))
        self.uk_remaining_label.pack(side=tk.LEFT)
        
        self.uk_covered_label = tk.Label(self.uk_remaining_frame, text="", 
                                        font=("Arial", 9), fg="darkgreen", bg=uk_frame.cget("bg"))
        self.uk_covered_label.pack(side=tk.LEFT)
        
        self.uk_plus_label = tk.Label(self.uk_remaining_frame, text="", 
                                     font=("Arial", 9), fg="black", bg=uk_frame.cget("bg"))
        self.uk_plus_label.pack(side=tk.LEFT)
        
        self.uk_uncovered_label = tk.Label(self.uk_remaining_frame, text="", 
                                          font=("Arial", 9), fg="#cc7a7a", bg=uk_frame.cget("bg"))
        self.uk_uncovered_label.pack(side=tk.LEFT)
        
        # UK completion date (clickable) - Link styling with yellow text
        self.uk_completion_button = tk.Button(uk_frame, text="", 
                                             font=("Arial", 9),
                                             relief=tk.FLAT, bd=0, cursor="hand2",
                                             fg="goldenrod", bg=self.cget("bg"),
                                             command=self._on_uk_completion_click)
        self.uk_completion_button.pack(anchor=tk.W, padx=5, pady=2)
    
    def toggle_view(self, view_mode: str):
        """Toggle between month and year view."""
        if view_mode == self.current_view:
            return
            
        self.current_view = view_mode
        
        # Update button appearances
        if view_mode == "month":
            self.month_toggle_btn.config(relief=tk.RAISED, bg="#e3f2fd", fg="black")
            self.year_toggle_btn.config(relief=tk.FLAT, bg="white", fg="gray")
        else:
            self.month_toggle_btn.config(relief=tk.FLAT, bg="white", fg="gray")
            self.year_toggle_btn.config(relief=tk.RAISED, bg="#e3f2fd", fg="black")
        
        # Notify parent about view change
        if self.on_view_toggle:
            self.on_view_toggle(view_mode)
    
    def update_toggle_appearance(self, view_mode: str):
        """Update toggle button appearance without triggering callback."""
        if view_mode == self.current_view:
            return
            
        self.current_view = view_mode
        
        # Update button appearances only
        if view_mode == "month":
            self.month_toggle_btn.config(relief=tk.RAISED, bg="#e3f2fd", fg="black")
            self.year_toggle_btn.config(relief=tk.FLAT, bg="white", fg="gray")
        else:
            self.month_toggle_btn.config(relief=tk.FLAT, bg="white", fg="gray")
            self.year_toggle_btn.config(relief=tk.RAISED, bg="#e3f2fd", fg="black")
    
    def setup_config_info(self):
        """Set up the configuration information section."""
        config_frame = tk.LabelFrame(self, text="Configuration", 
                                    font=("Arial", 10, "bold"))
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        if self.config:
            # Objective years
            obj_label = tk.Label(config_frame, 
                               text=f"Objective: {self.config.objective_years} years", 
                               font=("Arial", 9), anchor="w")
            obj_label.pack(anchor=tk.W, padx=5, pady=1)
            
            # Processing buffer years
            if hasattr(self.config, 'processing_buffer_years'):
                buffer_label = tk.Label(config_frame,
                                      text=f"Processing Buffer: {self.config.processing_buffer_years} years",
                                      font=("Arial", 9), anchor="w")
                buffer_label.pack(anchor=tk.W, padx=5, pady=1)
            
            # Timeline years  
            timeline_label = tk.Label(config_frame,
                                    text=f"Timeline: {self.config.start_year} - {self.config.end_year}",
                                    font=("Arial", 9), anchor="w") 
            timeline_label.pack(anchor=tk.W, padx=5, pady=1)
            
            # First entry date
            entry_label = tk.Label(config_frame,
                                 text=f"First Entry: {self.config.first_entry_date}",
                                 font=("Arial", 9), anchor="w")
            entry_label.pack(anchor=tk.W, padx=5, pady=1)
            
            # Days since first entry (will be updated from statistics)
            self.days_since_label = tk.Label(config_frame,
                                            text="Days Since Entry: Calculating...",
                                            font=("Arial", 9), anchor="w")
            self.days_since_label.pack(anchor=tk.W, padx=5, pady=1)
    
    def refresh_statistics(self, calculation_date: Optional[date] = None):
        """Refresh the statistics display."""
        if not self.ilr_engine:
            self._show_error_state()
            return
            
        try:
            # Get current statistics
            self.current_stats = self.ilr_engine.get_global_statistics(calculation_date)
            
            # Update In-UK scenario
            uk_scenario = self.current_stats.in_uk_scenario
            uk_progress_text = f"Progress: {uk_scenario.days_completed:,} / {uk_scenario.days_required:,} days ({uk_scenario.percentage_complete:.1f}%)"
            self.uk_progress_label.config(text=uk_progress_text)
            
            if uk_scenario.is_complete:
                self.uk_remaining_label.config(text="✅ Requirement Complete!", fg="green")
                self.uk_uncovered_label.config(text="")
                self.uk_completion_button.config(text="", state=tk.DISABLED)
            else:
                # Get remaining days breakdown from backend
                breakdown = self.ilr_engine.get_remaining_days_breakdown(scenario="in_uk", calculation_date=calculation_date)
                
                if breakdown['uncovered_remaining'] > 0:
                    self.uk_remaining_label.config(text=f"Remaining: {breakdown['total_remaining']:,} days (", fg="black")
                    self.uk_covered_label.config(text=f"{breakdown['covered_remaining']:,}", fg="darkgreen")
                    self.uk_plus_label.config(text=" + ", fg="black")
                    self.uk_uncovered_label.config(text=f"{breakdown['uncovered_remaining']:,} days)")
                else:
                    self.uk_remaining_label.config(text=f"Remaining: {breakdown['total_remaining']:,} days", fg="black")
                    self.uk_covered_label.config(text="")
                    self.uk_plus_label.config(text="")
                    self.uk_uncovered_label.config(text="")
                    
                if uk_scenario.target_completion_date:
                    completion_text = f"Target: {uk_scenario.target_completion_date.strftime('%d-%m-%Y')}"
                    self.uk_completion_button.config(text=completion_text, state=tk.NORMAL)
                else:
                    self.uk_completion_button.config(text="", state=tk.DISABLED)
            
            # Update Total scenario
            total_scenario = self.current_stats.total_scenario
            total_progress_text = f"Progress: {total_scenario.days_completed:,} / {total_scenario.days_required:,} days ({total_scenario.percentage_complete:.1f}%)"
            self.total_progress_label.config(text=total_progress_text)
            
            if total_scenario.is_complete:
                self.total_remaining_label.config(text="✅ Requirement Complete!", fg="green")
                self.total_uncovered_label.config(text="")
                self.total_completion_button.config(text="", state=tk.DISABLED)
            else:
                # Get remaining days breakdown from backend
                breakdown = self.ilr_engine.get_remaining_days_breakdown(scenario="total", calculation_date=calculation_date)
                
                if breakdown['uncovered_remaining'] > 0:
                    self.total_remaining_label.config(text=f"Remaining: {breakdown['total_remaining']:,} days (", fg="black")
                    self.total_covered_label.config(text=f"{breakdown['covered_remaining']:,}", fg="darkgreen")
                    self.total_plus_label.config(text=" + ", fg="black")
                    self.total_uncovered_label.config(text=f"{breakdown['uncovered_remaining']:,} days)")
                else:
                    self.total_remaining_label.config(text=f"Remaining: {breakdown['total_remaining']:,} days", fg="black")
                    self.total_covered_label.config(text="")
                    self.total_plus_label.config(text="")
                    self.total_uncovered_label.config(text="")
                    
                if total_scenario.target_completion_date:
                    completion_text = f"Target: {total_scenario.target_completion_date.strftime('%d-%m-%Y')}"
                    self.total_completion_button.config(text=completion_text, state=tk.NORMAL)
                else:
                    self.total_completion_button.config(text="", state=tk.DISABLED)
            
            # Update days since entry from backend statistics
            if hasattr(self, 'days_since_label'):
                days_since_text = f"Days Since Entry: {self.current_stats.days_since_entry:,} days"
                self.days_since_label.config(text=days_since_text)
            
            # Highlight target dates in calendar
            self._update_target_highlighting()
            
        except Exception as e:
            self._show_error_state(str(e))
    
    def _show_error_state(self, error_msg: str = "Configuration not available"):
        """Show error state when data cannot be loaded."""
        self.uk_progress_label.config(text="Unable to load statistics")
        self.uk_remaining_label.config(text=error_msg)
        self.total_progress_label.config(text="Unable to load statistics")
        self.total_remaining_label.config(text=error_msg)
        self.uk_remaining_label.config(text="")
        self.total_progress_label.config(text="Unable to load statistics")  
        self.total_remaining_label.config(text="")
        if hasattr(self, 'days_since_label'):
            self.days_since_label.config(text="Days Since Entry: Not available")
        self.uk_completion_button.config(text="", state=tk.DISABLED)
        self.total_completion_button.config(text="", state=tk.DISABLED)
    
    def _on_uk_completion_click(self):
        """Handle click on UK completion date."""
        if (self.current_stats and 
            self.current_stats.in_uk_scenario.target_completion_date and 
            self.on_completion_date_click):
            target_date = self.current_stats.in_uk_scenario.target_completion_date
            self.on_completion_date_click(target_date)
    
    def _on_total_completion_click(self):
        """Handle click on Total completion date."""
        if (self.current_stats and 
            self.current_stats.total_scenario.target_completion_date and 
            self.on_completion_date_click):
            target_date = self.current_stats.total_scenario.target_completion_date
            self.on_completion_date_click(target_date)
    
    def update_config_and_timeline(self, config, timeline):
        """Update configuration and timeline references."""
        self.config = config
        self.timeline = timeline
        if config and timeline:
            self.ilr_engine = ILRStatisticsEngine(timeline, config)
            self.refresh_statistics()
            # Force target highlighting refresh after everything is set up
            self._update_target_highlighting()
    
    def force_target_highlighting_refresh(self):
        """Force a refresh of target date highlighting. Call this after UI setup is complete."""
        self._update_target_highlighting()
    
    def _update_target_highlighting(self):
        """Update target date highlighting in the calendar."""
        if not self.on_highlight_target_dates or not self.current_stats:
            return
        
        target_dates = {}
        
        # Add UK scenario target date (goldenrod)
        if (self.current_stats.in_uk_scenario.target_completion_date and 
            not self.current_stats.in_uk_scenario.is_complete):
            target_dates[self.current_stats.in_uk_scenario.target_completion_date] = {
                'type': 'uk_days',
                'color': 'goldenrod'
            }
        
        # Add Total scenario target date (darkorange) 
        if (self.current_stats.total_scenario.target_completion_date and 
            not self.current_stats.total_scenario.is_complete):
            target_dates[self.current_stats.total_scenario.target_completion_date] = {
                'type': 'total_days',
                'color': 'darkorange'
            }
        
        # Call highlight callback with typed target dates
        self.on_highlight_target_dates(target_dates)