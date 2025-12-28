"""
Trip Classification System

Handles mapping of trips from JSON data to daily timeline and determines
day-by-day classifications based on ILR business rules.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from calendar_app.config import AppConfig


class TripClassifier:
    """
    Classifies days based on trip data and ILR business rules.
    
    Maps loaded trip data to daily timeline and determines:
    - UK residence days (not on any trip)  
    - Short trip days (<14 days - count toward ILR)
    - Long trip days (≥14 days - do not count toward ILR)
    """
    
    def __init__(self, config: AppConfig, trips_data: List[Dict]):
        """
        Initialize trip classifier with pre-loaded trip data.
        
        Args:
            config: Application configuration for validation
            trips_data: List of validated trip dictionaries from DataLoader
        """
        self.config = config
        self.trips_data = trips_data
        self._trip_day_map: Dict[date, Dict] = self._build_trip_day_map()
        
    def _build_trip_day_map(self) -> Dict[date, Dict]:
        """
        Build a mapping from each date to trip information.
        
        Returns:
            Dictionary mapping date -> trip data (or None for UK residence days)
        """            
        trip_day_map = {}
        
        for trip in self.trips_data:
            departure_date = trip["departure_date_obj"]
            return_date = trip["return_date_obj"]
            
            # Map each day of the trip to trip information
            current_date = departure_date
            while current_date <= return_date:
                if current_date in trip_day_map:
                    raise ValueError(
                        f"Date {current_date.strftime('%d-%m-%Y')} appears in multiple trips: "
                        f"'{trip_day_map[current_date]['id']}' and '{trip['id']}'"
                    )
                trip_day_map[current_date] = trip
                
                # Move to next day
                current_date += timedelta(days=1)
                
        return trip_day_map
        
    def get_day_trip_info(self, target_date: date) -> Optional[Dict]:
        """
        Get trip information for a specific date.
        
        Args:
            target_date: Date to check for trip information
            
        Returns:
            Trip dictionary if date is within a trip, None if UK residence day
        """
        return self._trip_day_map.get(target_date)
        
    def is_trip_day(self, target_date: date) -> bool:
        """Check if a date falls within any trip."""
        return self.get_day_trip_info(target_date) is not None
        
    def is_short_trip_day(self, target_date: date) -> bool:
        """
        Check if a date is part of a short trip (<14 days).
        
        Args:
            target_date: Date to check
            
        Returns:
            True if date is part of short trip, False otherwise
        """
        trip_info = self.get_day_trip_info(target_date)
        if trip_info is None:
            return False
        return trip_info["is_short_trip"]
        
    def is_long_trip_day(self, target_date: date) -> bool:
        """
        Check if a date is part of a long trip (≥14 days).
        
        Args:
            target_date: Date to check
            
        Returns:
            True if date is part of long trip, False otherwise  
        """
        trip_info = self.get_day_trip_info(target_date)
        if trip_info is None:
            return False
        return not trip_info["is_short_trip"]
        
    def get_trip_summary(self, target_date: date) -> Dict:
        """
        Get comprehensive trip information for a date.
        
        Args:
            target_date: Date to get trip summary for
            
        Returns:
            Dictionary with trip details, classification, and metadata
        """
        trip_info = self.get_day_trip_info(target_date)
        
        if trip_info is None:
            return {
                'classification': 'UK_RESIDENCE',
                'is_trip_day': False,
                'trip_id': None,
                'trip_type': None,
                'departure_date': None,
                'return_date': None,
                'trip_length_days': None,
                'from_airport': None,
                'to_airport': None
            }
        
        return {
            'classification': 'SHORT_TRIP' if trip_info["is_short_trip"] else 'LONG_TRIP',
            'is_trip_day': True,
            'trip_id': trip_info.get("id"),
            'trip_type': 'short' if trip_info["is_short_trip"] else 'long',
            'departure_date': trip_info["departure_date_obj"],
            'return_date': trip_info["return_date_obj"], 
            'trip_length_days': trip_info["trip_length_days"],
            'from_airport': trip_info.get("from_airport"),
            'to_airport': trip_info.get("to_airport")
        }
        
    def get_all_trips(self) -> List[Dict]:
        """
        Get all loaded trip data.
        
        Returns:
            List of all trip dictionaries with parsed dates
        """
        return self.trips_data
        
    def get_trips_in_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Get all trips that occur within a date range.
        
        Args:
            start_date: Range start date (inclusive)
            end_date: Range end date (inclusive)
            
        Returns:
            List of trips that overlap with the date range
        """
        overlapping_trips = []
        
        for trip in self.trips_data:
            trip_start = trip["departure_date_obj"]
            trip_end = trip["return_date_obj"]
            
            # Check for date range overlap
            if trip_start <= end_date and trip_end >= start_date:
                overlapping_trips.append(trip)
                
        return overlapping_trips
        
    def validate_trip_data(self) -> Tuple[bool, List[str]]:
        """
        Validate trip data for consistency and business rule compliance.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        try:
            # Trip day map was already built in constructor, so overlapping trips
            # would have been caught during initialization
            errors = []
            
            # Check for trips that might cause issues
            for trip in self.trips_data:
                # Business rule validation (already done by DataLoader, but double-check)
                if trip["departure_date_obj"] < self.config.first_entry_date_obj:
                    errors.append(
                        f"Trip {trip['id']}: starts before first entry date"
                    )
                    
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Trip validation failed: {e}"]