"""
UI Package

Contains user interface components and modules for the Calendar App.
"""

# Import new architecture components for easy access
from .components.navigation_header import NavigationHeader
from .components.calendar_component import CalendarComponent
from .grid_layout_manager import GridLayoutManager

__all__ = ['NavigationHeader', 'CalendarComponent', 'GridLayoutManager']