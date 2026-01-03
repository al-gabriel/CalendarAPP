"""
Grid Layout Manager

Manages the 2x2 grid layout of the main application window.
Coordinates the display of different modules:
- Top-left: ILR Statistics Module
- Bottom-left: Context info modules (Month/Year/Day details) 
- Right merged: Calendar Module (ViewManager + NavigationHeader)
"""

import tkinter as tk
from datetime import date
from typing import Optional

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline
from calendar_app.ui.components.calendar_component import CalendarComponent
from calendar_app.ui.modules.ilr_statistics_module import ILRStatisticsModule
from calendar_app.ui.modules.month_info_module import MonthInfoModule
from calendar_app.ui.modules.year_info_module import YearInfoModule
from calendar_app.ui.modules.day_info_module import DayInfoModule


class GridLayoutManager(tk.Frame):
    """
    Manages the 2x2 grid layout for the main application.
    
    Grid Layout:
    +-------------------+-----------------+
    | ILR Statistics    | Calendar        |
    | Module            | Module          | 
    +-------------------+ (merged         |
    | Info Module       |  right          |
    | (Month/Year/Day)  |  side)          |
    +-------------------+-----------------+
    """
    
    def __init__(self, parent: tk.Widget, config: AppConfig, timeline: Optional[DateTimeline] = None):
        """
        Initialize the grid layout manager.
        
        Args:
            parent: Parent widget
            config: Application configuration
            timeline: DateTimeline instance
        """
        super().__init__(parent)
        
        self.config = config
        self.timeline = timeline
        self.current_date = date.today()
        self.current_view_mode = "year"  # "month", "year" - default to year view
        self.selected_date = None  # When a specific day is selected
        
        # Module references
        self.calendar_component = None
        self.ilr_statistics_module = None
        self.current_info_module = None
        
        # Available info modules
        self.month_info_module = None
        self.year_info_module = None
        self.day_info_module = None
        
        # Setup layout
        self.setup_grid()
        self.create_modules()
    
    def setup_grid(self):
        """Configure the grid layout."""
        # Configure grid weights for proper resizing - increased sizes for year view
        self.grid_columnconfigure(0, weight=1, minsize=350)  # Left column - statistics and info panels
        self.grid_columnconfigure(1, weight=2, minsize=700)  # Right column - calendar with navigation (increased for year view)
        self.grid_rowconfigure(0, weight=1, minsize=300)     # Top row - statistics and navigation
        self.grid_rowconfigure(1, weight=1, minsize=200)     # Bottom row - info and calendar grid
    
    def create_modules(self):
        """Create and position all modules in the grid."""
        
        # Create info modules first (before calendar component that might trigger callbacks)
        self.month_info_module = MonthInfoModule(self, self.timeline)
        self.year_info_module = YearInfoModule(self, self.timeline)
        self.day_info_module = DayInfoModule(self, self.timeline, 
                                           on_date_click=self.on_date_selected,
                                           on_back_click=self.on_day_back_click)
        
        # Top-left: ILR Statistics Module
        self.ilr_statistics_module = ILRStatisticsModule(
            parent=self,
            timeline=self.timeline,
            config=self.config,
            on_completion_date_click=self.on_date_selected,
            on_highlight_target_dates=self.on_highlight_target_dates,
            on_view_toggle=self.on_view_toggle
        )
        self.ilr_statistics_module.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        
        # Right side (merged): Calendar Component
        self.calendar_component = CalendarComponent(
            parent=self,
            config=self.config,
            timeline=self.timeline,
            date_changed_callback=self.on_date_changed,
            view_changed_callback=self.on_view_changed,
            date_selected_callback=self.on_date_selected
        )
        self.calendar_component.grid(row=0, column=1, rowspan=2, padx=5, pady=5, sticky="nsew")
        
        # Force refresh target highlighting now that calendar components are ready
        if hasattr(self.ilr_statistics_module, 'force_target_highlighting_refresh'):
            self.ilr_statistics_module.force_target_highlighting_refresh()
        
        # Start with year info module to match year view default
        self.switch_info_module("year")
    
    def switch_info_module(self, info_type: str):
        """Switch the bottom-left info module based on current state."""
        # Remove current info module
        if self.current_info_module:
            self.current_info_module.grid_forget()
        
        # Switch to requested module
        if info_type == "month":
            self.current_info_module = self.month_info_module
            self.month_info_module.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        elif info_type == "year":
            self.current_info_module = self.year_info_module
            self.year_info_module.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        elif info_type == "day":
            self.current_info_module = self.day_info_module
            self.day_info_module.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        else:
            self.current_info_module = None
    
    # Callback methods - coordinating between modules
    def on_date_changed(self, new_date: date):
        """Handle date change from calendar navigation."""
        self.current_date = new_date
        
        # Update the info modules with the new date
        if self.current_info_module and hasattr(self.current_info_module, 'set_current_date'):
            self.current_info_module.set_current_date(new_date)
    
    def on_view_changed(self, view_mode: str):
        """Handle view mode change from calendar."""
        self.current_view_mode = view_mode
        
        # Update toggle button in ILR statistics module (appearance only)
        if self.ilr_statistics_module:
            self.ilr_statistics_module.update_toggle_appearance(view_mode)
        
        # Clear any day selection when changing views
        self.selected_date = None
        
        # Update info module based on view mode
        if view_mode == "year":
            self.switch_info_module("year")
        else:
            self.switch_info_module("month")
    
    def on_date_selected(self, selected_date: date):
        """Handle date selection from calendar or ILR statistics."""
        self.selected_date = selected_date
        old_date = self.current_date
        self.current_date = selected_date
        
        # Only update calendar component if we need to navigate to a different month/year
        need_calendar_update = (
            self.current_view_mode == "year" and old_date.year != selected_date.year or  # Different year in year view
            self.current_view_mode == "month" and (old_date.year != selected_date.year or old_date.month != selected_date.month)  # Different month/year in month view
        )
        
        if need_calendar_update and self.calendar_component:
            self.calendar_component.set_current_date(selected_date)
        
        # Switch to day info module and update it with selected date
        self.switch_info_module("day")
        if self.day_info_module:
            self.day_info_module.set_selected_date(selected_date)
    
    def on_day_back_click(self):
        """Handle back button click from day info module - return to appropriate view."""
        # Return to the info module appropriate for current view mode
        if self.current_view_mode == "year":
            self.switch_info_module("year")
            # Update the year info module with the current date
            if self.year_info_module and hasattr(self.year_info_module, 'set_current_date'):
                self.year_info_module.set_current_date(self.current_date)
        else:
            self.switch_info_module("month")
            # Update the month info module with the current date
            if self.month_info_module and hasattr(self.month_info_module, 'set_current_date'):
                self.month_info_module.set_current_date(self.current_date)
    
    def refresh_all(self):
        """Refresh all modules."""
        if self.calendar_component:
            self.calendar_component.refresh_display()
        
        if self.ilr_statistics_module:
            self.ilr_statistics_module.refresh_statistics()
        
        if self.current_info_module:
            if hasattr(self.current_info_module, 'refresh_info'):
                self.current_info_module.refresh_info()
    
    def update_timeline(self, timeline: DateTimeline):
        """Update timeline reference for all modules."""
        self.timeline = timeline
        
        # Update all modules
        if self.calendar_component:
            self.calendar_component.update_timeline(timeline)
        
        if self.ilr_statistics_module:
            self.ilr_statistics_module.update_timeline(timeline)
        
        if self.month_info_module:
            self.month_info_module.update_timeline(timeline)
        
        if self.year_info_module:
            self.year_info_module.update_timeline(timeline)
        
        if self.day_info_module:
            self.day_info_module.update_timeline(timeline)
        
        # Refresh all displays
        self.refresh_all()
    
    def on_view_toggle(self, view_mode: str):
        """Handle view toggle from ILR statistics module."""
        if self.calendar_component:
            self.calendar_component.switch_calendar_view(view_mode)
        
        # Update info module based on view mode
        if view_mode == "year":
            self.switch_info_module("year")
        else:
            self.switch_info_module("month")
    
    def on_highlight_target_dates(self, target_dates):
        """Handle target date highlighting request.
        
        Args:
            target_dates: Dictionary mapping date to {'type': str, 'color': str}
                         or list for backwards compatibility
        """
        if self.calendar_component:
            self.calendar_component.highlight_target_dates(target_dates)