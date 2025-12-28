"""
Base Calendar View

Abstract base class for all calendar views (month, year, day, stats).
Provides common interface and shared functionality.
"""

import tkinter as tk
from abc import ABC, abstractmethod
from datetime import date
from typing import Optional, Callable
from ..components.navigation_header import NavigationHeader


class BaseCalendarView(ABC):
    """
    Abstract base class for calendar views.
    
    Provides:
    - Common navigation header
    - Shared event handling
    - Standard interface for view switching
    - Date state management
    """
    
    def __init__(self, parent: tk.Widget, current_date: Optional[date] = None, 
                 config=None, timeline=None):
        """
        Initialize base calendar view.
        
        Args:
            parent: Parent widget to contain the view
            current_date: Starting date to display
            config: AppConfig instance
            timeline: DateTimeline instance
        """
        self.parent = parent
        self.config = config
        self.timeline = timeline
        
        # Date state
        self.current_date = current_date or date.today()
        
        # Callback for when view requests switching to another view
        self.view_switch_callback: Optional[Callable] = None
        
        # Main container
        self.main_frame = None
        self.navigation_header = None
        self.content_frame = None
        
        # Create the view
        self.create_view()
    
    def create_view(self):
        """Create the complete view with header and content."""
        # Main container
        self.main_frame = tk.Frame(self.parent, bg="white", relief="ridge", bd=2)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Navigation header (shared across all views)
        self.navigation_header = NavigationHeader(self.main_frame, self.config, self.timeline)
        self.setup_navigation_callbacks()
        
        # Content area (implemented by subclasses)
        self.content_frame = tk.Frame(self.main_frame, bg="white")
        self.content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Let subclass create its specific content
        self.create_content()
        
        # Initialize display
        self.navigation_header.set_current_date(self.current_date)
    
    def setup_navigation_callbacks(self):
        """Setup callbacks for navigation header events."""
        self.navigation_header.set_callbacks(
            on_date_changed=self.on_date_changed,
            on_first_entry_clicked=self.on_first_entry_clicked,
            on_target_date_clicked=self.on_target_date_clicked,
            on_prev_month=self.on_prev_month,
            on_next_month=self.on_next_month,
            on_prev_year=self.on_prev_year,
            on_next_year=self.on_next_year
        )
    
    @abstractmethod
    def create_content(self):
        """Create view-specific content. Must be implemented by subclasses."""
        pass
    
    @abstractmethod
    def update_display(self):
        """Update view display. Must be implemented by subclasses."""
        pass
    
    # Navigation event handlers (can be overridden by subclasses)
    def on_date_changed(self, new_date: date):
        """Handle date change from navigation header."""
        self.current_date = new_date
        self.update_display()
    
    def on_first_entry_clicked(self):
        """Handle first entry button click."""
        if self.config and self.config.first_entry_date:
            first_entry = self.config.first_entry_date
            if isinstance(first_entry, str):
                from datetime import datetime
                first_entry = datetime.strptime(first_entry, "%d-%m-%Y").date()
            
            # Navigate to first entry month
            self.set_current_date(date(first_entry.year, first_entry.month, 1))
    
    def on_target_date_clicked(self):
        """Handle target date button click."""
        if self.config and hasattr(self.config, 'target_completion_date'):
            target_date = self.config.target_completion_date
            self.set_current_date(date(target_date.year, target_date.month, 1))
    
    def on_prev_month(self):
        """Handle previous month navigation."""
        if self.current_date.month == 1:
            new_date = date(self.current_date.year - 1, 12, 1)
        else:
            new_date = date(self.current_date.year, self.current_date.month - 1, 1)
        
        # Validate against date range
        if self.config:
            if new_date.year >= self.config.start_year:
                self.set_current_date(new_date)
        else:
            self.set_current_date(new_date)
    
    def on_next_month(self):
        """Handle next month navigation."""
        if self.current_date.month == 12:
            new_date = date(self.current_date.year + 1, 1, 1)
        else:
            new_date = date(self.current_date.year, self.current_date.month + 1, 1)
        
        # Validate against date range
        if self.config:
            if new_date.year <= self.config.end_year:
                self.set_current_date(new_date)
        else:
            self.set_current_date(new_date)
    
    def on_prev_year(self):
        """Handle previous year navigation."""
        new_date = date(self.current_date.year - 1, self.current_date.month, 1)
        
        # Validate against date range
        if self.config:
            if new_date.year >= self.config.start_year:
                self.set_current_date(new_date)
        else:
            self.set_current_date(new_date)
    
    def on_next_year(self):
        """Handle next year navigation."""
        new_date = date(self.current_date.year + 1, self.current_date.month, 1)
        
        # Validate against date range
        if self.config:
            if new_date.year <= self.config.end_year:
                self.set_current_date(new_date)
        else:
            self.set_current_date(new_date)
    
    # Public interface methods
    def set_current_date(self, new_date: date):
        """Set current date and update all displays."""
        self.current_date = new_date
        self.navigation_header.set_current_date(new_date)
        self.update_display()
    
    def get_current_date(self) -> date:
        """Get current date."""
        return self.current_date
    
    def set_view_switch_callback(self, callback: Callable):
        """Set callback for view switching requests."""
        self.view_switch_callback = callback
    
    def request_view_switch(self, view_type: str, **kwargs):
        """Request switching to another view type."""
        if self.view_switch_callback:
            self.view_switch_callback(view_type, **kwargs)
    
    def destroy(self):
        """Clean up view resources."""
        if self.main_frame:
            self.main_frame.destroy()