"""
Comprehensive Test Suite for day.py
Tests all functionality of Day class and DayClassification enum.
"""

import sys
from pathlib import Path
from datetime import date, timedelta

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent.parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.model.day import Day, DayClassification


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
    assert day.visaPeriod_info is None, f"Expected None visaPeriod_info, got {day.visaPeriod_info}"
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
    """Test Day ILR counting methods with different classifications."""
    print("=== Testing Day ILR Counting Methods ===")
    
    # Set up test data
    first_entry_date = date(2023, 3, 29)  # 29-03-2023
    
    # Test dates
    pre_entry_date = date(2023, 1, 15)     # Before first entry
    uk_residence_date = date(2023, 4, 15)  # After first entry, UK residence
    short_trip_date = date(2023, 5, 15)    # After first entry, short trip
    long_trip_date = date(2023, 6, 15)     # After first entry, long trip
    
    # Create Day objects
    pre_entry_day = Day(pre_entry_date)
    pre_entry_day.classification = DayClassification.PRE_ENTRY
    
    uk_residence_day = Day(uk_residence_date)
    uk_residence_day.classification = DayClassification.UK_RESIDENCE
    
    short_trip_day = Day(short_trip_date)
    short_trip_day.classification = DayClassification.SHORT_TRIP
    
    long_trip_day = Day(long_trip_date)
    long_trip_day.classification = DayClassification.LONG_TRIP
    
    # Test counts_as_ilr_in_uk_day
    assert pre_entry_day.counts_as_ilr_in_uk_day(first_entry_date) == False, "Pre-entry day should not count as ILR in-UK"
    assert uk_residence_day.counts_as_ilr_in_uk_day(first_entry_date) == True, "UK residence day should count as ILR in-UK"
    assert short_trip_day.counts_as_ilr_in_uk_day(first_entry_date) == False, "Short trip day should not count as ILR in-UK"
    assert long_trip_day.counts_as_ilr_in_uk_day(first_entry_date) == False, "Long trip day should not count as ILR in-UK"
    print("✓ counts_as_ilr_in_uk_day() correct")
    
    # Test counts_as_short_trip_day
    assert pre_entry_day.counts_as_short_trip_day(first_entry_date) == False, "Pre-entry day should not count as short trip"
    assert uk_residence_day.counts_as_short_trip_day(first_entry_date) == False, "UK residence day should not count as short trip"
    assert short_trip_day.counts_as_short_trip_day(first_entry_date) == True, "Short trip day should count as short trip"
    assert long_trip_day.counts_as_short_trip_day(first_entry_date) == False, "Long trip day should not count as short trip"
    print("✓ counts_as_short_trip_day() correct")
    
    # Test counts_as_ilr_total_day
    assert pre_entry_day.counts_as_ilr_total_day(first_entry_date) == False, "Pre-entry day should not count toward ILR total"
    assert uk_residence_day.counts_as_ilr_total_day(first_entry_date) == True, "UK residence day should count toward ILR total"
    assert short_trip_day.counts_as_ilr_total_day(first_entry_date) == True, "Short trip day should count toward ILR total"
    assert long_trip_day.counts_as_ilr_total_day(first_entry_date) == False, "Long trip day should not count toward ILR total"
    print("✓ counts_as_ilr_total_day() correct")
    
    # Test counts_as_long_trip_day
    assert pre_entry_day.counts_as_long_trip_day(first_entry_date) == False, "Pre-entry day should not count as long trip"
    assert uk_residence_day.counts_as_long_trip_day(first_entry_date) == False, "UK residence day should not count as long trip"
    assert short_trip_day.counts_as_long_trip_day(first_entry_date) == False, "Short trip day should not count as long trip"
    assert long_trip_day.counts_as_long_trip_day(first_entry_date) == True, "Long trip day should count as long trip"
    print("✓ counts_as_long_trip_day() correct")
    
    print("✓ All Day ILR counting methods tests passed\n")


def test_day_boundary_conditions():
    """Test Day class boundary conditions."""
    print("=== Testing Day Class Boundary Conditions ===")
    
    # Test leap year day
    leap_day = Day(date(2024, 2, 29))
    assert leap_day.month == 2, f"Expected month 2 for leap day, got {leap_day.month}"
    assert leap_day.day == 29, f"Expected day 29 for leap day, got {leap_day.day}"
    print("✓ Leap year day handling correct")
    
    # Test year boundary
    new_year_day = Day(date(2024, 1, 1))
    assert new_year_day.year == 2024, f"Expected year 2024, got {new_year_day.year}"
    assert new_year_day.month == 1, f"Expected month 1, got {new_year_day.month}"
    assert new_year_day.day == 1, f"Expected day 1, got {new_year_day.day}"
    print("✓ Year boundary handling correct")
    
    # Test first entry date boundary
    first_entry = date(2023, 3, 29)
    
    # Day before first entry
    before_entry = Day(date(2023, 3, 28))
    before_entry.classification = DayClassification.UK_RESIDENCE
    assert before_entry.counts_as_ilr_total_day(first_entry) == False, "Day before first entry should not count"
    
    # Day on first entry
    on_entry = Day(date(2023, 3, 29))
    on_entry.classification = DayClassification.UK_RESIDENCE
    assert on_entry.counts_as_ilr_total_day(first_entry) == True, "Day on first entry should count"
    
    # Day after first entry
    after_entry = Day(date(2023, 3, 30))
    after_entry.classification = DayClassification.UK_RESIDENCE
    assert after_entry.counts_as_ilr_total_day(first_entry) == True, "Day after first entry should count"
    
    print("✓ First entry date boundary handling correct")
    
    print("✓ All Day boundary condition tests passed\n")


def run_all_day_tests():
    """Run all Day class tests."""
    print("=== Running All Day Class Tests ===\n")
    
    test_day_classification_enum()
    test_day_basic_functionality()
    test_day_ilr_counting_methods()
    test_day_boundary_conditions()
    
    print("=== All Day Class Tests Completed Successfully ===\n")


if __name__ == "__main__":
    run_all_day_tests()