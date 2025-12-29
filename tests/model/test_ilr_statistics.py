"""
Comprehensive Test Suite for ilr_statistics.py
Tests all functionality of ILRStatisticsEngine class including methods moved from Timeline.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.model.day import Day, DayClassification
from calendar_app.model.timeline import DateTimeline
from calendar_app.model.trips import TripClassifier
from calendar_app.model.visaPeriods import VisaClassifier
from calendar_app.model.ilr_statistics import ILRStatisticsEngine, ILRProgress, ILRStatistics
from calendar_app.config import AppConfig


class MockAppConfig:
    """Mock AppConfig for testing."""
    def __init__(self, start_year: int, end_year: int, first_entry_date: str, objective_years: int = 5):
        self.start_year = start_year
        self.end_year = end_year
        self.first_entry_date = first_entry_date
        self.objective_years = objective_years
        # Parse first_entry_date string to date object
        day, month, year = first_entry_date.split('-')
        self.first_entry_date_obj = date(int(year), int(month), int(day))


class MockTripClassifier:
    """Mock TripClassifier for testing."""
    def __init__(self, config):
        self.config = config
        self._mock_trips = {}
    
    def get_day_trip_info(self, target_date):
        return self._mock_trips.get(target_date)
    
    def is_trip_day(self, target_date):
        return target_date in self._mock_trips
    
    def is_short_trip_day(self, target_date):
        trip_info = self._mock_trips.get(target_date)
        return trip_info is not None and trip_info.get("is_short_trip", False)
    
    def is_long_trip_day(self, target_date):
        trip_info = self._mock_trips.get(target_date)
        return trip_info is not None and not trip_info.get("is_short_trip", True)
    
    def get_trip_summary(self, target_date):
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


class MockVisaClassifier:
    """Mock VisaClassifier for testing."""
    def __init__(self, config, visaPeriods_data=None):
        self.config = config
        self.visaPeriods_data = visaPeriods_data or []
        self._mock_visaPeriod_periods = {}
    
    def get_day_visaPeriod_info(self, target_date):
        return self._mock_visaPeriod_periods.get(target_date)
    
    def is_visaPeriod_day(self, target_date):
        return target_date in self._mock_visaPeriod_periods
    
    def get_visaPeriod_summary(self, target_date):
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


def create_test_timeline_with_classifications(config):
    """Create a timeline with specific day classifications for testing."""
    trip_classifier = MockTripClassifier(config)
    visa_classifier = MockVisaClassifier(config)
    timeline = DateTimeline.from_config(config, trip_classifier, visa_classifier, use_singleton=False)
    
    # Set up test classifications
    first_entry = config.first_entry_date_obj
    
    # Add some short trips
    short_trip_dates = [
        first_entry + timedelta(days=30),  # 30 days after entry
        first_entry + timedelta(days=31),  # 2-day short trip
        first_entry + timedelta(days=100),  # 100 days after entry
        first_entry + timedelta(days=101)   # 2-day short trip
    ]
    
    for trip_date in short_trip_dates:
        timeline.update_day_classification(trip_date, DayClassification.SHORT_TRIP)
    
    # Add some long trips
    long_trip_dates = [
        first_entry + timedelta(days=200),  # 200 days after entry
        first_entry + timedelta(days=201),  # 5-day long trip
        first_entry + timedelta(days=202),
        first_entry + timedelta(days=203),
        first_entry + timedelta(days=204)
    ]
    
    for trip_date in long_trip_dates:
        timeline.update_day_classification(trip_date, DayClassification.LONG_TRIP)
    
    return timeline


def test_ilr_statistics_engine_initialization():
    """Test ILRStatisticsEngine initialization and requirement calculation."""
    print("=== Testing ILRStatisticsEngine Initialization ===")
    
    # Test basic initialization
    config = MockAppConfig(2023, 2025, "01-03-2023", objective_years=5)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    assert ilr_engine.timeline == timeline
    assert ilr_engine.config == config
    assert hasattr(ilr_engine, 'ilr_days_required')
    assert ilr_engine.ilr_days_required > 0
    print("✓ ILRStatisticsEngine initialization successful")
    
    # Test requirement calculation
    req_info = ilr_engine.get_ilr_requirement_info()
    expected_keys = ['objective_years', 'first_entry_date', 'days_required', 'average_days_per_year', 'calculation_method']
    for key in expected_keys:
        assert key in req_info, f"Missing key: {key}"
    
    assert req_info['objective_years'] == 5
    assert req_info['first_entry_date'] == "01-03-2023"
    assert req_info['days_required'] == ilr_engine.ilr_days_required
    assert req_info['average_days_per_year'] > 365  # Should account for leap years
    print("✓ ILR requirement calculation correct")


def test_leap_year_requirement_calculation():
    """Test ILR requirement calculation with leap years."""
    print("=== Testing Leap Year Requirement Calculation ===")
    
    # Test entry on leap day
    config_leap = MockAppConfig(2020, 2025, "29-02-2020", objective_years=4)
    timeline_leap = create_test_timeline_with_classifications(config_leap)
    ilr_engine_leap = ILRStatisticsEngine(timeline_leap, config_leap)
    
    # 4 years from Feb 29, 2020 should be Feb 29, 2024 (both leap years)
    req_info_leap = ilr_engine_leap.get_ilr_requirement_info()
    
    # Manual calculation: Feb 29, 2020 to Feb 29, 2024
    # Year 1: Feb 29, 2020 to Feb 28, 2021 = 365 days
    # Year 2: Mar 1, 2021 to Feb 28, 2022 = 365 days  
    # Year 3: Mar 1, 2022 to Feb 28, 2023 = 365 days
    # Year 4: Mar 1, 2023 to Feb 29, 2024 = 366 days (2024 is leap year)
    expected_days = 365 + 365 + 365 + 366  # = 1461 days
    
    assert req_info_leap['days_required'] == expected_days
    print(f"✓ Leap year calculation correct: {req_info_leap['days_required']} days")
    
    # Test non-leap year entry for comparison
    config_regular = MockAppConfig(2021, 2026, "28-02-2021", objective_years=4)
    timeline_regular = create_test_timeline_with_classifications(config_regular)
    ilr_engine_regular = ILRStatisticsEngine(timeline_regular, config_regular)
    req_info_regular = ilr_engine_regular.get_ilr_requirement_info()
    
    print(f"✓ Regular year calculation: {req_info_regular['days_required']} days")
    print(f"✓ Leap year impact: {req_info_leap['days_required'] - req_info_regular['days_required']} day difference")


def test_ilr_counting_methods():
    """Test ILR counting methods moved from timeline."""
    print("=== Testing ILR Counting Methods ===")
    
    config = MockAppConfig(2023, 2024, "01-06-2023", objective_years=5)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test get_ilr_counts_total
    total_counts = ilr_engine.get_ilr_counts_total()
    required_keys = ['ilr_in_uk_days', 'short_trip_days', 'ilr_total_days', 'long_trip_days', 'pre_entry_days']
    for key in required_keys:
        assert key in total_counts, f"Missing key: {key}"
        assert isinstance(total_counts[key], int), f"{key} should be integer"
    
    # Verify logical consistency
    assert total_counts['ilr_total_days'] == total_counts['ilr_in_uk_days'] + total_counts['short_trip_days']
    assert total_counts['short_trip_days'] > 0  # We added short trips
    assert total_counts['long_trip_days'] > 0   # We added long trips
    print("✓ get_ilr_counts_total() works correctly")
    
    # Test get_ilr_counts_for_month (June 2023)
    june_counts = ilr_engine.get_ilr_counts_for_month(2023, 6)
    for key in required_keys:
        assert key in june_counts, f"Missing key: {key}"
    print("✓ get_ilr_counts_for_month() works correctly")
    
    # Test get_ilr_counts_for_year (2023)
    year_counts = ilr_engine.get_ilr_counts_for_year(2023)
    for key in required_keys:
        assert key in year_counts, f"Missing key: {key}"
    print("✓ get_ilr_counts_for_year() works correctly")
    
    # Test get_ilr_counts_for_date_range
    start_date = date(2023, 7, 1)
    end_date = date(2023, 7, 31)
    range_counts = ilr_engine.get_ilr_counts_for_date_range(start_date, end_date)
    for key in required_keys:
        assert key in range_counts, f"Missing key: {key}"
    print("✓ get_ilr_counts_for_date_range() works correctly")


def test_global_statistics():
    """Test global ILR statistics calculation."""
    print("=== Testing Global Statistics ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)  # Short period for testing
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test with specific calculation date
    calc_date = date(2023, 9, 1)
    stats = ilr_engine.get_global_statistics(calculation_date=calc_date)
    
    # Verify ILRStatistics structure
    assert isinstance(stats, ILRStatistics)
    assert isinstance(stats.in_uk_scenario, ILRProgress)
    assert isinstance(stats.total_scenario, ILRProgress)
    assert stats.calculation_date == calc_date
    assert stats.first_entry_date == config.first_entry_date_obj
    assert stats.days_since_entry > 0
    print("✓ ILRStatistics structure correct")
    
    # Verify progress calculations
    assert stats.in_uk_scenario.days_required == ilr_engine.ilr_days_required
    assert stats.total_scenario.days_required == ilr_engine.ilr_days_required
    assert stats.total_scenario.days_completed >= stats.in_uk_scenario.days_completed  # Total includes short trips
    print("✓ Progress calculations correct")
    
    # Test without calculation date (should use today)
    current_stats = ilr_engine.get_global_statistics()
    assert isinstance(current_stats, ILRStatistics)
    print("✓ Current date statistics work correctly")


def test_progress_calculation():
    """Test progress calculation methods."""
    print("=== Testing Progress Calculation ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test _calculate_progress directly
    days_completed = 400
    days_required = 730
    calc_date = date(2023, 9, 1)
    
    progress = ilr_engine._calculate_progress(days_completed, days_required, calc_date, 'total')
    
    assert progress.days_completed == days_completed
    assert progress.days_required == days_required
    assert progress.days_remaining == days_required - days_completed
    assert progress.percentage_complete == (days_completed / days_required) * 100
    assert not progress.is_complete
    assert progress.target_completion_date is not None
    print("✓ Progress calculation logic correct")
    
    # Test completed scenario
    completed_progress = ilr_engine._calculate_progress(800, 730, calc_date, 'total')
    assert completed_progress.is_complete
    assert completed_progress.days_remaining == 0
    assert completed_progress.percentage_complete == 100.0
    assert completed_progress.days_over_requirement == 70
    print("✓ Completed scenario calculation correct")


def test_progress_calculation():
    """Test progress calculation methods."""
    print("=== Testing Progress Calculation ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test _calculate_progress directly
    days_completed = 400
    days_required = 730
    calc_date = date(2023, 9, 1)
    
    progress = ilr_engine._calculate_progress(days_completed, days_required, calc_date, 'total')
    
    assert progress.days_completed == days_completed
    assert progress.days_required == days_required
    assert progress.days_remaining == days_required - days_completed
    assert progress.percentage_complete == (days_completed / days_required) * 100
    assert not progress.is_complete
    
    # Test that target completion date is calculated correctly (inline now)
    expected_target = calc_date + timedelta(days=progress.days_remaining)
    assert progress.target_completion_date == expected_target
    print("✓ Progress calculation logic correct")
    
    # Test completed scenario
    completed_progress = ilr_engine._calculate_progress(800, 730, calc_date, 'total')
    assert completed_progress.is_complete
    assert completed_progress.days_remaining == 0
    assert completed_progress.percentage_complete == 100.0
    assert completed_progress.days_over_requirement == 70
    assert completed_progress.target_completion_date is None  # No projection needed when complete
    print("✓ Completed scenario calculation correct")


def test_progress_summary():
    """Test progress summary generation."""
    print("=== Testing Progress Summary ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    stats = ilr_engine.get_global_statistics(calculation_date=date(2023, 9, 1))
    summary = ilr_engine.get_progress_summary(stats)
    
    expected_keys = [
        'in_uk_progress', 'total_progress', 'days_since_entry',
        'in_uk_remaining', 'total_remaining', 'in_uk_target', 'total_target'
    ]
    
    for key in expected_keys:
        assert key in summary, f"Missing summary key: {key}"
        assert isinstance(summary[key], str), f"Summary {key} should be string"
    
    # Check for expected formatting
    assert "/" in summary['in_uk_progress']  # Should have "completed / required"
    assert "%" in summary['in_uk_progress']  # Should have percentage
    print("✓ Progress summary formatting correct")


def test_ilr_eligibility():
    """Test ILR eligibility checking using statistics data directly."""
    print("=== Testing ILR Eligibility ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=1)  # Short period to test completion
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test not eligible (should be the case with short objective period)
    stats_early = ilr_engine.get_global_statistics(calculation_date=date(2023, 6, 1))
    
    # Check eligibility directly using the statistics data
    is_eligible_early = stats_early.in_uk_scenario.is_complete or stats_early.total_scenario.is_complete
    assert not is_eligible_early, "Should not be eligible early in timeline"
    
    # Verify we can access the progress data directly
    assert stats_early.in_uk_scenario.days_remaining > 0
    assert stats_early.total_scenario.days_remaining > 0
    print(f"✓ Early eligibility check: Not eligible - need {min(stats_early.in_uk_scenario.days_remaining, stats_early.total_scenario.days_remaining)} more days")
    
    # Test potential eligibility with later date
    stats_later = ilr_engine.get_global_statistics(calculation_date=date(2024, 6, 1))
    is_eligible_later = stats_later.in_uk_scenario.is_complete or stats_later.total_scenario.is_complete
    
    if is_eligible_later:
        if stats_later.in_uk_scenario.is_complete:
            print(f"✓ Later eligibility check: Eligible via In-UK scenario with {stats_later.in_uk_scenario.days_completed} days")
        else:
            print(f"✓ Later eligibility check: Eligible via Total scenario with {stats_later.total_scenario.days_completed} days")
    else:
        remaining_days = min(stats_later.in_uk_scenario.days_remaining, stats_later.total_scenario.days_remaining)
        print(f"✓ Later eligibility check: Still not eligible - need {remaining_days} more days")


def test_monthly_and_yearly_statistics():
    """Test monthly and yearly statistics methods."""
    print("=== Testing Monthly and Yearly Statistics ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Test monthly statistics
    monthly_stats = ilr_engine.get_monthly_statistics(2023, 6)
    assert isinstance(monthly_stats, ILRStatistics)
    assert monthly_stats.calculation_date == date(2023, 6, 30)  # Last day of June
    print("✓ Monthly statistics work correctly")
    
    # Test yearly statistics
    yearly_stats = ilr_engine.get_yearly_statistics(2023)
    assert isinstance(yearly_stats, ILRStatistics)
    assert yearly_stats.calculation_date == date(2023, 12, 31)  # Last day of year
    print("✓ Yearly statistics work correctly")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("=== Testing Edge Cases ===")
    
    # Test with very short objective period
    config_short = MockAppConfig(2023, 2024, "01-12-2023", objective_years=1)
    timeline_short = create_test_timeline_with_classifications(config_short)
    ilr_engine_short = ILRStatisticsEngine(timeline_short, config_short)
    
    req_info_short = ilr_engine_short.get_ilr_requirement_info()
    assert req_info_short['days_required'] > 0
    print("✓ Short objective period handled correctly")
    
    # Test with entry date at timeline boundary
    config_boundary = MockAppConfig(2023, 2024, "31-12-2023", objective_years=1)
    timeline_boundary = create_test_timeline_with_classifications(config_boundary)
    ilr_engine_boundary = ILRStatisticsEngine(timeline_boundary, config_boundary)
    
    stats_boundary = ilr_engine_boundary.get_global_statistics()
    assert isinstance(stats_boundary, ILRStatistics)
    print("✓ Timeline boundary entry handled correctly")
    
    # Test with calculation date before first entry
    early_calc_date = config_short.first_entry_date_obj - timedelta(days=30)
    early_stats = ilr_engine_short.get_global_statistics(calculation_date=early_calc_date)
    assert early_stats.days_since_entry == 0  # Should be 0 or positive
    print("✓ Calculation date before entry handled correctly")


def test_data_class_properties():
    """Test ILRProgress and ILRStatistics data class properties."""
    print("=== Testing Data Class Properties ===")
    
    config = MockAppConfig(2023, 2024, "01-03-2023", objective_years=2)
    timeline = create_test_timeline_with_classifications(config)
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    stats = ilr_engine.get_global_statistics()
    
    # Test ILRProgress properties
    progress = stats.in_uk_scenario
    days_over = progress.days_over_requirement
    assert isinstance(days_over, int)
    
    if progress.is_complete:
        assert days_over >= 0
    else:
        assert days_over < 0
    
    print("✓ ILRProgress properties work correctly")
    
    # Test ILRStatistics structure
    assert hasattr(stats, 'ilr_in_uk_days')
    assert hasattr(stats, 'short_trip_days')
    assert hasattr(stats, 'ilr_total_days')
    assert hasattr(stats, 'long_trip_days')
    assert hasattr(stats, 'pre_entry_days')
    assert hasattr(stats, 'in_uk_scenario')
    assert hasattr(stats, 'total_scenario')
    assert hasattr(stats, 'calculation_date')
    assert hasattr(stats, 'first_entry_date')
    assert hasattr(stats, 'days_since_entry')
    print("✓ ILRStatistics structure complete")


def run_all_ilr_statistics_tests():
    """Run all ILRStatisticsEngine tests."""
    print("Starting ILRStatisticsEngine Test Suite...")
    print("=" * 60)
    
    try:
        test_ilr_statistics_engine_initialization()
        print()
        
        test_leap_year_requirement_calculation()
        print()
        
        test_ilr_counting_methods()
        print()
        
        test_global_statistics()
        print()
        
        test_progress_calculation()
        print()
        
        test_progress_summary()
        print()
        
        test_ilr_eligibility()
        print()
        
        test_monthly_and_yearly_statistics()
        print()
        
        test_edge_cases()
        print()
        
        test_data_class_properties()
        print()
        
        print("=" * 60)
        print("✅ ALL ILR STATISTICS ENGINE TESTS PASSED!")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_ilr_statistics_tests()