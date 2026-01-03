"""
Date Timeline Management for Calendar App
Contains DateTimeline class for managing configurable day-by-day timeline for ILR tracking.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional

from calendar_app.config import AppConfig
from calendar_app.model.day import Day, DayClassification
from calendar_app.model.trips import TripClassifier
from calendar_app.model.visaPeriods import VisaClassifier


class DateTimeline:
    """Manages the complete day-by-day timeline for a specified date range."""
    
    _instance: Optional['DateTimeline'] = None  # Class-level singleton instance
    
    def __init__(self, config: AppConfig, trip_classifier: 'TripClassifier', visaPeriod_classifier: 'VisaClassifier'):
        """
        Initialize timeline from AppConfig (private - use from_config class method).
        
        Args:
            config: AppConfig instance with start_year and end_year
            trip_classifier: TripClassifier for real trip data integration (required)
            visaPeriod_classifier: VisaClassifier for visa period data integration (required)
            
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
        self.trip_classifier = trip_classifier
        self.visaPeriod_classifier = visaPeriod_classifier
        self.days: Dict[date, Day] = {}
        self._generate_timeline()
    
    @classmethod
    def from_config(cls, config: AppConfig, trip_classifier: 'TripClassifier', visaPeriod_classifier: 'VisaClassifier', use_singleton: bool = True) -> 'DateTimeline':
        """
        Create DateTimeline from AppConfig with trip and visa integration.
        
        Args:
            config: AppConfig instance with validated start_year and end_year
            trip_classifier: TripClassifier for real trip data integration (required)
            visaPeriod_classifier: VisaClassifier for visa period data integration (required)
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
        
        instance = cls(config, trip_classifier, visaPeriod_classifier)
        if use_singleton:
            cls._instance = instance
        return instance
    
    @classmethod
    def reset_singleton(cls) -> None:
        """Reset the singleton instance (useful for testing)."""
        cls._instance = None
    
    def _classify_day_from_trip_data(self, current_date: date, trip_classifier: 'TripClassifier') -> DayClassification:
        """
        Classify a day based on trip data from TripClassifier and visa coverage.
        
        Args:
            current_date: Date to classify
            trip_classifier: TripClassifier instance
            
        Returns:
            DayClassification for the date
        """
        # Handle pre-entry days
        if current_date < self.config.first_entry_date_obj:
            return DayClassification.PRE_ENTRY
        
        # Check if day is part of any trip
        if trip_classifier.is_short_trip_day(current_date):
            return DayClassification.SHORT_TRIP
        elif trip_classifier.is_long_trip_day(current_date):
            return DayClassification.LONG_TRIP
        else:
            # Not part of any trip = UK residence day
            # Check if day has visa coverage
            visaPeriod_summary = self.visaPeriod_classifier.get_visaPeriod_summary(current_date)
            if visaPeriod_summary['has_visaPeriod']:
                return DayClassification.UK_RESIDENCE
            else:
                # UK residence day without visa coverage - counts toward ILR but tracked separately
                return DayClassification.NO_VISA_COVERAGE

    def _generate_timeline(self) -> None:
        """Generate all days based on configured date range and classify them."""
        start_date = date(self.start_year, 1, 1)
        end_date = date(self.end_year, 12, 31)
        
        current_date = start_date
        while current_date <= end_date:
            day_obj = Day(current_date)
            
            # Set day classification using trip data (trip_classifier is always present)
            day_obj.classification = self._classify_day_from_trip_data(current_date, self.trip_classifier)
            
            # Store trip information if this is a trip day
            trip_summary = self.trip_classifier.get_trip_summary(current_date)
            if trip_summary['is_trip_day']:
                day_obj.trip_info = trip_summary
            
            # Store visa period information if this day has visa period coverage
            visaPeriod_summary = self.visaPeriod_classifier.get_visaPeriod_summary(current_date)
            if visaPeriod_summary['has_visaPeriod']:
                day_obj.visaPeriod_info = visaPeriod_summary
            
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
                                visaPeriod: Optional[str] = None) -> bool:
        """Update classification and info for a specific day."""
        day_obj = self.get_day(date_obj)
        if day_obj:
            day_obj.classification = classification
            if trip_info:
                day_obj.trip_info = trip_info
            if visaPeriod:
                day_obj.visaPeriod = visaPeriod
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
    
    
    def update_date_range_classification(self, start_date: date, end_date: date, 
                                       classification: DayClassification,
                                       trip_info: Optional[Dict] = None,
                                       visaPeriod: Optional[str] = None) -> int:
        """
        Update classification for a range of dates (inclusive).
        Useful for applying trip classifications to entire trip periods.
        
        Returns:
            Number of days successfully updated
        """
        updated_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            if self.update_day_classification(current_date, classification, trip_info, visaPeriod):
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
        Focused on day classification data only (no ILR-specific logic).
        
        Args:
            start_date: Optional start date for summary range (defaults to timeline start)
            end_date: Optional end date for summary range (defaults to timeline end)
            debug: If True, include debug information (classification_counts, percentages)
        
        Returns:
            Dictionary with timeline classification statistics
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
        
        # Get classification counts for the specified date range
        if start_date is None and end_date is None:
            # Use optimized whole-timeline methods
            classification_counts = self.get_classification_counts_total()
            total_days = self.get_total_days()
            date_range_description = f"{self.start_year}-{self.end_year} (full timeline)"
        else:
            # Calculate classification counts for date range
            classification_counts = self.get_classification_counts_for_date_range(actual_start_date, actual_end_date)
            total_days = sum(classification_counts.values())
            date_range_description = f"{actual_start_date.strftime('%d-%m-%Y')} to {actual_end_date.strftime('%d-%m-%Y')}"
        
        # Build main result (always visible)
        result = {
            'total_days': total_days,
            'date_range': date_range_description,
            'actual_start_date': actual_start_date.strftime('%d-%m-%Y'),
            'actual_end_date': actual_end_date.strftime('%d-%m-%Y'),
            'classification_counts': {k.value: v for k, v in classification_counts.items()}
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
                'classification_progress': {
                    'classified_percentage': round(classified_percentage, 1),
                    'unknown_percentage': round(unknown_percentage, 1),
                    'classified_days': total_days - unknown_count,
                    'unknown_days': unknown_count
                }
            }
        
        return result