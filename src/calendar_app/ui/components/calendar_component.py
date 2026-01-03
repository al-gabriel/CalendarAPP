"""
Calendar Component

Main calendar component that combines NavigationHeader with calendar modules.
This replaces the old calendar_module.py and handles switching between month/year views.
"""

import tkinter as tk
from datetime import date
from typing import Optional, Callable

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline
from calendar_app.ui.components.navigation_header import NavigationHeader
from calendar_app.ui.modules.calendar_month_module import CalendarMonthModule
from calendar_app.ui.modules.calendar_year_module import CalendarYearModule


class CalendarComponent(tk.Frame):
    """
    Calendar component managing navigation and calendar views.
    
    Structure:
    - Top: NavigationHeader (date navigation, view switching)
    - Bottom: Current calendar view (month or year module)
    
    This goes in the right side of the 2x2 grid layout.
    """
    
    def __init__(self, parent: tk.Widget, config: Optional[AppConfig] = None,
                 timeline: Optional[DateTimeline] = None,
                 date_changed_callback: Optional[Callable[[date], None]] = None,
                 view_changed_callback: Optional[Callable[[str], None]] = None,
                 date_selected_callback: Optional[Callable[[date], None]] = None):
        """
        Initialize calendar component.
        
        Args:
            parent: Parent widget
            config: Application configuration
            timeline: DateTimeline instance
            date_changed_callback: Called when date changes
            view_changed_callback: Called when view mode changes
            date_selected_callback: Called when a date is selected
        """
        super().__init__(parent, relief=tk.RAISED, bd=1, bg="white")
        
        self.config = config
        self.timeline = timeline
        self.date_changed_callback = date_changed_callback
        self.view_changed_callback = view_changed_callback
        self.date_selected_callback = date_selected_callback
        
        # State
        self.current_date = date.today()
        self.current_view_mode = "year"  # "month" or "year" - default to year view
        
        # Components
        self.navigation_header = None
        self.calendar_container = None
        self.current_calendar_module = None
        
        # Calendar modules
        self.month_module = None
        self.year_module = None
        
        # Setup
        self.setup_component()
    
    def setup_component(self):
        """Set up the calendar component."""
        # Configure grid layout
        self.grid_rowconfigure(0, weight=0)  # Header
        self.grid_rowconfigure(1, weight=1)  # Calendar
        self.grid_columnconfigure(0, weight=1)
        
        # Navigation header
        self.navigation_header = NavigationHeader(
            self,
            config=self.config,
            timeline=self.timeline
        )
        
        # Set up navigation callbacks
        self.navigation_header.on_date_changed = self._on_navigation_date_change
        self.navigation_header.on_first_entry_clicked = self._on_first_entry_click
        self.navigation_header.on_uk_target_clicked = self._on_uk_target_click
        self.navigation_header.on_total_target_clicked = self._on_total_target_click
        self.navigation_header.on_today_clicked = self._on_today_click
        self.navigation_header.on_prev_month = self._on_prev_month
        self.navigation_header.on_next_month = self._on_next_month
        self.navigation_header.on_prev_year = self._on_prev_year
        self.navigation_header.on_next_year = self._on_next_year
        
        self.navigation_header.header_frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        # Calendar container
        self.calendar_container = tk.Frame(self, bg="white")
        self.calendar_container.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))
        
        # Configure calendar container
        self.calendar_container.grid_rowconfigure(0, weight=1)
        self.calendar_container.grid_columnconfigure(0, weight=1)
        
        # Create calendar modules
        self.month_module = CalendarMonthModule(
            self.calendar_container,
            config=self.config,
            timeline=self.timeline,
            date_selected_callback=self._on_date_selected_from_calendar
        )
        
        # Create year module
        self.year_module = CalendarYearModule(
            self.calendar_container,
            config=self.config,
            timeline=self.timeline,
            date_selected_callback=self._on_date_selected_from_calendar,
            month_selected_callback=self._on_month_selected_from_year
        )
        
        # Start with year view
        self.switch_calendar_view("year")
    
    def switch_calendar_view(self, view_mode: str):
        """Switch between month and year calendar views."""
        # Remove current calendar module
        if self.current_calendar_module:
            self.current_calendar_module.grid_forget()
        
        # Switch to appropriate module
        if view_mode == "year" and self.year_module:
            self.current_calendar_module = self.year_module
            self.year_module.set_current_date(self.current_date)
        else:
            # Default to month view
            self.current_calendar_module = self.month_module
            self.month_module.set_current_date(self.current_date)
            view_mode = "month"
        
        # Place the new module
        self.current_calendar_module.grid(row=0, column=0, sticky="nsew")
        
        # Update state
        self.current_view_mode = view_mode
        
        # Update navigation header to show/hide month buttons
        if self.navigation_header:
            self.navigation_header.set_view_mode(view_mode)
        
        # Notify parent
        if self.view_changed_callback:
            self.view_changed_callback(view_mode)
    
    def set_current_date(self, new_date: date):
        """Set current date and update all components."""
        self.current_date = new_date
        
        # Update navigation header
        if self.navigation_header:
            self.navigation_header.set_current_date(new_date)
        
        # Update current calendar module
        if self.current_calendar_module:
            if hasattr(self.current_calendar_module, 'set_current_date'):
                self.current_calendar_module.set_current_date(new_date)
    
    # Navigation callbacks
    def _on_navigation_date_change(self, new_date: date):
        """Handle date change from navigation header."""
        self.current_date = new_date
        
        # Update current calendar module
        if self.current_calendar_module:
            if hasattr(self.current_calendar_module, 'set_current_date'):
                self.current_calendar_module.set_current_date(new_date)
        
        # Notify parent
        if self.date_changed_callback:
            self.date_changed_callback(new_date)
    
    def _on_first_entry_click(self):
        """Handle First Entry button click."""
        if self.config and hasattr(self.config, 'first_entry_date_obj'):
            self.set_current_date(self.config.first_entry_date_obj)
            if self.date_changed_callback:
                self.date_changed_callback(self.config.first_entry_date_obj)
    
    def _on_uk_target_click(self):
        """Handle UK target button click."""
        if not self.config or not self.timeline:
            return
            
        try:
            # Import here to avoid circular imports
            from calendar_app.model.ilr_statistics import ILRStatisticsEngine
            
            # Get current ILR statistics
            ilr_engine = ILRStatisticsEngine(self.timeline, self.config)
            current_stats = ilr_engine.get_global_statistics()
            
            # Navigate to UK scenario target completion date
            if (current_stats and 
                current_stats.in_uk_scenario.target_completion_date and 
                not current_stats.in_uk_scenario.is_complete):
                target_date = current_stats.in_uk_scenario.target_completion_date
                self.set_current_date(target_date)
                if self.date_changed_callback:
                    self.date_changed_callback(target_date)
        except Exception as e:
            print(f"Error getting UK target date: {e}")
    
    def _on_total_target_click(self):
        """Handle Total target button click."""
        if not self.config or not self.timeline:
            return
            
        try:
            # Import here to avoid circular imports
            from calendar_app.model.ilr_statistics import ILRStatisticsEngine
            
            # Get current ILR statistics
            ilr_engine = ILRStatisticsEngine(self.timeline, self.config)
            current_stats = ilr_engine.get_global_statistics()
            
            # Navigate to Total scenario target completion date
            if (current_stats and 
                current_stats.total_scenario.target_completion_date and 
                not current_stats.total_scenario.is_complete):
                target_date = current_stats.total_scenario.target_completion_date
                self.set_current_date(target_date)
                if self.date_changed_callback:
                    self.date_changed_callback(target_date)
        except Exception as e:
            print(f"Error getting Total target date: {e}")
    
    def _on_today_click(self):
        """Handle Today button click."""
        today = date.today()
        self.set_current_date(today)
        if self.date_changed_callback:
            self.date_changed_callback(today)
    
    def _on_prev_month(self):
        """Handle previous month navigation."""
        current = self.current_date
        if current.month == 1:
            new_date = current.replace(year=current.year - 1, month=12, day=1)
        else:
            new_date = current.replace(month=current.month - 1, day=1)
        
        self.set_current_date(new_date)
        if self.date_changed_callback:
            self.date_changed_callback(new_date)
    
    def _on_next_month(self):
        """Handle next month navigation."""
        current = self.current_date
        if current.month == 12:
            new_date = current.replace(year=current.year + 1, month=1, day=1)
        else:
            new_date = current.replace(month=current.month + 1, day=1)
        
        self.set_current_date(new_date)
        if self.date_changed_callback:
            self.date_changed_callback(new_date)
    
    def _on_prev_year(self):
        """Handle previous year navigation."""
        new_date = self.current_date.replace(year=self.current_date.year - 1)
        self.set_current_date(new_date)
        if self.date_changed_callback:
            self.date_changed_callback(new_date)
    
    def _on_next_year(self):
        """Handle next year navigation."""
        new_date = self.current_date.replace(year=self.current_date.year + 1)
        self.set_current_date(new_date)
        if self.date_changed_callback:
            self.date_changed_callback(new_date)
    
    def _on_view_mode_changed(self, view_mode: str):
        """Handle view mode change from navigation header."""
        self.switch_calendar_view(view_mode)
    
    def _on_date_selected_from_calendar(self, selected_date: date):
        """Handle date selection from month calendar."""
        self.current_date = selected_date
        
        # Update navigation header
        if self.navigation_header:
            self.navigation_header.set_current_date(selected_date)
        
        # Notify parent
        if self.date_selected_callback:
            self.date_selected_callback(selected_date)
    
    def _on_month_selected_from_year(self, month_date: date):
        """Handle month selection from year calendar - switch to month view."""
        self.current_date = month_date
        
        # Switch to month view
        self.switch_calendar_view("month")
        
        # Update navigation header
        if self.navigation_header:
            self.navigation_header.set_current_date(month_date)
        
        # Notify parent about date change
        if self.date_changed_callback:
            self.date_changed_callback(month_date)
            self.date_changed_callback(month_date)
    
    def refresh_display(self):
        """Refresh the calendar display."""
        if self.current_calendar_module:
            if hasattr(self.current_calendar_module, 'refresh_display'):
                self.current_calendar_module.refresh_display()
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference for all components."""
        self.timeline = timeline
        
        # Update navigation header
        if self.navigation_header:
            self.navigation_header.update_timeline(timeline)
        
        # Update calendar modules
        if self.month_module:
            self.month_module.update_timeline(timeline)
        
        if self.year_module:
            self.year_module.update_timeline(timeline)
        
        # Refresh display
        self.refresh_display()
    
    def highlight_target_dates(self, target_dates):
        """Highlight target dates in the calendar.
        
        Args:
            target_dates: Dictionary mapping date to {'type': str, 'color': str}
                         or list for backwards compatibility
        """
        # Update month module if it exists
        if self.month_module and hasattr(self.month_module, 'set_target_dates'):
            self.month_module.set_target_dates(target_dates)
        
        # Update year module if it exists (placeholder for future)
        if self.year_module and hasattr(self.year_module, 'set_target_dates'):
            self.year_module.set_target_dates(target_dates)