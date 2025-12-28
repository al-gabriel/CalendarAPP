"""
Day Foundation Classes for Calendar App
Contains Day class and DayClassification enum for individual day management.
"""

from datetime import date
from enum import Enum
from typing import Dict, Optional


class DayClassification(Enum):
    """Classification types for each day in the timeline."""
    UK_RESIDENCE = "uk_residence"  # Normal UK residence day
    SHORT_TRIP = "short_trip"      # Day during short trip (<14 days) - counts toward ILR total
    LONG_TRIP = "long_trip"        # Day during long trip (>=14 days) - does not count toward ILR
    PRE_ENTRY = "pre_entry"        # Before first UK entry date
    UNKNOWN = "unknown"            # Classification not yet determined


class Day:
    """Represents a single day in the timeline with its classification."""
    
    def __init__(self, date_obj: date):
        self.date = date_obj
        self.classification = DayClassification.UNKNOWN
        self.trip_info: Optional[Dict] = None  # Will store trip details if it's a trip day
        self.visaPeriod_info: Optional[Dict] = None  # Will store visa period details if day has visa coverage
    
    @property
    def year(self) -> int:
        return self.date.year
    
    @property
    def month(self) -> int:
        return self.date.month
    
    @property
    def day(self) -> int:
        return self.date.day
    
    @property
    def weekday(self) -> int:
        """Returns weekday (0=Monday, 6=Sunday)"""
        return self.date.weekday()
    
    @property
    def is_weekend(self) -> bool:
        """Returns True if day is Saturday or Sunday"""
        return self.weekday >= 5
    
    def counts_as_ilr_in_uk_day(self, first_entry_date: date) -> bool:
        """
        Check if this day counts as an ILR in-UK day.
        
        Args:
            first_entry_date: Date when ILR counting began
            
        Returns:
            True if day counts as ILR in-UK day (pure UK residence, no trips)
        """
        return (self.date >= first_entry_date and 
                self.classification == DayClassification.UK_RESIDENCE)
    
    def counts_as_short_trip_day(self, first_entry_date: date) -> bool:
        """
        Check if this day counts as a short trip day for ILR total.
        
        Args:
            first_entry_date: Date when ILR counting began
            
        Returns:
            True if day is part of short trip (<14 days) and counts toward ILR total
        """
        return (self.date >= first_entry_date and 
                self.classification == DayClassification.SHORT_TRIP)
    
    def counts_as_ilr_total_day(self, first_entry_date: date) -> bool:
        """
        Check if this day counts toward ILR total days.
        
        ILR total = ILR in-UK days + short trip days
        
        Args:
            first_entry_date: Date when ILR counting began
            
        Returns:
            True if day counts toward ILR total
        """
        return (self.counts_as_ilr_in_uk_day(first_entry_date) or 
                self.counts_as_short_trip_day(first_entry_date))
    
    def counts_as_long_trip_day(self, first_entry_date: date) -> bool:
        """
        Check if this day is a long trip day (>=14 days, does not count toward ILR).
        
        Args:
            first_entry_date: Date when ILR counting began
            
        Returns:
            True if day is part of long trip (tracked but not counted toward ILR)
        """
        return (self.date >= first_entry_date and 
                self.classification == DayClassification.LONG_TRIP)
    
    def __str__(self) -> str:
        return f"Day({self.date.strftime('%d-%m-%Y')}, {self.classification.value})"
    
    def __repr__(self) -> str:
        return self.__str__()