"""
View Manager

Simple view manager for handling calendar view switching.
MVP implementation focused on month view with foundation for future views.
"""

import tkinter as tk
from datetime import date
from typing import Dict, Type, Optional
from .base_view import BaseCalendarView


class ViewType:
    """Enum-like class for view types."""
    MONTH = "month"
    YEAR = "year"     # Future implementation
    DAY = "day"       # Future implementation
    STATS = "stats"   # Future implementation


class ViewManager:
    """
    Simple view manager for calendar application.
    
    Handles:
    - View switching between month/year/day/stats views
    - View state preservation
    - Basic navigation history
    """
    
    def __init__(self, parent: tk.Widget, config=None, timeline=None):
        """
        Initialize view manager.
        
        Args:
            parent: Parent widget for views
            config: AppConfig instance
            timeline: DateTimeline instance
        """
        self.parent = parent
        self.config = config
        self.timeline = timeline
        
        # Current view state
        self.current_view: Optional[BaseCalendarView] = None
        self.current_view_type: Optional[str] = None
        self.current_date = date.today()
        
        # View registry (will be expanded for future views)
        self.view_registry: Dict[str, Type[BaseCalendarView]] = {}
        
        # Register available views
        self.register_views()
    
    def register_views(self):
        """Register available view types."""
        # Import here to avoid circular imports
        try:
            from .month_view import MonthView
            self.view_registry[ViewType.MONTH] = MonthView
        except ImportError:
            # Month view not yet refactored - we'll handle this in next step
            pass
        
        # Future view registrations:
        # self.view_registry[ViewType.YEAR] = YearView
        # self.view_registry[ViewType.DAY] = DayView  
        # self.view_registry[ViewType.STATS] = StatsView
    
    def switch_to_view(self, view_type: str, **kwargs):
        """
        Switch to specified view type.
        
        Args:
            view_type: Type of view to switch to (ViewType constant)
            **kwargs: Additional parameters for view creation
        """
        # Preserve current date if switching views
        if self.current_view:
            self.current_date = self.current_view.get_current_date()
        
        # Clean up current view
        if self.current_view:
            self.current_view.destroy()
        
        # Get target date from kwargs or use current
        target_date = kwargs.get('date', self.current_date)
        
        # Create new view
        if view_type in self.view_registry:
            view_class = self.view_registry[view_type]
            self.current_view = view_class(
                self.parent, 
                current_date=target_date,
                config=self.config,
                timeline=self.timeline
            )
            
            # Setup view switching callback
            self.current_view.set_view_switch_callback(self.switch_to_view)
            
            self.current_view_type = view_type
            self.current_date = target_date
            
        else:
            raise ValueError(f"Unknown view type: {view_type}")
    
    def get_current_view_type(self) -> Optional[str]:
        """Get current active view type."""
        return self.current_view_type
    
    def get_current_date(self) -> date:
        """Get current date from active view."""
        if self.current_view:
            return self.current_view.get_current_date()
        return self.current_date
    
    def set_date(self, new_date: date):
        """Set date in current view."""
        if self.current_view:
            self.current_view.set_current_date(new_date)
        self.current_date = new_date
    
    # Convenience methods for specific view switches
    def show_month_view(self, date: Optional[date] = None):
        """Switch to month view."""
        self.switch_to_view(ViewType.MONTH, date=date)
    
    def show_year_view(self, date: Optional[date] = None):
        """Switch to year view (future implementation)."""
        self.switch_to_view(ViewType.YEAR, date=date)
    
    def show_day_view(self, date: Optional[date] = None):
        """Switch to day detail view (future implementation)."""
        self.switch_to_view(ViewType.DAY, date=date)
    
    def show_stats_view(self):
        """Switch to ILR statistics view (future implementation)."""
        self.switch_to_view(ViewType.STATS)
    
    def cleanup(self):
        """Clean up view manager resources."""
        if self.current_view:
            self.current_view.destroy()
            self.current_view = None