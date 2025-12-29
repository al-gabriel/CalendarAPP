"""
ILR Statistics Engine

High-level business logic for ILR (Indefinite Leave to Remain) statistics.
Builds upon DateTimeline to provide ILR-specific calculations, projections, and target completion dates.
"""

from datetime import date, timedelta
from typing import Dict, Optional, Tuple, NamedTuple
from dataclasses import dataclass

from calendar_app.model.timeline import DateTimeline
from calendar_app.config import AppConfig


@dataclass
class ILRProgress:
    """Data class representing ILR progress for a specific scenario."""
    days_completed: int
    days_required: int
    days_remaining: int
    percentage_complete: float
    target_completion_date: Optional[date]
    is_complete: bool
    
    @property
    def days_over_requirement(self) -> int:
        """Days over the requirement (negative if still under)."""
        return self.days_completed - self.days_required


@dataclass
class ILRStatistics:
    """Complete ILR statistics for both scenarios."""
    # Raw counts
    ilr_in_uk_days: int
    short_trip_days: int
    ilr_total_days: int
    long_trip_days: int
    pre_entry_days: int
    
    # Progress tracking
    in_uk_scenario: ILRProgress
    total_scenario: ILRProgress
    
    # Date information
    calculation_date: date
    first_entry_date: date
    days_since_entry: int


class ILRStatisticsEngine:
    """
    High-level ILR statistics engine.
    
    Provides business logic for ILR calculations including:
    - Progress tracking for both scenarios (with/without short trips counting)
    - Target completion date projections
    - Percentage complete calculations
    - Month/Year/Global statistics aggregation
    
    Two ILR scenarios:
    1. In-UK scenario: Only UK residence days count (short trips do NOT count)
    2. Total scenario: UK residence + short trips count (short trips DO count)
    
    Both scenarios use the same day requirement (objective_years) but different counting methods.
    Long trips never count towards ILR in either scenario.
    """
    
    def __init__(self, timeline: DateTimeline, config: AppConfig):
        """
        Initialize ILR statistics engine.
        
        Args:
            timeline: DateTimeline instance with classified days
            config: AppConfig with ILR requirements and dates
        """
        self.timeline = timeline
        self.config = config
        
        # Calculate exact ILR requirement based on objective_years and leap years
        self.ilr_days_required = self._calculate_ilr_days_requirement()
    
    def _calculate_ilr_days_requirement(self) -> int:
        """
        Calculate exact number of days required for ILR based on objective_years.
        Accounts for leap years in the period from first_entry_date.
        
        Returns:
            Exact number of days required for ILR
        """
        first_entry = self.config.first_entry_date_obj
        objective_years = self.config.objective_years
        
        # Calculate end date: first_entry + objective_years
        # We need to go year by year to account for leap years
        current_date = first_entry
        total_days = 0
        
        for year_offset in range(objective_years):
            # Handle the case where first entry date doesn't exist in target year (Feb 29 on non-leap year)
            try:
                year_start = date(first_entry.year + year_offset, first_entry.month, first_entry.day)
            except ValueError:
                # Feb 29 on non-leap year, use Feb 28
                year_start = date(first_entry.year + year_offset, first_entry.month, 28)
            
            try:
                year_end = date(first_entry.year + year_offset + 1, first_entry.month, first_entry.day)
            except ValueError:
                # Feb 29 on non-leap year, use Feb 28
                year_end = date(first_entry.year + year_offset + 1, first_entry.month, 28)
            
            # For the first year, start from actual first entry date
            if year_offset == 0:
                year_start = first_entry
            
            # Calculate days in this year of the objective period
            days_in_year = (year_end - year_start).days
            total_days += days_in_year
        
        return total_days
    
    def get_ilr_requirement_info(self) -> Dict[str, any]:
        """
        Get information about the ILR requirement calculation.
        
        Returns:
            Dict with requirement details
        """
        return {
            'objective_years': self.config.objective_years,
            'first_entry_date': self.config.first_entry_date,
            'days_required': self.ilr_days_required,
            'average_days_per_year': self.ilr_days_required / self.config.objective_years,
            'calculation_method': 'Exact calculation accounting for leap years'
        }
    
    def get_global_statistics(self, calculation_date: Optional[date] = None) -> ILRStatistics:
        """
        Get complete ILR statistics for the entire timeline up to calculation_date.
        
        Args:
            calculation_date: Date to calculate statistics up to (default: today)
            
        Returns:
            ILRStatistics with complete progress information
        """
        calc_date = calculation_date or date.today()
        
        # Get raw counts from timeline up to calculation date
        if calc_date >= date(self.timeline.end_year, 12, 31):
            # Use total timeline counts
            raw_counts = self.get_ilr_counts_total()
        else:
            # Use date range from first entry to calculation date
            raw_counts = self.get_ilr_counts_for_date_range(
                self.config.first_entry_date_obj, 
                calc_date
            )
        
        # Calculate days since entry (inclusive of both start and end dates)
        # Formula: (end_date - start_date).days + 1 to include both endpoints
        days_since_entry = max(0, (calc_date - self.config.first_entry_date_obj).days + 1)
        
        # Create progress objects for both scenarios (same requirement, different counting)
        in_uk_progress = self._calculate_progress(
            days_completed=raw_counts['ilr_in_uk_days'],
            days_required=self.ilr_days_required,
            calculation_date=calc_date,
            scenario_type='in_uk'
        )
        
        total_progress = self._calculate_progress(
            days_completed=raw_counts['ilr_total_days'],
            days_required=self.ilr_days_required,
            calculation_date=calc_date,
            scenario_type='total'
        )
        
        return ILRStatistics(
            # Raw counts
            ilr_in_uk_days=raw_counts['ilr_in_uk_days'],
            short_trip_days=raw_counts['short_trip_days'],
            ilr_total_days=raw_counts['ilr_total_days'],
            long_trip_days=raw_counts['long_trip_days'],
            pre_entry_days=raw_counts['pre_entry_days'],
            
            # Progress tracking
            in_uk_scenario=in_uk_progress,
            total_scenario=total_progress,
            
            # Date information
            calculation_date=calc_date,
            first_entry_date=self.config.first_entry_date_obj,
            days_since_entry=days_since_entry
        )
    
    def get_monthly_statistics(self, year: int, month: int) -> ILRStatistics:
        """
        Get ILR statistics for a specific month.
        
        Args:
            year: Year to calculate
            month: Month to calculate (1-12)
            
        Returns:
            ILRStatistics for the specified month
        """
        # Get month counts
        raw_counts = self.get_ilr_counts_for_month(year, month)
        
        # For monthly stats, we calculate cumulative progress up to end of month
        from calendar import monthrange
        last_day_of_month = date(year, month, monthrange(year, month)[1])
        
        return self.get_global_statistics(calculation_date=last_day_of_month)
    
    def get_yearly_statistics(self, year: int) -> ILRStatistics:
        """
        Get ILR statistics for a specific year.
        
        Args:
            year: Year to calculate
            
        Returns:
            ILRStatistics for the specified year
        """
        # Get year counts
        raw_counts = self.get_ilr_counts_for_year(year)
        
        # For yearly stats, we calculate cumulative progress up to end of year
        last_day_of_year = date(year, 12, 31)
        
        return self.get_global_statistics(calculation_date=last_day_of_year)
    
    def _calculate_progress(self, days_completed: int, days_required: int, 
                          calculation_date: date, scenario_type: str) -> ILRProgress:
        """
        Calculate progress metrics for a specific scenario.
        
        Args:
            days_completed: Number of days completed
            days_required: Number of days required
            calculation_date: Date of calculation
            scenario_type: 'in_uk' or 'total' for projection logic
            
        Returns:
            ILRProgress with calculated metrics
        """
        days_remaining = max(0, days_required - days_completed)
        percentage_complete = min(100.0, (days_completed / days_required) * 100)
        is_complete = days_completed >= days_required
        
        # Calculate target completion date
        target_completion_date = None
        if not is_complete and calculation_date <= date.today():
            # Simple projection: assume continuous UK residence from calculation_date
            target_completion_date = calculation_date + timedelta(days=days_remaining)
        
        return ILRProgress(
            days_completed=days_completed,
            days_required=days_required,
            days_remaining=days_remaining,
            percentage_complete=percentage_complete,
            target_completion_date=target_completion_date,
            is_complete=is_complete
        )
    
    def get_progress_summary(self, statistics: ILRStatistics) -> Dict[str, str]:
        """
        Get human-readable progress summary.
        
        Args:
            statistics: ILRStatistics object
            
        Returns:
            Dict with formatted progress strings
        """
        return {
            'in_uk_progress': f"{statistics.in_uk_scenario.days_completed:,} / {statistics.in_uk_scenario.days_required:,} days ({statistics.in_uk_scenario.percentage_complete:.1f}%)",
            'total_progress': f"{statistics.total_scenario.days_completed:,} / {statistics.total_scenario.days_required:,} days ({statistics.total_scenario.percentage_complete:.1f}%)",
            'days_since_entry': f"{statistics.days_since_entry:,} days since first entry",
            'in_uk_remaining': f"{statistics.in_uk_scenario.days_remaining:,} days remaining" if not statistics.in_uk_scenario.is_complete else "✅ In-UK requirement complete!",
            'total_remaining': f"{statistics.total_scenario.days_remaining:,} days remaining" if not statistics.total_scenario.is_complete else "✅ Total requirement complete!",
            'in_uk_target': statistics.in_uk_scenario.target_completion_date.strftime('%d-%m-%Y') if statistics.in_uk_scenario.target_completion_date else "N/A",
            'total_target': statistics.total_scenario.target_completion_date.strftime('%d-%m-%Y') if statistics.total_scenario.target_completion_date else "N/A"
        }
    
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
        
        for day in self.timeline.days.values():
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
        
        month_days = self.timeline.get_days_in_month(year, month)
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
        
        year_days = self.timeline.get_days_in_year(year)
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
    
    def get_ilr_counts_for_date_range(self, start_date: date, end_date: date) -> Dict[str, int]:
        """
        Get ILR-specific day counts for a specific date range.
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
        
        current_date = start_date
        while current_date <= end_date:
            day_obj = self.timeline.get_day(current_date)
            if day_obj:
                if day_obj.counts_as_ilr_in_uk_day(first_entry):
                    counts['ilr_in_uk_days'] += 1
                elif day_obj.counts_as_short_trip_day(first_entry):
                    counts['short_trip_days'] += 1
                elif day_obj.counts_as_long_trip_day(first_entry):
                    counts['long_trip_days'] += 1
                elif day_obj.date < first_entry:
                    counts['pre_entry_days'] += 1
            current_date += timedelta(days=1)
        
        counts['ilr_total_days'] = counts['ilr_in_uk_days'] + counts['short_trip_days']
        return counts