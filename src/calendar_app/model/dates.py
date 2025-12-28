"""
Date Timeline Foundation for Calendar App
Generates and manages configurable day-by-day timeline for ILR tracking.
"""

from datetime import date, timedelta
from enum import Enum
from typing import Dict, List, Optional

# Import config module from parent directory
from calendar_app.config import AppConfig


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
        self.trip_info: Optional[Dict] = None  # Will store trip details later
        self.visa_period: Optional[str] = None  # Will store visa period info later
    
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


class DateTimeline:
    """Manages the complete day-by-day timeline for a specified date range."""
    
    _instance: Optional['DateTimeline'] = None  # Class-level singleton instance
    
    def __init__(self, config: AppConfig):
        """
        Initialize timeline from AppConfig (private - use from_config class method).
        
        Args:
            config: AppConfig instance with start_year and end_year
            
        Raises:
            AttributeError: If config missing required attributes
            ValueError: If config values are invalid
        """
        if not hasattr(config, 'start_year') or not hasattr(config, 'end_year'):
            raise AttributeError("config must have start_year and end_year attributes")
        
        # Config validation already happened in AppConfig.validate_config()
        # Just extract the validated values
        self.start_year = config.start_year
        self.end_year = config.end_year
        self.config = config
        self.days: Dict[date, Day] = {}
        self._generate_timeline()
    
    @classmethod
    def from_config(cls, config: AppConfig, use_singleton: bool = True) -> 'DateTimeline':
        """
        Create DateTimeline from AppConfig.
        
        Args:
            config: AppConfig instance with validated start_year and end_year
            use_singleton: If True, reuse existing instance with matching config
            
        Returns:
            DateTimeline instance
            
        Raises:
            ValueError: If singleton exists with different config and use_singleton=True
        """
        if use_singleton and cls._instance is not None:
            # Check if existing instance matches requested config
            if (cls._instance.start_year != config.start_year or 
                cls._instance.end_year != config.end_year):
                raise ValueError(
                    f"Timeline instance exists with range {cls._instance.start_year}-{cls._instance.end_year}, "
                    f"cannot create with different range {config.start_year}-{config.end_year}. "
                    f"Use use_singleton=False or call reset_singleton() first."
                )
            return cls._instance
        
        instance = cls(config)
        if use_singleton:
            cls._instance = instance
        return instance
    
    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
    
    def _generate_timeline(self) -> None:
        """Generate all days based on configured date range."""
        start_date = date(self.start_year, 1, 1)
        end_date = date(self.end_year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            day_obj = Day(current_date)
            self.days[current_date] = day_obj
            current_date += timedelta(days=1)
    
    def get_day(self, date_obj: date) -> Optional[Day]:
        """Get a specific day from the timeline."""
        return self.days.get(date_obj)
    
    def get_days_in_month(self, year: int, month: int) -> List[Day]:
        """Get all days for a specific month."""
        days_in_month = []
        
        # Get first day of month
        first_day = date(year, month, 1)
        
        # Get last day of month
        if month == 12:
            last_day = date(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = date(year, month + 1, 1) - timedelta(days=1)
        
        current_date = first_day
        while current_date <= last_day:
            day_obj = self.get_day(current_date)
            if day_obj:
                days_in_month.append(day_obj)
            current_date += timedelta(days=1)
        
        return days_in_month
    
    def get_days_in_year(self, year: int) -> List[Day]:
        """Get all days for a specific year."""
        days_in_year = []
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            day_obj = self.get_day(current_date)
            if day_obj:
                days_in_year.append(day_obj)
            current_date += timedelta(days=1)
        
        return days_in_year
    
    def is_date_in_range(self, date_obj: date) -> bool:
        """Check if a date is within the supported timeline range."""
        return (self.start_year <= date_obj.year <= self.end_year and 
                date_obj in self.days)
    
    def get_total_days(self) -> int:
        """Get total number of days in timeline."""
        return len(self.days)
    
    def get_date_range_info(self) -> Dict[str, date]:
        """Get information about the timeline date range."""
        return {
            'start_date': date(self.start_year, 1, 1),
            'end_date': date(self.end_year, 12, 31),
            'total_days': self.get_total_days()
        }
    
    def update_day_classification(self, date_obj: date, classification: DayClassification,
                                trip_info: Optional[Dict] = None, 
                                visa_period: Optional[str] = None) -> bool:
        """Update classification and info for a specific day."""
        day_obj = self.get_day(date_obj)
        if day_obj:
            day_obj.classification = classification
            if trip_info:
                day_obj.trip_info = trip_info
            if visa_period:
                day_obj.visa_period = visa_period
            return True
        return False
    
    def get_days_by_classification(self, classification: DayClassification) -> List[Day]:
        """Get all days with a specific classification."""
        return [day for day in self.days.values() if day.classification == classification]
    
    def get_classification_counts_total(self) -> Dict[DayClassification, int]:
        """Get counts of each classification type across the entire timeline."""
        counts = {classification: 0 for classification in DayClassification}
        
        for day in self.days.values():
            counts[day.classification] += 1
            
        return counts
    
    def get_classification_counts_for_month(self, year: int, month: int) -> Dict[DayClassification, int]:
        """Get counts of each classification type for a specific month."""
        counts = {classification: 0 for classification in DayClassification}
        
        month_days = self.get_days_in_month(year, month)
        for day in month_days:
            counts[day.classification] += 1
            
        return counts
    
    def get_classification_counts_for_year(self, year: int) -> Dict[DayClassification, int]:
        """Get counts of each classification type for a specific year."""
        counts = {classification: 0 for classification in DayClassification}
        
        year_days = self.get_days_in_year(year)
        for day in year_days:
            counts[day.classification] += 1
            
        return counts
    
    def get_classification_counts_for_date_range(self, start_date: date, end_date: date) -> Dict[DayClassification, int]:
        """Get counts of each classification type for a specific date range."""
        counts = {classification: 0 for classification in DayClassification}
        
        current_date = start_date
        while current_date <= end_date:
            day_obj = self.get_day(current_date)
            if day_obj:
                counts[day_obj.classification] += 1
            current_date += timedelta(days=1)
            
        return counts
    
    def get_ilr_counts_total(self) -> Dict[str, int]:
        """
        Get ILR-specific day counts across the entire timeline.
        Uses first_entry_date from config to determine qualifying days.
        
        Returns:
            Dict with keys: 'ilr_in_uk_days', 'short_trip_days', 'ilr_total_days', 'long_trip_days', 'pre_entry_days'
        """
        first_entry = self.config.first_entry_date_obj
        counts = {
            'ilr_in_uk_days': 0,
            'short_trip_days': 0,
            'ilr_total_days': 0,
            'long_trip_days': 0,
            'pre_entry_days': 0
        }
        
        for day in self.days.values():
            if day.counts_as_ilr_in_uk_day(first_entry):
                counts['ilr_in_uk_days'] += 1
            elif day.counts_as_short_trip_day(first_entry):
                counts['short_trip_days'] += 1
            elif day.counts_as_long_trip_day(first_entry):
                counts['long_trip_days'] += 1
            elif day.date < first_entry:
                counts['pre_entry_days'] += 1
        
        counts['ilr_total_days'] = counts['ilr_in_uk_days'] + counts['short_trip_days']
        return counts
    
    def get_ilr_counts_for_month(self, year: int, month: int) -> Dict[str, int]:
        """
        Get ILR-specific day counts for a specific month.
        Uses first_entry_date from config to determine qualifying days.
        """
        first_entry = self.config.first_entry_date_obj
        counts = {
            'ilr_in_uk_days': 0,
            'short_trip_days': 0,
            'ilr_total_days': 0,
            'long_trip_days': 0,
            'pre_entry_days': 0
        }
        
        month_days = self.get_days_in_month(year, month)
        for day in month_days:
            if day.counts_as_ilr_in_uk_day(first_entry):
                counts['ilr_in_uk_days'] += 1
            elif day.counts_as_short_trip_day(first_entry):
                counts['short_trip_days'] += 1
            elif day.counts_as_long_trip_day(first_entry):
                counts['long_trip_days'] += 1
            elif day.date < first_entry:
                counts['pre_entry_days'] += 1
        
        counts['ilr_total_days'] = counts['ilr_in_uk_days'] + counts['short_trip_days']
        return counts
    
    def get_ilr_counts_for_year(self, year: int) -> Dict[str, int]:
        """
        Get ILR-specific day counts for a specific year.
        Uses first_entry_date from config to determine qualifying days.
        """
        first_entry = self.config.first_entry_date_obj
        counts = {
            'ilr_in_uk_days': 0,
            'short_trip_days': 0,
            'ilr_total_days': 0,
            'long_trip_days': 0,
            'pre_entry_days': 0
        }
        
        year_days = self.get_days_in_year(year)
        for day in year_days:
            if day.counts_as_ilr_in_uk_day(first_entry):
                counts['ilr_in_uk_days'] += 1
            elif day.counts_as_short_trip_day(first_entry):
                counts['short_trip_days'] += 1
            elif day.counts_as_long_trip_day(first_entry):
                counts['long_trip_days'] += 1
            elif day.date < first_entry:
                counts['pre_entry_days'] += 1
        
        counts['ilr_total_days'] = counts['ilr_in_uk_days'] + counts['short_trip_days']
        return counts
    
    def update_date_range_classification(self, start_date: date, end_date: date, 
                                       classification: DayClassification,
                                       trip_info: Optional[Dict] = None,
                                       visa_period: Optional[str] = None) -> int:
        """
        Update classification for a range of dates (inclusive).
        Useful for applying trip classifications to entire trip periods.
        
        Returns:
            Number of days successfully updated
        """
        updated_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            if self.update_day_classification(current_date, classification, trip_info, visa_period):
                updated_count += 1
            current_date += timedelta(days=1)
            
        return updated_count
    
    def classify_pre_entry_days(self) -> int:
        """
        Automatically classify all days before first_entry_date as PRE_ENTRY.
        
        Returns:
            Number of days classified as pre-entry
        """
        first_entry = self.config.first_entry_date_obj
        updated_count = 0
        
        for day in self.days.values():
            if day.date < first_entry and day.classification == DayClassification.UNKNOWN:
                day.classification = DayClassification.PRE_ENTRY
                updated_count += 1
                
        return updated_count
    
    def auto_classify_all_days(self) -> Dict[str, int]:
        """
        Automatically classify all days in the timeline.
        Should be called after trip data is loaded.
        
        Returns:
            Dictionary with counts of days classified by type
        """
        # First classify all pre-entry days
        pre_entry_count = self.classify_pre_entry_days()
        
        # Then classify all remaining UNKNOWN days as UK_RESIDENCE
        # (Trip days will be classified when trip data is loaded)
        first_entry = self.config.first_entry_date_obj
        uk_residence_count = 0
        
        for day in self.days.values():
            if (day.date >= first_entry and 
                day.classification == DayClassification.UNKNOWN):
                day.classification = DayClassification.UK_RESIDENCE
                uk_residence_count += 1
        
        return {
            'pre_entry_classified': pre_entry_count,
            'uk_residence_classified': uk_residence_count,
            'total_classified': pre_entry_count + uk_residence_count
        }
    
    def validate_no_unknown_days(self) -> bool:
        """
        Validate that no days remain UNKNOWN.
        Should be called after full classification is complete.
        
        Returns:
            True if all days are classified, False otherwise
            
        Raises:
            ValueError: If any days remain UNKNOWN (in strict mode)
        """
        unknown_days = self.get_days_by_classification(DayClassification.UNKNOWN)
        
        if unknown_days:
            unknown_count = len(unknown_days)
            first_unknown = unknown_days[0].date.strftime('%d-%m-%Y')
            raise ValueError(
                f"Timeline validation failed: {unknown_count} days remain UNKNOWN. "
                f"First unknown day: {first_unknown}. All days must be classified before use."
            )
        
        return True
    
    def get_classification_summary(self, start_date: Optional[date] = None, end_date: Optional[date] = None, debug: bool = False) -> Dict[str, any]:
        """
        Get comprehensive summary of timeline classification status.
        
        Args:
            start_date: Optional start date for summary range (defaults to timeline start)
            end_date: Optional end date for summary range (defaults to timeline end)
            debug: If True, include debug information (classification_counts, percentages)
        
        Returns:
            Dictionary with ILR counts and optionally debug statistics
        """
        # Determine the actual date range to analyze
        if start_date is None:
            actual_start_date = date(self.start_year, 1, 1)
        else:
            actual_start_date = start_date
            
        if end_date is None:
            actual_end_date = date(self.end_year, 12, 31)
        else:
            actual_end_date = end_date
        
        # Get counts for the specified date range
        if start_date is None and end_date is None:
            # Use optimized whole-timeline methods
            ilr_counts = self.get_ilr_counts_total()
            total_days = self.get_total_days()
            date_range_description = f"{self.start_year}-{self.end_year} (full timeline)"
            if debug:
                classification_counts = self.get_classification_counts_total()
        else:
            # Calculate ILR counts for date range
            first_entry = self.config.first_entry_date_obj
            ilr_counts = {
                'ilr_in_uk_days': 0,
                'short_trip_days': 0,
                'ilr_total_days': 0,
                'long_trip_days': 0,
                'pre_entry_days': 0
            }
            
            if debug:
                classification_counts = self.get_classification_counts_for_date_range(actual_start_date, actual_end_date)
            
            current_date = actual_start_date
            while current_date <= actual_end_date:
                day_obj = self.get_day(current_date)
                if day_obj:
                    if day_obj.counts_as_ilr_in_uk_day(first_entry):
                        ilr_counts['ilr_in_uk_days'] += 1
                    elif day_obj.counts_as_short_trip_day(first_entry):
                        ilr_counts['short_trip_days'] += 1
                    elif day_obj.counts_as_long_trip_day(first_entry):
                        ilr_counts['long_trip_days'] += 1
                    elif day_obj.date < first_entry:
                        ilr_counts['pre_entry_days'] += 1
                current_date += timedelta(days=1)
            
            ilr_counts['ilr_total_days'] = ilr_counts['ilr_in_uk_days'] + ilr_counts['short_trip_days']
            # Calculate total days excluding the computed ilr_total_days to avoid double counting
            total_days = (ilr_counts['ilr_in_uk_days'] + ilr_counts['short_trip_days'] + 
                         ilr_counts['long_trip_days'] + ilr_counts['pre_entry_days'])
            date_range_description = f"{actual_start_date.strftime('%d-%m-%Y')} to {actual_end_date.strftime('%d-%m-%Y')}"
        
        # Build main result (always visible)
        result = {
            'total_days': total_days,
            'date_range': date_range_description,
            'actual_start_date': actual_start_date.strftime('%d-%m-%Y'),
            'actual_end_date': actual_end_date.strftime('%d-%m-%Y'),
            'first_entry_date': self.config.first_entry_date,
            'ilr_counts': ilr_counts
        }
        
        # Add debug information only if requested
        if debug:
            unknown_count = classification_counts.get(DayClassification.UNKNOWN, 0)
            unknown_percentage = (unknown_count / total_days) * 100 if total_days > 0 else 0
            classified_percentage = 100 - unknown_percentage
            
            # Validate that all days are properly classified in production
            if unknown_count > 0:
                print(f"WARNING: {unknown_count} days remain UNKNOWN - timeline not fully classified!")
            
            result['debug_info'] = {
                'classification_counts': {k.value: v for k, v in classification_counts.items()},
                'classification_progress': {
                    'classified_percentage': round(classified_percentage, 1),
                    'unknown_percentage': round(unknown_percentage, 1),
                    'classified_days': total_days - unknown_count,
                    'unknown_days': unknown_count
                }
            }
        
        return result


