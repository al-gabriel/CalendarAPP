"""
DEPRECATED: This file has been split into modular components.

Comprehensive Test Suite for dates.py
Tests all functionality of Day and DateTimeline classes with hardcoded values.

This file has been refactored into:
- tests_day.py: Contains Day class and DayClassification enum
- tests_timeline.py: Contains DateTimeline class

Please update your imports:
- from calendar_app.model.day import Day, DayClassification
- from calendar_app.model.timeline import DateTimeline

This file will be removed in a future version.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
import calendar

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.config import AppConfig
from calendar_app.model.dates import Day, DateTimeline, DayClassification


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


def test_day_classification_enum():
    """Test DayClassification enum values."""
    print("=== Testing DayClassification Enum ===")
    
    # Test all enum values exist
    expected_values = {
        'UK_RESIDENCE': "uk_residence",
        'SHORT_TRIP': "short_trip", 
        'LONG_TRIP': "long_trip",
        'PRE_ENTRY': "pre_entry",
        'UNKNOWN': "unknown"
    }
    
    for name, value in expected_values.items():
        enum_item = getattr(DayClassification, name)
        assert enum_item.value == value, f"Expected {name} to have value {value}, got {enum_item.value}"
        print(f"✓ {name} = {enum_item.value}")
    
    print("✓ All DayClassification enum values correct\n")


def test_day_basic_functionality():
    """Test Day class basic functionality."""
    print("=== Testing Day Class Basic Functionality ===")
    
    # Create test date
    test_date = date(2024, 3, 15)  # March 15, 2024 (Friday)
    day = Day(test_date)
    
    # Test initialization
    assert day.date == test_date, f"Expected date {test_date}, got {day.date}"
    assert day.classification == DayClassification.UNKNOWN, f"Expected UNKNOWN classification, got {day.classification}"
    assert day.trip_info is None, f"Expected None trip_info, got {day.trip_info}"
    assert day.visa_period is None, f"Expected None visa_period, got {day.visa_period}"
    print("✓ Day initialization correct")
    
    # Test properties
    assert day.year == 2024, f"Expected year 2024, got {day.year}"
    assert day.month == 3, f"Expected month 3, got {day.month}"
    assert day.day == 15, f"Expected day 15, got {day.day}"
    assert day.weekday == 4, f"Expected weekday 4 (Friday), got {day.weekday}"  # Friday = 4
    assert day.is_weekend == False, f"Expected Friday to not be weekend, got {day.is_weekend}"
    print("✓ Day properties correct")
    
    # Test weekend detection
    weekend_day = Day(date(2024, 3, 16))  # Saturday
    assert weekend_day.is_weekend == True, f"Expected Saturday to be weekend, got {weekend_day.is_weekend}"
    print("✓ Weekend detection correct")
    
    # Test string representation
    str_repr = str(day)
    expected_str = "Day(15-03-2024, unknown)"
    assert str_repr == expected_str, f"Expected '{expected_str}', got '{str_repr}'"
    print("✓ String representation correct")
    
    print("✓ All Day class basic functionality tests passed\n")


def test_day_ilr_counting_methods():
    """Test Day class ILR counting methods."""
    print("=== Testing Day ILR Counting Methods ===")
    
    first_entry = date(2023, 3, 29)
    
    # Test UK residence day (after first entry)
    uk_day = Day(date(2023, 4, 15))
    uk_day.classification = DayClassification.UK_RESIDENCE
    
    assert uk_day.counts_as_ilr_in_uk_day(first_entry) == True, "UK residence day should count as ILR in-UK"
    assert uk_day.counts_as_short_trip_day(first_entry) == False, "UK residence day should not count as short trip"
    assert uk_day.counts_as_ilr_total_day(first_entry) == True, "UK residence day should count as ILR total"
    assert uk_day.counts_as_long_trip_day(first_entry) == False, "UK residence day should not count as long trip"
    print("✓ UK residence day counting correct")
    
    # Test short trip day (after first entry)
    short_trip_day = Day(date(2023, 5, 10))
    short_trip_day.classification = DayClassification.SHORT_TRIP
    
    assert short_trip_day.counts_as_ilr_in_uk_day(first_entry) == False, "Short trip day should not count as ILR in-UK"
    assert short_trip_day.counts_as_short_trip_day(first_entry) == True, "Short trip day should count as short trip"
    assert short_trip_day.counts_as_ilr_total_day(first_entry) == True, "Short trip day should count as ILR total"
    assert short_trip_day.counts_as_long_trip_day(first_entry) == False, "Short trip day should not count as long trip"
    print("✓ Short trip day counting correct")
    
    # Test long trip day (after first entry)
    long_trip_day = Day(date(2023, 6, 20))
    long_trip_day.classification = DayClassification.LONG_TRIP
    
    assert long_trip_day.counts_as_ilr_in_uk_day(first_entry) == False, "Long trip day should not count as ILR in-UK"
    assert long_trip_day.counts_as_short_trip_day(first_entry) == False, "Long trip day should not count as short trip"
    assert long_trip_day.counts_as_ilr_total_day(first_entry) == False, "Long trip day should not count as ILR total"
    assert long_trip_day.counts_as_long_trip_day(first_entry) == True, "Long trip day should count as long trip"
    print("✓ Long trip day counting correct")
    
    # Test pre-entry day (before first entry)
    pre_entry_day = Day(date(2023, 3, 15))  # Before March 29
    pre_entry_day.classification = DayClassification.UK_RESIDENCE  # Even if marked as UK residence
    
    assert pre_entry_day.counts_as_ilr_in_uk_day(first_entry) == False, "Pre-entry day should not count regardless of classification"
    assert pre_entry_day.counts_as_short_trip_day(first_entry) == False, "Pre-entry day should not count regardless of classification"
    assert pre_entry_day.counts_as_ilr_total_day(first_entry) == False, "Pre-entry day should not count regardless of classification"
    assert pre_entry_day.counts_as_long_trip_day(first_entry) == False, "Pre-entry day should not count regardless of classification"
    print("✓ Pre-entry day counting correct")
    
    print("✓ All Day ILR counting method tests passed\n")


def test_date_timeline_creation():
    """Test DateTimeline creation and singleton behavior."""
    print("=== Testing DateTimeline Creation ===")
    
    setup_test()
    
    # Test configuration-only creation
    config = MockAppConfig(2023, 2025, "01-01-2023")  # Smaller range for faster testing
    
    # Test from_config method
    timeline1 = DateTimeline.from_config(config)
    assert timeline1 is not None, "Timeline should be created"
    assert timeline1.start_year == 2023, f"Expected start_year 2023, got {timeline1.start_year}"
    assert timeline1.end_year == 2025, f"Expected end_year 2025, got {timeline1.end_year}"
    assert timeline1.config == config, "Timeline should store config reference"
    print("✓ Timeline creation from config works")
    
    # Test singleton behavior
    timeline2 = DateTimeline.from_config(config)  # Same config
    assert timeline1 is timeline2, "Should return same instance with same config"
    print("✓ Singleton behavior works with same config")
    
    # Test singleton with different config
    different_config = MockAppConfig(2023, 2026, "01-01-2023")  # Different end year
    try:
        timeline3 = DateTimeline.from_config(different_config)
        assert False, "Should raise ValueError with different config"
    except ValueError as e:
        assert "Timeline instance exists with range" in str(e), f"Expected specific error message, got: {e}"
        print("✓ Singleton correctly rejects different config")
    
    # Test non-singleton creation
    timeline3 = DateTimeline.from_config(different_config, use_singleton=False)
    assert timeline3 is not timeline1, "Non-singleton should create new instance"
    assert timeline3.start_year == 2023 and timeline3.end_year == 2026, "Non-singleton should use different config"
    print("✓ Non-singleton creation works")
    
    # Test singleton reset
    DateTimeline.reset_singleton()
    timeline4 = DateTimeline.from_config(different_config)
    assert timeline4 is not timeline1, "After reset, should create new instance"
    print("✓ Singleton reset works")
    
    print("✓ All DateTimeline creation tests passed\n")
    teardown_test()


def test_date_timeline_basic_methods():
    """Test DateTimeline basic methods."""
    print("=== Testing DateTimeline Basic Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "01-06-2023")  # Small range, mid-year start
    timeline = DateTimeline.from_config(config)
    
    # Test total days calculation - calculate dynamically
    start_date = date(2023, 1, 1)
    end_date = date(2024, 12, 31)
    expected_days = (end_date - start_date).days + 1  # +1 for inclusive range
    actual_days = timeline.get_total_days()
    assert actual_days == expected_days, f"Expected {expected_days} total days, got {actual_days}"
    print(f"✓ Total days calculation correct: {actual_days} days")
    
    # Test get_day method
    test_date = date(2023, 7, 15)
    day_obj = timeline.get_day(test_date)
    assert day_obj is not None, "Should return Day object for valid date"
    assert day_obj.date == test_date, f"Expected {test_date}, got {day_obj.date}"
    print("✓ get_day method works")
    
    # Test get_day for invalid date
    invalid_date = date(2022, 1, 1)  # Before timeline range
    invalid_day = timeline.get_day(invalid_date)
    assert invalid_day is None, "Should return None for date outside range"
    print("✓ get_day correctly handles invalid dates")
    
    # Test is_date_in_range
    assert timeline.is_date_in_range(test_date) == True, "Valid date should be in range"
    assert timeline.is_date_in_range(invalid_date) == False, "Invalid date should not be in range"
    print("✓ is_date_in_range method works")
    
    # Test get_date_range_info
    range_info = timeline.get_date_range_info()
    assert 'start_date' in range_info, "Range info should contain start_date"
    assert 'end_date' in range_info, "Range info should contain end_date"
    assert 'total_days' in range_info, "Range info should contain total_days"
    assert range_info['start_date'] == date(2023, 1, 1), "Start date should be January 1st"
    assert range_info['end_date'] == date(2024, 12, 31), "End date should be December 31st"
    print("✓ get_date_range_info method works")
    
    print("✓ All DateTimeline basic method tests passed\n")


def test_date_timeline_month_year_methods():
    """Test DateTimeline month and year methods."""
    print("=== Testing DateTimeline Month/Year Methods ===")
    
    DateTimeline.reset_singleton()
    config = MockAppConfig(2023, 2024, "01-01-2023")
    timeline = DateTimeline.from_config(config)
    
    # Test get_days_in_month
    march_days = timeline.get_days_in_month(2023, 3)
    assert len(march_days) == 31, f"March should have 31 days, got {len(march_days)}"
    assert march_days[0].date == date(2023, 3, 1), "First day should be March 1st"
    assert march_days[-1].date == date(2023, 3, 31), "Last day should be March 31st"
    print("✓ get_days_in_month works for regular month")
    
    # Test February in leap year
    feb_2024_days = timeline.get_days_in_month(2024, 2)
    assert len(feb_2024_days) == 29, f"February 2024 (leap year) should have 29 days, got {len(feb_2024_days)}"
    print("✓ get_days_in_month works for leap year February")
    
    # Test December (edge case)
    dec_days = timeline.get_days_in_month(2024, 12)
    assert len(dec_days) == 31, f"December should have 31 days, got {len(dec_days)}"
    assert dec_days[-1].date == date(2024, 12, 31), "Last day should be December 31st"
    print("✓ get_days_in_month works for December")
    
    # Test get_days_in_year
    year_2023_days = timeline.get_days_in_year(2023)
    assert len(year_2023_days) == 365, f"2023 should have 365 days, got {len(year_2023_days)}"
    assert year_2023_days[0].date == date(2023, 1, 1), "First day should be January 1st"
    assert year_2023_days[-1].date == date(2023, 12, 31), "Last day should be December 31st"
    print("✓ get_days_in_year works for non-leap year")
    
    # Test leap year
    year_2024_days = timeline.get_days_in_year(2024)
    assert len(year_2024_days) == 366, f"2024 should have 366 days, got {len(year_2024_days)}"
    print("✓ get_days_in_year works for leap year")
    
    print("✓ All DateTimeline month/year method tests passed\n")


def test_date_timeline_classification_methods():
    """Test DateTimeline classification methods."""
    print("=== Testing DateTimeline Classification Methods ===")
    
    DateTimeline.reset_singleton()
    config = MockAppConfig(2023, 2024, "01-06-2023")
    timeline = DateTimeline.from_config(config)
    
    # Test update_day_classification
    test_date = date(2023, 7, 15)
    trip_info = {"trip_id": "trip_001", "destination": "Paris"}
    
    success = timeline.update_day_classification(
        test_date, 
        DayClassification.SHORT_TRIP, 
        trip_info=trip_info,
        visa_period="visa_1"
    )
    assert success == True, "Should successfully update day classification"
    
    updated_day = timeline.get_day(test_date)
    assert updated_day.classification == DayClassification.SHORT_TRIP, "Classification should be updated"
    assert updated_day.trip_info == trip_info, "Trip info should be stored"
    assert updated_day.visa_period == "visa_1", "Visa period should be stored"
    print("✓ update_day_classification works")
    
    # Test get_days_by_classification
    short_trip_days = timeline.get_days_by_classification(DayClassification.SHORT_TRIP)
    assert len(short_trip_days) == 1, f"Should have 1 short trip day, got {len(short_trip_days)}"
    assert short_trip_days[0].date == test_date, "Should return the updated day"
    print("✓ get_days_by_classification works")
    
    # Test update_date_range_classification
    start_range = date(2023, 8, 1)
    end_range = date(2023, 8, 5)
    updated_count = timeline.update_date_range_classification(
        start_range, end_range, DayClassification.LONG_TRIP
    )
    assert updated_count == 5, f"Should update 5 days, got {updated_count}"
    
    long_trip_days = timeline.get_days_by_classification(DayClassification.LONG_TRIP)
    assert len(long_trip_days) == 5, f"Should have 5 long trip days, got {len(long_trip_days)}"
    print("✓ update_date_range_classification works")
    
    # Test get_classification_counts_total
    counts = timeline.get_classification_counts_total()
    assert DayClassification.SHORT_TRIP in counts, "Counts should include SHORT_TRIP"
    assert DayClassification.LONG_TRIP in counts, "Counts should include LONG_TRIP"
    assert counts[DayClassification.SHORT_TRIP] == 1, f"Should have 1 short trip day, got {counts[DayClassification.SHORT_TRIP]}"
    assert counts[DayClassification.LONG_TRIP] == 5, f"Should have 5 long trip days, got {counts[DayClassification.LONG_TRIP]}"
    print("✓ get_classification_counts_total works")
    
    print("✓ All DateTimeline classification method tests passed\n")


def test_date_timeline_ilr_methods():
    """Test DateTimeline ILR-specific methods."""
    print("=== Testing DateTimeline ILR Methods ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "29-03-2023")
    timeline = DateTimeline.from_config(config)
    
    # Set up test scenario
    first_entry = date(2023, 3, 29)
    
    # Classify some days manually to test ILR counting
    # Pre-entry days (before March 29) - manually classify a few for testing
    timeline.update_day_classification(date(2023, 3, 15), DayClassification.PRE_ENTRY)
    timeline.update_day_classification(date(2023, 3, 20), DayClassification.PRE_ENTRY)
    
    # For testing, we need to classify ALL pre-entry days to get accurate counts
    # This simulates what auto_classify_all_days would do
    timeline.classify_pre_entry_days()
    
    # UK residence days (after first entry)
    timeline.update_day_classification(date(2023, 3, 30), DayClassification.UK_RESIDENCE)
    timeline.update_day_classification(date(2023, 4, 1), DayClassification.UK_RESIDENCE)
    timeline.update_day_classification(date(2023, 4, 2), DayClassification.UK_RESIDENCE)
    
    # Short trip days (after first entry)
    timeline.update_day_classification(date(2023, 4, 10), DayClassification.SHORT_TRIP)
    timeline.update_day_classification(date(2023, 4, 11), DayClassification.SHORT_TRIP)
    
    # Long trip days (after first entry)
    timeline.update_day_classification(date(2023, 5, 1), DayClassification.LONG_TRIP)
    timeline.update_day_classification(date(2023, 5, 2), DayClassification.LONG_TRIP)
    timeline.update_day_classification(date(2023, 5, 3), DayClassification.LONG_TRIP)
    
    # Test get_ilr_counts_total
    ilr_counts = timeline.get_ilr_counts_total()
    
    expected_keys = ['ilr_in_uk_days', 'short_trip_days', 'ilr_total_days', 'long_trip_days', 'pre_entry_days']
    for key in expected_keys:
        assert key in ilr_counts, f"ILR counts should contain key: {key}"
    
    assert ilr_counts['ilr_in_uk_days'] == 3, f"Expected 3 ILR in-UK days, got {ilr_counts['ilr_in_uk_days']}"
    assert ilr_counts['short_trip_days'] == 2, f"Expected 2 short trip days, got {ilr_counts['short_trip_days']}"
    assert ilr_counts['ilr_total_days'] == 5, f"Expected 5 ILR total days, got {ilr_counts['ilr_total_days']}"
    assert ilr_counts['long_trip_days'] == 3, f"Expected 3 long trip days, got {ilr_counts['long_trip_days']}"
    
    # Calculate expected pre-entry days dynamically
    timeline_start = date(2023, 1, 1)
    expected_pre_entry = (first_entry - timeline_start).days
    assert ilr_counts['pre_entry_days'] == expected_pre_entry, f"Expected {expected_pre_entry} pre-entry days, got {ilr_counts['pre_entry_days']}"
    
    print("✓ get_ilr_counts_total works correctly")
    
    # Test get_ilr_counts_for_month (April 2023)
    april_counts = timeline.get_ilr_counts_for_month(2023, 4)
    assert april_counts['ilr_in_uk_days'] == 2, f"April should have 2 ILR in-UK days, got {april_counts['ilr_in_uk_days']}"
    assert april_counts['short_trip_days'] == 2, f"April should have 2 short trip days, got {april_counts['short_trip_days']}"
    assert april_counts['ilr_total_days'] == 4, f"April should have 4 ILR total days, got {april_counts['ilr_total_days']}"
    print("✓ get_ilr_counts_for_month works correctly")
    
    # Test get_ilr_counts_for_year
    year_2023_counts = timeline.get_ilr_counts_for_year(2023)
    assert year_2023_counts['ilr_in_uk_days'] == 3, f"2023 should have 3 ILR in-UK days, got {year_2023_counts['ilr_in_uk_days']}"
    assert year_2023_counts['short_trip_days'] == 2, f"2023 should have 2 short trip days, got {year_2023_counts['short_trip_days']}"
    assert year_2023_counts['long_trip_days'] == 3, f"2023 should have 3 long trip days, got {year_2023_counts['long_trip_days']}"
    print("✓ get_ilr_counts_for_year works correctly")
    
    print("✓ All DateTimeline ILR method tests passed\n")


def test_date_timeline_auto_classification():
    """Test DateTimeline automatic classification methods."""
    print("=== Testing DateTimeline Auto Classification ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "29-03-2023")
    timeline = DateTimeline.from_config(config)
    
    # Test classify_pre_entry_days - calculate expected days dynamically
    first_entry = date(2023, 3, 29)
    timeline_start = date(2023, 1, 1)
    expected_pre_entry = (first_entry - timeline_start).days  # Days from Jan 1 to March 28
    
    pre_entry_count = timeline.classify_pre_entry_days()
    assert pre_entry_count == expected_pre_entry, f"Expected {expected_pre_entry} pre-entry days, got {pre_entry_count}"
    
    # Verify classification
    pre_entry_day = timeline.get_day(date(2023, 3, 15))
    assert pre_entry_day.classification == DayClassification.PRE_ENTRY, "March 15 should be classified as PRE_ENTRY"
    
    entry_day = timeline.get_day(date(2023, 3, 29))
    assert entry_day.classification == DayClassification.UNKNOWN, "March 29 (entry day) should remain UNKNOWN"
    print("✓ classify_pre_entry_days works correctly")
    
    # Test auto_classify_all_days
    classification_result = timeline.auto_classify_all_days()
    
    assert 'pre_entry_classified' in classification_result, "Result should contain pre_entry_classified"
    assert 'uk_residence_classified' in classification_result, "Result should contain uk_residence_classified"
    assert 'total_classified' in classification_result, "Result should contain total_classified"
    
    # Should classify remaining days as UK_RESIDENCE
    post_entry_day = timeline.get_day(date(2023, 3, 29))
    assert post_entry_day.classification == DayClassification.UK_RESIDENCE, "March 29 should be classified as UK_RESIDENCE"
    
    print("✓ auto_classify_all_days works correctly")
    
    # Test validate_no_unknown_days (should pass after auto-classification)
    try:
        result = timeline.validate_no_unknown_days()
        assert result == True, "Validation should pass after auto-classification"
        print("✓ validate_no_unknown_days passes after auto-classification")
    except ValueError as e:
        assert False, f"Validation should not fail after auto-classification: {e}"
    
    # Test validate_no_unknown_days with unknown days
    timeline.update_day_classification(date(2023, 5, 15), DayClassification.UNKNOWN)
    try:
        timeline.validate_no_unknown_days()
        assert False, "Validation should fail with unknown days"
    except ValueError as e:
        assert "Timeline validation failed" in str(e), f"Expected specific error message, got: {e}"
        print("✓ validate_no_unknown_days correctly fails with unknown days")
    
    print("✓ All DateTimeline auto classification method tests passed\n")


def test_date_timeline_summary_methods():
    """Test DateTimeline summary methods."""
    print("=== Testing DateTimeline Summary Methods ===")
    
    DateTimeline.reset_singleton()
    config = MockAppConfig(2023, 2024, "01-01-2023")
    timeline = DateTimeline.from_config(config)
    
    # Set up test data
    timeline.auto_classify_all_days()
    
    # Add some trip days
    timeline.update_date_range_classification(
        date(2023, 5, 1), date(2023, 5, 5), DayClassification.SHORT_TRIP
    )
    timeline.update_date_range_classification(
        date(2023, 8, 1), date(2023, 8, 20), DayClassification.LONG_TRIP
    )
    
    # Test get_classification_summary without debug
    summary = timeline.get_classification_summary()
    
    required_keys = ['total_days', 'date_range', 'actual_start_date', 'actual_end_date', 'first_entry_date', 'ilr_counts']
    for key in required_keys:
        assert key in summary, f"Summary should contain key: {key}"
    
    assert isinstance(summary['total_days'], int), "total_days should be an integer"
    assert 'ilr_counts' in summary, "Summary should contain ilr_counts"
    assert 'debug_info' not in summary, "Summary should not contain debug_info by default"
    print("✓ get_classification_summary works without debug")
    
    # Test get_classification_summary with debug
    debug_summary = timeline.get_classification_summary(debug=True)
    
    assert 'debug_info' in debug_summary, "Debug summary should contain debug_info"
    
    debug_info = debug_summary['debug_info']
    assert 'classification_counts' in debug_info, "Debug info should contain classification_counts"
    assert 'classification_progress' in debug_info, "Debug info should contain classification_progress"
    
    progress = debug_info['classification_progress']
    assert 'classified_percentage' in progress, "Progress should contain classified_percentage"
    assert 'unknown_percentage' in progress, "Progress should contain unknown_percentage"
    print("✓ get_classification_summary works with debug")
    
    # Test get_classification_summary with date range
    range_summary = timeline.get_classification_summary(
        start_date=date(2023, 5, 1), 
        end_date=date(2023, 5, 31)
    )
    
    assert range_summary['actual_start_date'] == "01-05-2023", "Should show specified start date"
    assert range_summary['actual_end_date'] == "31-05-2023", "Should show specified end date"
    assert range_summary['total_days'] == 31, f"May should have 31 days, got {range_summary['total_days']}"
    print("✓ get_classification_summary works with date range")
    
    print("✓ All DateTimeline summary method tests passed\n")


def test_leap_year_boundary_conditions():
    """Test leap year boundary conditions and edge cases."""
    print("=== Testing Leap Year Boundary Conditions ===")
    
    setup_test()
    
    # Test leap year February 29
    config_2024 = MockAppConfig(2024, 2024, "01-01-2024")
    timeline_2024 = DateTimeline.from_config(config_2024)
    
    feb_29_2024 = timeline_2024.get_day(date(2024, 2, 29))
    assert feb_29_2024 is not None, "Feb 29 should exist in leap year 2024"
    assert feb_29_2024.date == date(2024, 2, 29), "Feb 29 date should be correct"
    print("✓ February 29 exists in leap year 2024")
    
    # Test February days count in leap year
    feb_days_2024 = timeline_2024.get_days_in_month(2024, 2)
    assert len(feb_days_2024) == 29, f"February 2024 should have 29 days, got {len(feb_days_2024)}"
    assert feb_days_2024[-1].date == date(2024, 2, 29), "Last day of February 2024 should be 29th"
    print("✓ February 2024 has correct 29 days")
    
    # Test non-leap year February
    setup_test()  # Reset singleton for new timeline
    config_2023 = MockAppConfig(2023, 2023, "01-01-2023")
    timeline_2023 = DateTimeline.from_config(config_2023)
    
    feb_days_2023 = timeline_2023.get_days_in_month(2023, 2)
    assert len(feb_days_2023) == 28, f"February 2023 should have 28 days, got {len(feb_days_2023)}"
    assert feb_days_2023[-1].date == date(2023, 2, 28), "Last day of February 2023 should be 28th"
    print("✓ February 2023 has correct 28 days")
    
    # Test Feb 29 doesn't exist in non-leap year
    feb_29_2023 = timeline_2023.get_day(date(2024, 2, 29))  # This date is outside range
    assert feb_29_2023 is None, "Feb 29 should not exist for 2023 timeline"
    print("✓ February 29 correctly doesn't exist in non-leap year timeline")
    
    # Test leap year transition (Feb 28 -> Feb 29 -> Mar 1)
    setup_test()
    config_transition = MockAppConfig(2024, 2024, "27-02-2024")
    timeline_transition = DateTimeline.from_config(config_transition)
    
    feb_28 = timeline_transition.get_day(date(2024, 2, 28))
    feb_29 = timeline_transition.get_day(date(2024, 2, 29))
    mar_01 = timeline_transition.get_day(date(2024, 3, 1))
    
    assert all(day is not None for day in [feb_28, feb_29, mar_01]), "All transition days should exist"
    print("✓ Leap year transition days (Feb 28 -> Feb 29 -> Mar 1) all exist")
    
    # Test year-end to year-start transition
    setup_test()
    config_year_transition = MockAppConfig(2023, 2024, "30-12-2023")
    timeline_year = DateTimeline.from_config(config_year_transition)
    
    dec_31_2023 = timeline_year.get_day(date(2023, 12, 31))
    jan_01_2024 = timeline_year.get_day(date(2024, 1, 1))
    
    assert dec_31_2023 is not None, "Dec 31, 2023 should exist"
    assert jan_01_2024 is not None, "Jan 1, 2024 should exist"
    print("✓ Year transition (Dec 31 -> Jan 1) works correctly")
    
    print("✓ All leap year boundary condition tests passed\n")
    teardown_test()


def test_trip_classification_boundary_conditions():
    """Test trip classification boundary conditions, especially 14-day threshold."""
    print("=== Testing Trip Classification Boundary Conditions ===")
    
    setup_test()
    config = MockAppConfig(2023, 2024, "01-01-2023")
    timeline = DateTimeline.from_config(config)
    first_entry = date(2023, 1, 1)
    
    # Test 1-day trip (shortest possible)
    single_day = Day(date(2023, 5, 15))
    single_day.classification = DayClassification.SHORT_TRIP
    
    assert single_day.counts_as_short_trip_day(first_entry) == True, "1-day trip should be SHORT_TRIP"
    assert single_day.counts_as_long_trip_day(first_entry) == False, "1-day trip should not be LONG_TRIP"
    assert single_day.counts_as_ilr_total_day(first_entry) == True, "1-day trip should count toward ILR total"
    print("✓ 1-day trip classified correctly as SHORT_TRIP")
    
    # Test 13-day trip (just under threshold)
    trip_13_days = []
    start_date = date(2023, 6, 1)
    for i in range(13):
        day = Day(start_date + timedelta(days=i))
        day.classification = DayClassification.SHORT_TRIP
        trip_13_days.append(day)
    
    for day in trip_13_days:
        assert day.counts_as_short_trip_day(first_entry) == True, "13-day trip days should be SHORT_TRIP"
        assert day.counts_as_long_trip_day(first_entry) == False, "13-day trip days should not be LONG_TRIP"
        assert day.counts_as_ilr_total_day(first_entry) == True, "13-day trip days should count toward ILR total"
    print("✓ 13-day trip classified correctly as SHORT_TRIP")
    
    # Test exactly 14-day trip (boundary condition)
    trip_14_days = []
    start_date = date(2023, 7, 1)
    for i in range(14):
        day = Day(start_date + timedelta(days=i))
        day.classification = DayClassification.LONG_TRIP
        trip_14_days.append(day)
    
    for day in trip_14_days:
        assert day.counts_as_short_trip_day(first_entry) == False, "14-day trip days should not be SHORT_TRIP"
        assert day.counts_as_long_trip_day(first_entry) == True, "14-day trip days should be LONG_TRIP"
        assert day.counts_as_ilr_total_day(first_entry) == False, "14-day trip days should NOT count toward ILR total"
    print("✓ 14-day trip (boundary) classified correctly as LONG_TRIP")
    
    # Test 15-day trip (over threshold)
    trip_15_days = []
    start_date = date(2023, 8, 1)
    for i in range(15):
        day = Day(start_date + timedelta(days=i))
        day.classification = DayClassification.LONG_TRIP
        trip_15_days.append(day)
    
    for day in trip_15_days:
        assert day.counts_as_short_trip_day(first_entry) == False, "15-day trip days should not be SHORT_TRIP"
        assert day.counts_as_long_trip_day(first_entry) == True, "15-day trip days should be LONG_TRIP"
        assert day.counts_as_ilr_total_day(first_entry) == False, "15-day trip days should NOT count toward ILR total"
    print("✓ 15-day trip classified correctly as LONG_TRIP")
    
    # Test trip spanning months (edge case)
    timeline.update_date_range_classification(
        date(2023, 9, 25), date(2023, 10, 5), DayClassification.SHORT_TRIP  # 11-day trip spanning months
    )
    
    sep_days = timeline.get_days_in_month(2023, 9)
    oct_days = timeline.get_days_in_month(2023, 10)
    
    # Check September days (25-30)
    trip_days_sep = [day for day in sep_days if day.classification == DayClassification.SHORT_TRIP]
    assert len(trip_days_sep) == 6, f"Expected 6 trip days in September, got {len(trip_days_sep)}"
    
    # Check October days (1-5) 
    trip_days_oct = [day for day in oct_days if day.classification == DayClassification.SHORT_TRIP]
    assert len(trip_days_oct) == 5, f"Expected 5 trip days in October, got {len(trip_days_oct)}"
    
    print("✓ Trip spanning months classified correctly")
    
    # Test trip spanning years
    timeline.update_date_range_classification(
        date(2023, 12, 28), date(2024, 1, 3), DayClassification.SHORT_TRIP  # 7-day trip spanning years
    )
    
    dec_days = timeline.get_days_in_year(2023)
    jan_days = timeline.get_days_in_month(2024, 1)
    
    # Check December days (28-31)
    trip_days_dec = [day for day in dec_days if day.date >= date(2023, 12, 28) and day.classification == DayClassification.SHORT_TRIP]
    assert len(trip_days_dec) == 4, f"Expected 4 trip days in December, got {len(trip_days_dec)}"
    
    # Check January days (1-3)
    trip_days_jan = [day for day in jan_days if day.date <= date(2024, 1, 3) and day.classification == DayClassification.SHORT_TRIP]
    assert len(trip_days_jan) == 3, f"Expected 3 trip days in January, got {len(trip_days_jan)}"
    
    print("✓ Trip spanning years classified correctly")
    
    print("✓ All trip classification boundary condition tests passed\n")
    teardown_test()


def test_error_conditions():
    """Test error conditions and edge cases."""
    print("=== Testing Error Conditions ===")
    
    # Test DateTimeline with invalid config
    try:
        invalid_config = MockAppConfig()
        # Remove required attributes
        delattr(invalid_config, 'start_year')
        timeline = DateTimeline.from_config(invalid_config)
        assert False, "Should raise AttributeError with missing config attributes"
    except AttributeError as e:
        assert "start_year" in str(e), f"Expected error about start_year, got: {e}"
        print("✓ DateTimeline correctly handles missing config attributes")
    
    # Test update_day_classification with invalid date
    DateTimeline.reset_singleton()
    config = MockAppConfig(2023, 2024, "01-01-2023")
    timeline = DateTimeline.from_config(config)
    
    invalid_date = date(2025, 1, 1)  # Outside range
    success = timeline.update_day_classification(invalid_date, DayClassification.UK_RESIDENCE)
    assert success == False, "Should return False for date outside range"
    print("✓ update_day_classification handles invalid dates correctly")
    
    # Test get_days_in_month with invalid month
    days = timeline.get_days_in_month(2025, 1)  # Year outside range
    assert len(days) == 0, "Should return empty list for year outside range"
    print("✓ get_days_in_month handles invalid year correctly")
    
    print("✓ All error condition tests passed\n")


def run_all_tests():
    """Run all test functions."""
    print("Starting comprehensive test suite for dates.py")
    print("=" * 60)
    
    test_functions = [
        test_day_classification_enum,
        test_day_basic_functionality,
        test_day_ilr_counting_methods,
        test_date_timeline_creation,
        test_date_timeline_basic_methods,
        test_date_timeline_month_year_methods,
        test_date_timeline_classification_methods,
        test_date_timeline_ilr_methods,
        test_date_timeline_auto_classification,
        test_date_timeline_summary_methods,
        test_leap_year_boundary_conditions,
        test_trip_classification_boundary_conditions,
        test_error_conditions
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for test_func in test_functions:
        try:
            test_func()
            passed_tests += 1
        except Exception as e:
            print(f"❌ {test_func.__name__} FAILED: {e}")
            failed_tests += 1
    
    print("=" * 60)
    print(f"Test Results: {passed_tests} passed, {failed_tests} failed")
    
    if failed_tests == 0:
        print("🎉 ALL TESTS PASSED! dates.py is working correctly.")
    else:
        print("❌ Some tests failed. Please check the implementation.")
    
    return failed_tests == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)