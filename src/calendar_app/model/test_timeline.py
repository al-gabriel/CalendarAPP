"""
Comprehensive Test Suite for timeline.py
Tests all functionality of DateTimeline class.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import calendar

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.model.day import Day, DayClassification
from calendar_app.model.timeline import DateTimeline
from calendar_app.model.trips import TripClassifier


def setup_test():
    """Setup function called before each test to ensure clean state."""
    DateTimeline.reset_singleton()


def teardown_test():
    """Teardown function called after each test to clean up."""
    DateTimeline.reset_singleton()


class MockAppConfig:
    """Mock AppConfig for testing without JSON files."""
    
    def __init__(self, start_year=2023, end_year=2040, first_entry_date="29-03-2023"):
        self.start_year = start_year
        self.end_year = end_year
        self.first_entry_date = first_entry_date
        # Mock the parsed date object
        from datetime import datetime
        self.first_entry_date_obj = datetime.strptime(first_entry_date, "%d-%m-%Y").date()
        # Add other required attributes
        self.objective_years = 10
        self.processing_buffer_years = 1


class MockTripClassifier:
    """Mock TripClassifier for testing without real trip data."""
    
    def __init__(self, config):
        self.config = config
        # Mock empty trip data for testing
        self._mock_trips = {}  # date -> trip_info mapping
    
    def get_day_trip_info(self, target_date):
        """Mock method - returns None (no trips)"""
        return self._mock_trips.get(target_date)
    
    def is_trip_day(self, target_date):
        """Mock method - returns False (no trips)"""
        return target_date in self._mock_trips
    
    def is_short_trip_day(self, target_date):
        """Mock method - returns False (no short trips)"""
        trip_info = self._mock_trips.get(target_date)
        return trip_info is not None and trip_info.get("is_short_trip", False)
    
    def is_long_trip_day(self, target_date):
        """Mock method - returns False (no long trips)"""
        trip_info = self._mock_trips.get(target_date)
        return trip_info is not None and not trip_info.get("is_short_trip", True)
    
    def get_trip_summary(self, target_date):
        """Mock method - returns UK residence summary"""
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
    
    def add_mock_trip(self, start_date, end_date, is_short_trip=True, trip_id="mock_trip"):
        """Add a mock trip for testing"""
        from datetime import timedelta
        current_date = start_date
        trip_info = {
            "id": trip_id,
            "is_short_trip": is_short_trip,
            "departure_date_obj": start_date,
            "return_date_obj": end_date,
            "trip_length_days": (end_date - start_date).days + 1
        }
        
        while current_date <= end_date:
            self._mock_trips[current_date] = trip_info
            current_date += timedelta(days=1)


class MockVisaPeriodClassifier:
    """Mock VisaClassifier for testing without real visa data."""
    
    def __init__(self, config, visaPeriods_data=None):
        self.config = config
        self.visaPeriods_data = visaPeriods_data or []
        # Mock empty visa data for testing
        self._mock_visaPeriod_periods = {}  # date -> visaPeriod_info mapping
    
    def get_day_visaPeriod_info(self, target_date):
        """Mock method - returns None (no visa periods)"""
        return self._mock_visaPeriod_periods.get(target_date)
    
    def is_visaPeriod_day(self, target_date):
        """Mock method - returns False (no visa periods)"""
        return target_date in self._mock_visaPeriod_periods
    
    def get_visaPeriod_summary(self, target_date):
        """Mock method - returns no visa period summary"""
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
    
    def add_mock_visaPeriod(self, start_date, end_date, visaPeriod_id="mock_visa", salary="£30000.00"):
        """Add a mock visa period for testing"""
        from datetime import timedelta
        current_date = start_date
        
        while current_date <= end_date:
            self._mock_visaPeriod_periods[current_date] = {
                'visaPeriod_id': visaPeriod_id,
                'visaPeriod_label': f'Mock Visa {visaPeriod_id}',
                'start_date': start_date,
                'end_date': end_date,
                'gross_salary': salary
            }
            current_date += timedelta(days=1)


def test_date_timeline_creation():
    """Test DateTimeline creation and singleton behavior."""
    print("=== Testing DateTimeline Creation ===")
    
    setup_test()
    
    # Test configuration-only creation
    config = MockAppConfig(2023, 2025, "01-01-2023")  # Smaller range for faster testing
    
    # Test from_config method
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline1 = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier)
    assert timeline1 is not None, "Timeline should be created"
    assert timeline1.start_year == 2023, f"Expected start_year 2023, got {timeline1.start_year}"
    assert timeline1.end_year == 2025, f"Expected end_year 2025, got {timeline1.end_year}"
    assert timeline1.config == config, "Timeline should store config reference"
    print("✓ Timeline creation from config works")
    
    # Test singleton behavior
    timeline2 = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier)  # Same config
    assert timeline1 is timeline2, "Should return same instance with same config"
    print("✓ Singleton behavior works with same config")
    
    # Test singleton with different config
    different_config = MockAppConfig(2023, 2026, "01-01-2023")  # Different end year
    different_mock_classifier = MockTripClassifier(different_config)
    different_mock_visaPeriod_classifier = MockVisaPeriodClassifier(different_config)
    try:
        timeline3 = DateTimeline.from_config(different_config, different_mock_classifier, different_mock_visaPeriod_classifier)
        assert False, "Should raise ValueError with different config"
    except ValueError as e:
        assert "Timeline instance exists with range" in str(e), f"Expected specific error message, got: {e}"
        print("✓ Singleton correctly rejects different config")
    
    # Test non-singleton creation
    timeline3 = DateTimeline.from_config(different_config, different_mock_classifier, different_mock_visaPeriod_classifier, use_singleton=False)
    assert timeline3 is not timeline1, "Non-singleton should create new instance"
    assert timeline3.start_year == 2023 and timeline3.end_year == 2026, "Non-singleton should use different config"
    print("✓ Non-singleton creation works")
    
    # Test singleton reset
    DateTimeline.reset_singleton()
    timeline4 = DateTimeline.from_config(different_config, different_mock_classifier, different_mock_visaPeriod_classifier)
    assert timeline4 is not timeline1, "After reset, should create new instance"
    print("✓ Singleton reset works")
    
    print("✓ All DateTimeline creation tests passed\n")
    teardown_test()


def test_date_timeline_basic_methods():
    """Test DateTimeline basic methods."""
    print("=== Testing DateTimeline Basic Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2025, "01-01-2023")
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Test get_day method
    test_date = date(2024, 6, 15)
    day = timeline.get_day(test_date)
    assert day is not None, f"Expected Day object for {test_date}, got None"
    assert day.date == test_date, f"Expected date {test_date}, got {day.date}"
    assert isinstance(day, Day), f"Expected Day instance, got {type(day)}"
    print("✓ get_day() works correctly")
    
    # Test get_day for date outside range
    outside_date = date(2022, 1, 1)  # Before 2023
    day_outside = timeline.get_day(outside_date)
    assert day_outside is None, f"Expected None for date outside range, got {day_outside}"
    print("✓ get_day() returns None for dates outside range")
    
    # Test is_date_in_range
    assert timeline.is_date_in_range(test_date) == True, "Date 2024-06-15 should be in range"
    assert timeline.is_date_in_range(outside_date) == False, "Date 2022-01-01 should not be in range"
    print("✓ is_date_in_range() works correctly")
    
    # Test get_total_days
    total_days = timeline.get_total_days()
    expected_days = (date(2025, 12, 31) - date(2023, 1, 1)).days + 1  # +1 because it's inclusive
    assert total_days == expected_days, f"Expected {expected_days} total days, got {total_days}"
    print("✓ get_total_days() correct")
    
    # Test get_date_range_info
    range_info = timeline.get_date_range_info()
    assert range_info['start_date'] == date(2023, 1, 1), f"Expected start 2023-01-01, got {range_info['start_date']}"
    assert range_info['end_date'] == date(2025, 12, 31), f"Expected end 2025-12-31, got {range_info['end_date']}"
    assert range_info['total_days'] == expected_days, f"Expected {expected_days} total days in range_info"
    print("✓ get_date_range_info() correct")
    
    print("✓ All DateTimeline basic methods tests passed\n")
    teardown_test()


def test_date_timeline_month_year_methods():
    """Test DateTimeline month and year methods."""
    print("=== Testing DateTimeline Month/Year Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2025, "01-01-2023")
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Test get_days_in_month for regular month
    april_2024_days = timeline.get_days_in_month(2024, 4)
    assert len(april_2024_days) == 30, f"Expected 30 days in April 2024, got {len(april_2024_days)}"
    assert april_2024_days[0].date == date(2024, 4, 1), f"Expected first day to be 2024-04-01, got {april_2024_days[0].date}"
    assert april_2024_days[-1].date == date(2024, 4, 30), f"Expected last day to be 2024-04-30, got {april_2024_days[-1].date}"
    print("✓ get_days_in_month() works for regular month")
    
    # Test get_days_in_month for leap year February
    feb_2024_days = timeline.get_days_in_month(2024, 2)
    assert len(feb_2024_days) == 29, f"Expected 29 days in February 2024 (leap year), got {len(feb_2024_days)}"
    assert feb_2024_days[-1].date == date(2024, 2, 29), f"Expected last day to be 2024-02-29, got {feb_2024_days[-1].date}"
    print("✓ get_days_in_month() works for leap year February")
    
    # Test get_days_in_month for December
    dec_2024_days = timeline.get_days_in_month(2024, 12)
    assert len(dec_2024_days) == 31, f"Expected 31 days in December 2024, got {len(dec_2024_days)}"
    assert dec_2024_days[-1].date == date(2024, 12, 31), f"Expected last day to be 2024-12-31, got {dec_2024_days[-1].date}"
    print("✓ get_days_in_month() works for December")
    
    # Test get_days_in_year
    days_2024 = timeline.get_days_in_year(2024)
    expected_2024_days = 366  # 2024 is a leap year
    assert len(days_2024) == expected_2024_days, f"Expected {expected_2024_days} days in 2024, got {len(days_2024)}"
    assert days_2024[0].date == date(2024, 1, 1), f"Expected first day to be 2024-01-01, got {days_2024[0].date}"
    assert days_2024[-1].date == date(2024, 12, 31), f"Expected last day to be 2024-12-31, got {days_2024[-1].date}"
    print("✓ get_days_in_year() works correctly")
    
    print("✓ All DateTimeline month/year methods tests passed\n")
    teardown_test()


def test_date_timeline_classification_methods():
    """Test DateTimeline classification methods."""
    print("=== Testing DateTimeline Classification Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2025, "01-03-2023")  # March 1st first entry
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Initially, days should be classified as PRE_ENTRY or UK_RESIDENCE
    pre_entry_day = timeline.get_day(date(2023, 2, 15))  # Before first entry
    uk_residence_day = timeline.get_day(date(2023, 4, 15))  # After first entry
    
    assert pre_entry_day.classification == DayClassification.PRE_ENTRY, f"Expected PRE_ENTRY, got {pre_entry_day.classification}"
    assert uk_residence_day.classification == DayClassification.UK_RESIDENCE, f"Expected UK_RESIDENCE, got {uk_residence_day.classification}"
    print("✓ Initial classification correct")
    
    # Test update_day_classification
    success = timeline.update_day_classification(
        date(2023, 4, 15), 
        DayClassification.SHORT_TRIP,
        trip_info={"trip_id": "test_trip"},
        visaPeriod="Student Visa"
    )
    assert success == True, "update_day_classification should return True for valid date"
    
    updated_day = timeline.get_day(date(2023, 4, 15))
    assert updated_day.classification == DayClassification.SHORT_TRIP, f"Expected SHORT_TRIP after update, got {updated_day.classification}"
    assert updated_day.trip_info["trip_id"] == "test_trip", f"Expected trip_info to be set, got {updated_day.trip_info}"
    assert updated_day.visaPeriod == "Student Visa", f"Expected visaPeriod to be set, got {updated_day.visaPeriod}"
    print("✓ update_day_classification() works correctly")
    
    # Test get_days_by_classification
    short_trip_days = timeline.get_days_by_classification(DayClassification.SHORT_TRIP)
    assert len(short_trip_days) == 1, f"Expected 1 short trip day, got {len(short_trip_days)}"
    assert short_trip_days[0].date == date(2023, 4, 15), f"Expected the updated day in results"
    print("✓ get_days_by_classification() works correctly")
    
    # Test get_classification_counts_total
    total_counts = timeline.get_classification_counts_total()
    assert DayClassification.PRE_ENTRY in total_counts, "PRE_ENTRY should be in counts"
    assert DayClassification.UK_RESIDENCE in total_counts, "UK_RESIDENCE should be in counts"
    assert DayClassification.SHORT_TRIP in total_counts, "SHORT_TRIP should be in counts"
    assert total_counts[DayClassification.SHORT_TRIP] == 1, f"Expected 1 SHORT_TRIP day, got {total_counts[DayClassification.SHORT_TRIP]}"
    print("✓ get_classification_counts_total() works correctly")
    
    print("✓ All DateTimeline classification methods tests passed\n")
    teardown_test()


def test_date_timeline_ilr_methods():
    """Test DateTimeline ILR-specific methods."""
    print("=== Testing DateTimeline ILR Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "01-06-2023")  # June 1st first entry, smaller range for testing
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Manually set up some test classifications to verify ILR counting
    timeline.update_day_classification(date(2023, 7, 1), DayClassification.UK_RESIDENCE)  
    timeline.update_day_classification(date(2023, 7, 2), DayClassification.SHORT_TRIP)
    timeline.update_day_classification(date(2023, 7, 3), DayClassification.LONG_TRIP)
    # Days before 2023-06-01 should already be PRE_ENTRY
    
    # Test get_ilr_counts_total
    ilr_counts = timeline.get_ilr_counts_total()
    assert 'ilr_in_uk_days' in ilr_counts, "Should have ilr_in_uk_days key"
    assert 'short_trip_days' in ilr_counts, "Should have short_trip_days key"
    assert 'ilr_total_days' in ilr_counts, "Should have ilr_total_days key"
    assert 'long_trip_days' in ilr_counts, "Should have long_trip_days key"
    assert 'pre_entry_days' in ilr_counts, "Should have pre_entry_days key"
    
    # Verify specific counts for our test data
    assert ilr_counts['short_trip_days'] >= 1, f"Expected at least 1 short trip day, got {ilr_counts['short_trip_days']}"
    assert ilr_counts['long_trip_days'] >= 1, f"Expected at least 1 long trip day, got {ilr_counts['long_trip_days']}"
    assert ilr_counts['pre_entry_days'] > 0, f"Expected some pre-entry days, got {ilr_counts['pre_entry_days']}"
    
    # ILR total should be ilr_in_uk_days + short_trip_days
    expected_total = ilr_counts['ilr_in_uk_days'] + ilr_counts['short_trip_days']
    assert ilr_counts['ilr_total_days'] == expected_total, f"Expected ILR total {expected_total}, got {ilr_counts['ilr_total_days']}"
    print("✓ get_ilr_counts_total() works correctly")
    
    # Test get_ilr_counts_for_month
    july_counts = timeline.get_ilr_counts_for_month(2023, 7)
    assert july_counts['short_trip_days'] >= 1, f"Expected at least 1 short trip day in July, got {july_counts['short_trip_days']}"
    assert july_counts['long_trip_days'] >= 1, f"Expected at least 1 long trip day in July, got {july_counts['long_trip_days']}"
    print("✓ get_ilr_counts_for_month() works correctly")
    
    # Test get_ilr_counts_for_year
    year_2023_counts = timeline.get_ilr_counts_for_year(2023)
    assert year_2023_counts['pre_entry_days'] > 0, f"Expected some pre-entry days in 2023, got {year_2023_counts['pre_entry_days']}"
    assert year_2023_counts['ilr_total_days'] >= 2, f"Expected at least 2 ILR total days, got {year_2023_counts['ilr_total_days']}"
    print("✓ get_ilr_counts_for_year() works correctly")
    
    print("✓ All DateTimeline ILR methods tests passed\n")
    teardown_test()


def test_date_timeline_auto_classification():
    """Test DateTimeline automatic classification methods."""
    print("=== Testing DateTimeline Auto Classification ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "01-06-2023")  # June 1st first entry
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Initially timeline should be auto-classified, but let's test the methods explicitly
    
    # Test classify_pre_entry_days
    pre_entry_count = timeline.classify_pre_entry_days()
    # Should return 0 because days are already classified during initialization
    print(f"  Pre-entry days classified: {pre_entry_count}")
    
    # Verify that days before first entry are properly classified
    test_pre_entry = timeline.get_day(date(2023, 5, 15))
    assert test_pre_entry.classification == DayClassification.PRE_ENTRY, f"Expected PRE_ENTRY, got {test_pre_entry.classification}"
    print("✓ classify_pre_entry_days() works correctly")
    
    # Test auto_classify_all_days by creating a timeline with some UNKNOWN days
    # Create timeline but manually set some days to UNKNOWN to test the method
    test_day = timeline.get_day(date(2023, 7, 15))
    test_day.classification = DayClassification.UNKNOWN
    
    classification_result = timeline.auto_classify_all_days()
    assert 'pre_entry_classified' in classification_result, "Should have pre_entry_classified count"
    assert 'uk_residence_classified' in classification_result, "Should have uk_residence_classified count"
    assert 'total_classified' in classification_result, "Should have total_classified count"
    
    # Verify the day was reclassified
    reclassified_day = timeline.get_day(date(2023, 7, 15))
    assert reclassified_day.classification == DayClassification.UK_RESIDENCE, f"Expected UK_RESIDENCE after auto-classification, got {reclassified_day.classification}"
    print("✓ auto_classify_all_days() works correctly")
    
    # Test validate_no_unknown_days
    try:
        is_valid = timeline.validate_no_unknown_days()
        assert is_valid == True, "Timeline should be valid with no UNKNOWN days"
        print("✓ validate_no_unknown_days() passes with fully classified timeline")
    except ValueError:
        assert False, "Timeline should be valid after auto-classification"
    
    # Test validate_no_unknown_days with UNKNOWN days
    test_day.classification = DayClassification.UNKNOWN  # Set one back to UNKNOWN
    try:
        timeline.validate_no_unknown_days()
        assert False, "Should raise ValueError with UNKNOWN days"
    except ValueError as e:
        assert "Timeline validation failed" in str(e), f"Expected specific error message, got: {e}"
        print("✓ validate_no_unknown_days() correctly raises error with UNKNOWN days")
    
    print("✓ All DateTimeline auto classification tests passed\n")
    teardown_test()


def test_date_timeline_summary_methods():
    """Test DateTimeline summary methods."""
    print("=== Testing DateTimeline Summary Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "01-06-2023")  # Smaller range for predictable testing
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    # Test get_classification_summary without debug
    summary = timeline.get_classification_summary()
    
    # Verify required keys
    required_keys = ['total_days', 'date_range', 'actual_start_date', 'actual_end_date', 'first_entry_date', 'ilr_counts']
    for key in required_keys:
        assert key in summary, f"Expected key '{key}' in summary"
    
    # Verify data types and values
    assert isinstance(summary['total_days'], int), f"total_days should be int, got {type(summary['total_days'])}"
    assert summary['total_days'] > 0, f"Expected positive total_days, got {summary['total_days']}"
    assert isinstance(summary['ilr_counts'], dict), f"ilr_counts should be dict, got {type(summary['ilr_counts'])}"
    print("✓ get_classification_summary() basic functionality works")
    
    # Test get_classification_summary with debug
    debug_summary = timeline.get_classification_summary(debug=True)
    assert 'debug_info' in debug_summary, "Debug summary should have debug_info"
    assert 'classification_counts' in debug_summary['debug_info'], "Debug info should have classification_counts"
    assert 'classification_progress' in debug_summary['debug_info'], "Debug info should have classification_progress"
    
    debug_progress = debug_summary['debug_info']['classification_progress']
    assert 'classified_percentage' in debug_progress, "Should have classified_percentage"
    assert 'unknown_percentage' in debug_progress, "Should have unknown_percentage"
    assert debug_progress['classified_percentage'] + debug_progress['unknown_percentage'] == 100.0, "Percentages should sum to 100"
    print("✓ get_classification_summary() debug functionality works")
    
    # Test get_classification_summary with date range
    start_date = date(2023, 7, 1)
    end_date = date(2023, 7, 31)
    range_summary = timeline.get_classification_summary(start_date=start_date, end_date=end_date)
    
    assert range_summary['actual_start_date'] == start_date.strftime('%d-%m-%Y'), f"Expected start date in summary"
    assert range_summary['actual_end_date'] == end_date.strftime('%d-%m-%Y'), f"Expected end date in summary"
    assert range_summary['total_days'] == 31, f"Expected 31 days for July, got {range_summary['total_days']}"
    print("✓ get_classification_summary() with date range works")
    
    print("✓ All DateTimeline summary methods tests passed\n")
    teardown_test()


def test_leap_year_boundary_conditions():
    """Test leap year boundary conditions and edge cases."""
    print("=== Testing Leap Year Boundary Conditions ===")
    
    setup_test()
    
    # Test timeline spanning leap year boundary
    config_leap = MockAppConfig(2023, 2024, "01-01-2023")  # Includes 2024 leap year
    mock_trip_classifier_leap = MockTripClassifier(config_leap)
    mock_visaPeriod_classifier_leap = MockVisaPeriodClassifier(config_leap)
    timeline_leap = DateTimeline.from_config(config_leap, mock_trip_classifier_leap, mock_visaPeriod_classifier_leap, use_singleton=False)
    
    # Test leap day exists
    leap_day = timeline_leap.get_day(date(2024, 2, 29))
    assert leap_day is not None, "Leap day 2024-02-29 should exist in timeline"
    assert leap_day.date == date(2024, 2, 29), f"Expected date 2024-02-29, got {leap_day.date}"
    print("✓ Leap day (Feb 29, 2024) handled correctly")
    
    # Test February 2024 has 29 days
    feb_2024_days = timeline_leap.get_days_in_month(2024, 2)
    assert len(feb_2024_days) == 29, f"Expected 29 days in February 2024, got {len(feb_2024_days)}"
    print("✓ February 2024 has correct number of days (29)")
    
    # Test year boundary transition
    dec_31_2023 = timeline_leap.get_day(date(2023, 12, 31))
    jan_01_2024 = timeline_leap.get_day(date(2024, 1, 1))
    
    assert dec_31_2023 is not None, "Dec 31, 2023 should exist"
    assert jan_01_2024 is not None, "Jan 1, 2024 should exist"
    print("✓ Year transition (Dec 31 -> Jan 1) works correctly")
    
    print("✓ All leap year boundary condition tests passed\n")
    teardown_test()


def test_error_conditions():
    """Test error conditions and edge cases."""
    print("=== Testing Error Conditions ===")
    
    setup_test()
    
    # Test creation with invalid config
    class InvalidConfig:
        pass
    
    invalid_config = InvalidConfig()
    mock_trip_classifier = MockTripClassifier(MockAppConfig(2023, 2024, "01-01-2023"))
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(MockAppConfig(2023, 2024, "01-01-2023"))
    
    try:
        timeline = DateTimeline(invalid_config, mock_trip_classifier, mock_visaPeriod_classifier)
        assert False, "Should raise AttributeError with invalid config"
    except AttributeError as e:
        assert "start_year and end_year" in str(e), f"Expected specific error message, got: {e}"
        print("✓ Invalid config correctly raises AttributeError")
    
    # Test update_day_classification with invalid date
    config = MockAppConfig(2023, 2024, "01-01-2023")
    mock_trip_classifier = MockTripClassifier(config)
    mock_visaPeriod_classifier = MockVisaPeriodClassifier(config)
    timeline = DateTimeline.from_config(config, mock_trip_classifier, mock_visaPeriod_classifier, use_singleton=False)
    
    invalid_date = date(2022, 1, 1)  # Outside range
    success = timeline.update_day_classification(invalid_date, DayClassification.UK_RESIDENCE)
    assert success == False, "update_day_classification should return False for invalid date"
    print("✓ update_day_classification correctly handles invalid dates")
    
    # Test update_date_range_classification
    updated_count = timeline.update_date_range_classification(
        date(2023, 1, 1), date(2023, 1, 3),
        DayClassification.SHORT_TRIP
    )
    assert updated_count == 3, f"Expected 3 days updated, got {updated_count}"
    
    # Verify the updates
    for i in range(1, 4):
        day = timeline.get_day(date(2023, 1, i))
        assert day.classification == DayClassification.SHORT_TRIP, f"Day {i} should be SHORT_TRIP"
    print("✓ update_date_range_classification works correctly")
    
    print("✓ All error condition tests passed\n")
    teardown_test()


def run_all_timeline_tests():
    """Run all DateTimeline tests."""
    print("=== Running All DateTimeline Tests ===\n")
    
    test_date_timeline_creation()
    test_date_timeline_basic_methods()
    test_date_timeline_month_year_methods()
    test_date_timeline_classification_methods()
    test_date_timeline_ilr_methods()
    test_date_timeline_auto_classification()
    test_date_timeline_summary_methods()
    test_leap_year_boundary_conditions()
    test_error_conditions()
    
    print("=== All DateTimeline Tests Completed Successfully ===\n")


if __name__ == "__main__":
    run_all_timeline_tests()