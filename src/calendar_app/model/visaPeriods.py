"""
Visa Period Matching System

Handles mapping of visa periods from JSON data to daily timeline and provides
visa context for ILR calculations and tracking.
"""

from datetime import date, timedelta
from typing import Dict, List, Optional, Tuple
from calendar_app.config import AppConfig


class VisaClassifier:
    """
    Maps days to visa periods and provides visa context for ILR calculations.
    
    Handles visa period transitions, salary tracking, and provides context
    for each day about which visa period it belongs to.
    """
    
    def __init__(self, config: AppConfig, visaPeriods_data: List[Dict]):
        """
        Initialize visa classifier with pre-loaded visa period data.
        
        Args:
            config: Application configuration for validation
            visaPeriods_data: List of validated visa period dictionaries from DataLoader
            
        Raises:
            ValueError: If visa periods have gaps or overlaps
        """
        self.config = config
        self.visaPeriods_data = visaPeriods_data
        self._visaPeriod_day_map: Dict[date, Dict] = self._build_visaPeriod_day_map()
        
    def _build_visaPeriod_day_map(self) -> Dict[date, Dict]:
        """
        Build a mapping from each date to visa period information.
        
        Returns:
            Dictionary mapping date -> visa period data
            
        Raises:
            ValueError: If visa periods overlap or have gaps within timeline range
        """
        visaPeriod_day_map = {}
        
        # Sort visa periods by start date to check for gaps/overlaps
        sorted_periods = sorted(self.visaPeriods_data, key=lambda x: x["start_date_obj"])
        
        for i, visaPeriod in enumerate(sorted_periods):
            start_date = visaPeriod["start_date_obj"]
            end_date = visaPeriod["end_date_obj"]
            
            # Validate visa period is within or overlaps with timeline range
            timeline_start = date(self.config.start_year, 1, 1)
            timeline_end = date(self.config.end_year, 12, 31)
            
            # Check for overlaps with previous periods
            if i > 0:
                previous_visaPeriod = sorted_periods[i - 1]
                previous_end = previous_visaPeriod["end_date_obj"]
                
                # Check for overlap
                if start_date <= previous_end:
                    raise ValueError(
                        f"Visa period '{visaPeriod['id']}' overlaps with "
                        f"'{previous_visaPeriod['id']}'. Period starts {start_date.strftime('%d-%m-%Y')} "
                        f"but previous period ends {previous_end.strftime('%d-%m-%Y')}"
                    )
                
                # Check for gaps (only if within timeline range)
                expected_start = previous_end + timedelta(days=1)
                if (start_date > expected_start and 
                    previous_end >= timeline_start and 
                    start_date <= timeline_end):
                    raise ValueError(
                        f"Gap found between visa periods: '{previous_visaPeriod['id']}' ends "
                        f"{previous_end.strftime('%d-%m-%Y')} but '{visaPeriod['id']}' starts "
                        f"{start_date.strftime('%d-%m-%Y')}. Expected continuous periods."
                    )
            
            # Map each day of the visa period to visa information
            current_date = start_date
            while current_date <= end_date:
                # Only map days within timeline range
                if timeline_start <= current_date <= timeline_end:
                    if current_date in visaPeriod_day_map:
                        raise ValueError(
                            f"Date {current_date.strftime('%d-%m-%Y')} appears in multiple visa periods: "
                            f"'{visaPeriod_day_map[current_date]['id']}' and '{visaPeriod['id']}'"
                        )
                    visaPeriod_day_map[current_date] = visaPeriod
                
                current_date += timedelta(days=1)
                
        return visaPeriod_day_map
        
    def get_day_visaPeriod_info(self, target_date: date) -> Optional[Dict]:
        """
        Get visa period information for a specific date.
        
        Args:
            target_date: Date to check for visa period information
            
        Returns:
            Visa period dictionary if date is within a visa period, None otherwise
        """
        return self._visaPeriod_day_map.get(target_date)
        
    def is_visaPeriod_day(self, target_date: date) -> bool:
        """Check if a date falls within any visa period."""
        return self.get_day_visaPeriod_info(target_date) is not None
        
    def get_visaPeriod_label(self, target_date: date) -> Optional[str]:
        """
        Get the human-readable label for the visa period covering a date.
        
        Args:
            target_date: Date to check
            
        Returns:
            Visa period label if date is covered, None otherwise
        """
        visaPeriod_info = self.get_day_visaPeriod_info(target_date)
        if visaPeriod_info is None:
            return None
        return visaPeriod_info.get("label")
        
    def get_visaPeriod_id(self, target_date: date) -> Optional[str]:
        """
        Get the ID for the visa period covering a date.
        
        Args:
            target_date: Date to check
            
        Returns:
            Visa period ID if date is covered, None otherwise
        """
        visaPeriod_info = self.get_day_visaPeriod_info(target_date)
        if visaPeriod_info is None:
            return None
        return visaPeriod_info.get("id")
        
    def get_visaPeriod_salary(self, target_date: date) -> Optional[str]:
        """
        Get the salary for the visa period covering a date.
        
        Args:
            target_date: Date to check
            
        Returns:
            Salary string if date is covered, None otherwise
        """
        visaPeriod_info = self.get_day_visaPeriod_info(target_date)
        if visaPeriod_info is None:
            return None
        return visaPeriod_info.get("gross_salary")
        
    def get_visaPeriod_summary(self, target_date: date) -> Dict:
        """
        Get comprehensive visa period information for a date.
        
        Args:
            target_date: Date to get visa summary for
            
        Returns:
            Dictionary with visa period details and metadata
        """
        visaPeriod_info = self.get_day_visaPeriod_info(target_date)
        
        if visaPeriod_info is None:
            return {
                'has_visaPeriod': False,
                'visaPeriod_id': None,
                'visaPeriod_label': None,
                'start_date': None,
                'end_date': None,
                'gross_salary': None,
                'days_in_period': None,
                'day_number_in_period': None
            }
        
        # Calculate day position within visa period
        period_start = visaPeriod_info["start_date_obj"]
        period_end = visaPeriod_info["end_date_obj"]
        days_in_period = (period_end - period_start).days + 1
        day_number_in_period = (target_date - period_start).days + 1
        
        return {
            'has_visaPeriod': True,
            'visaPeriod_id': visaPeriod_info.get("id"),
            'visaPeriod_label': visaPeriod_info.get("label"),
            'start_date': period_start,
            'end_date': period_end,
            'gross_salary': visaPeriod_info.get("gross_salary"),
            'days_in_period': days_in_period,
            'day_number_in_period': day_number_in_period
        }
        
    def get_all_visaPeriods(self) -> List[Dict]:
        """
        Get all loaded visa period data.
        
        Returns:
            List of all visa period dictionaries with parsed dates
        """
        return self.visaPeriods_data
        
    def get_visaPeriods_in_date_range(self, start_date: date, end_date: date) -> List[Dict]:
        """
        Get all visa periods that occur within a date range.
        
        Args:
            start_date: Range start date (inclusive)
            end_date: Range end date (inclusive)
            
        Returns:
            List of visa periods that overlap with the date range
        """
        overlapping_periods = []
        
        for visaPeriod in self.visaPeriods_data:
            period_start = visaPeriod["start_date_obj"]
            period_end = visaPeriod["end_date_obj"]
            
            # Check for date range overlap
            if period_start <= end_date and period_end >= start_date:
                overlapping_periods.append(visaPeriod)
                
        return overlapping_periods
        
    def get_visaPeriod_transitions(self) -> List[Dict]:
        """
        Get information about visa period transitions.
        
        Returns:
            List of transition information between visa periods
        """
        if len(self.visaPeriods_data) <= 1:
            return []
            
        sorted_periods = sorted(self.visaPeriods_data, key=lambda x: x["start_date_obj"])
        transitions = []
        
        for i in range(1, len(sorted_periods)):
            previous_period = sorted_periods[i - 1]
            current_period = sorted_periods[i]
            
            transition = {
                'from_visaPeriod_id': previous_period["id"],
                'from_visaPeriod_label': previous_period["label"],
                'from_end_date': previous_period["end_date_obj"],
                'from_salary': previous_period.get("gross_salary"),
                'to_visaPeriod_id': current_period["id"],
                'to_visaPeriod_label': current_period["label"],
                'to_start_date': current_period["start_date_obj"],
                'to_salary': current_period.get("gross_salary"),
                'transition_date': current_period["start_date_obj"],
                'is_salary_increase': self._is_salary_increase(
                    previous_period.get("gross_salary", "£0.00"),
                    current_period.get("gross_salary", "£0.00")
                )
            }
            transitions.append(transition)
            
        return transitions
        
    def _is_salary_increase(self, old_salary: str, new_salary: str) -> Optional[bool]:
        """
        Compare two salary strings to determine if there's an increase.
        
        Args:
            old_salary: Previous salary string (e.g., "£32400.00")
            new_salary: New salary string (e.g., "£40200.00")
            
        Returns:
            True if increase, False if decrease, None if cannot compare
        """
        try:
            # Extract numeric values from salary strings
            old_amount = float(old_salary.replace('£', '').replace(',', ''))
            new_amount = float(new_salary.replace('£', '').replace(',', ''))
            return new_amount > old_amount
        except (ValueError, AttributeError):
            return None
            
    def get_current_visaPeriod(self, reference_date: Optional[date] = None) -> Optional[Dict]:
        """
        Get the visa period that covers a reference date (defaults to today).
        
        Args:
            reference_date: Date to check (defaults to first_entry_date from config)
            
        Returns:
            Current visa period info or None if no period covers the date
        """
        if reference_date is None:
            reference_date = self.config.first_entry_date_obj
            
        return self.get_day_visaPeriod_info(reference_date)
        
    def validate_visaPeriods(self) -> Tuple[bool, List[str]]:
        """
        Validate visa period data for consistency and business rule compliance.
        
        Returns:
            Tuple of (is_valid, list_of_error_messages)
        """
        try:
            # Visa day map was already built in constructor, so overlapping/gap issues
            # would have been caught during initialization
            errors = []
            
            # Check for periods before first entry date
            for visaPeriod in self.visaPeriods_data:
                if visaPeriod["end_date_obj"] < self.config.first_entry_date_obj:
                    errors.append(
                        f"Visa period '{visaPeriod['id']}': ends before first entry date"
                    )
                    
            # Check that first entry date is covered by a visa period
            first_entry_visaPeriod = self.get_day_visaPeriod_info(self.config.first_entry_date_obj)
            if first_entry_visaPeriod is None:
                errors.append(
                    f"First entry date {self.config.first_entry_date} is not covered by any visa period"
                )
                
            # Validate salary formats
            for visaPeriod in self.visaPeriods_data:
                salary = visaPeriod.get("gross_salary", "")
                if salary and not salary.startswith('£'):
                    errors.append(
                        f"Visa period '{visaPeriod['id']}': invalid salary format '{salary}'. Expected format: £12345.00"
                    )
                    
            return len(errors) == 0, errors
            
        except Exception as e:
            return False, [f"Visa period validation failed: {e}"]
            
    def get_timeline_coverage_summary(self) -> Dict[str, any]:
        """
        Get summary of how well visa periods cover the timeline range.
        
        Returns:
            Dictionary with coverage statistics and uncovered date ranges
        """
        timeline_start = date(self.config.start_year, 1, 1)
        timeline_end = date(self.config.end_year, 12, 31)
        
        total_timeline_days = (timeline_end - timeline_start).days + 1
        covered_days = len(self._visaPeriod_day_map)
        coverage_percentage = (covered_days / total_timeline_days) * 100 if total_timeline_days > 0 else 0
        
        # Find uncovered date ranges
        uncovered_ranges = []
        current_date = timeline_start
        range_start = None
        
        while current_date <= timeline_end:
            if current_date not in self._visaPeriod_day_map:
                if range_start is None:
                    range_start = current_date
            else:
                if range_start is not None:
                    uncovered_ranges.append({
                        'start_date': range_start.strftime('%d-%m-%Y'),
                        'end_date': (current_date - timedelta(days=1)).strftime('%d-%m-%Y'),
                        'days': (current_date - range_start).days
                    })
                    range_start = None
            current_date += timedelta(days=1)
            
        # Handle case where timeline ends with uncovered period
        if range_start is not None:
            uncovered_ranges.append({
                'start_date': range_start.strftime('%d-%m-%Y'),
                'end_date': timeline_end.strftime('%d-%m-%Y'),
                'days': (timeline_end - range_start).days + 1
            })
        
        return {
            'timeline_start': timeline_start.strftime('%d-%m-%Y'),
            'timeline_end': timeline_end.strftime('%d-%m-%Y'),
            'total_timeline_days': total_timeline_days,
            'covered_days': covered_days,
            'uncovered_days': total_timeline_days - covered_days,
            'coverage_percentage': round(coverage_percentage, 1),
            'total_visaPeriods': len(self.visaPeriods_data),
            'uncovered_date_ranges': uncovered_ranges
        }