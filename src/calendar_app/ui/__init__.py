"""
UI Package

Contains user interface components and views for the Calendar App.
"""

# Import new architecture components for easy access
from .views.view_manager import ViewManager, ViewType
from .views.month_view import MonthView
from .components.navigation_header import NavigationHeader

__all__ = ['ViewManager', 'ViewType', 'MonthView', 'NavigationHeader']