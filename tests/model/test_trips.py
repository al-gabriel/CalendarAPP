"""
Comprehensive Test Suite for trips.py
Tests all functionality of TripClassifier class with real and mock JSON data.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.model.trips import TripClassifier
from calendar_app.config import AppConfig


class MockAppConfig:
    """Mock AppConfig for testing."""
    def __init__(self, start_year: int, end_year: int, first_entry_date: str):
        self.start_year = start_year
        self.end_year = end_year
        self.first_entry_date = first_entry_date
        # Parse first_entry_date string to date object
        day, month, year = first_entry_date.split('-')
        self.first_entry_date_obj = date(int(year), int(month), int(day))


def create_test_trip_data() -> List[Dict]:
    """Create test trip data with various scenarios."""
    return [
        {
            "id": "short_trip_1",
            "departure_date": "10-06-2023",
            "return_date": "20-06-2023", 
            "departure_date_obj": date(2023, 6, 10),
            "return_date_obj": date(2023, 6, 20),
            "trip_length_days": 11,
            "is_short_trip": True,
            "from_airport": "LHR",
            "to_airport": "LIS",
            "notes": "Summer holiday - short trip"
        },
        {
            "id": "long_trip_1", 
            "departure_date": "01-12-2024",
            "return_date": "15-01-2025",
            "departure_date_obj": date(2024, 12, 1),
            "return_date_obj": date(2025, 1, 15),
            "trip_length_days": 46,
            "is_short_trip": False,
            "from_airport": "LHR",
            "to_airport": "OPO", 
            "notes": "Christmas holidays - long trip"
        },
        {
            "id": "short_trip_2",
            "departure_date": "15-03-2024",
            "return_date": "22-03-2024",
            "departure_date_obj": date(2024, 3, 15),
            "return_date_obj": date(2024, 3, 22),
            "trip_length_days": 8,
            "is_short_trip": True,
            "from_airport": "LGW",
            "to_airport": "BCN",
            "notes": "Short business trip"
        }
    ]


def test_trip_classifier_initialization():
    """Test TripClassifier initialization and trip day map building."""
    print("=== Testing TripClassifier Initialization ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    
    # Test successful initialization
    classifier = TripClassifier(config, trips_data)
    assert classifier.config == config
    assert classifier.trips_data == trips_data
    assert hasattr(classifier, '_trip_day_map')
    print("✓ TripClassifier initialization successful")
    
    # Test trip day map contains expected entries
    # Short trip 1: 11 days (10-06-2023 to 20-06-2023)
    short_trip_start = date(2023, 6, 10)
    short_trip_end = date(2023, 6, 20)
    
    current_date = short_trip_start
    while current_date <= short_trip_end:
        assert current_date in classifier._trip_day_map
        trip_info = classifier._trip_day_map[current_date]
        assert trip_info["id"] == "short_trip_1"
        assert trip_info["is_short_trip"] == True
        current_date += timedelta(days=1)
    
    print("✓ Trip day map correctly built for short trip")
    
    # Test non-trip days are not in map
    non_trip_date = date(2023, 5, 15)
    assert non_trip_date not in classifier._trip_day_map
    print("✓ Non-trip days correctly excluded from map")
    

def test_overlapping_trips_error():
    """Test that overlapping trips raise appropriate error."""
    print("=== Testing Overlapping Trips Error Handling ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    
    # Create overlapping trips data
    overlapping_trips = [
        {
            "id": "trip_1",
            "departure_date": "10-06-2023",
            "return_date": "20-06-2023",
            "departure_date_obj": date(2023, 6, 10),
            "return_date_obj": date(2023, 6, 20),
            "trip_length_days": 11,
            "is_short_trip": True
        },
        {
            "id": "trip_2", 
            "departure_date": "15-06-2023",  # Overlaps with trip_1
            "return_date": "25-06-2023",
            "departure_date_obj": date(2023, 6, 15),
            "return_date_obj": date(2023, 6, 25),
            "trip_length_days": 11,
            "is_short_trip": True
        }
    ]
    
    try:
        classifier = TripClassifier(config, overlapping_trips)
        assert False, "Should have raised ValueError for overlapping trips"
    except ValueError as e:
        assert "appears in multiple trips" in str(e)
        assert "trip_1" in str(e) and "trip_2" in str(e)
        print("✓ Overlapping trips correctly raise ValueError")


def test_get_day_trip_info():
    """Test getting trip information for specific dates."""
    print("=== Testing get_day_trip_info Method ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023") 
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    # Test trip day
    trip_date = date(2023, 6, 15)  # Middle of short_trip_1
    trip_info = classifier.get_day_trip_info(trip_date)
    assert trip_info is not None
    assert trip_info["id"] == "short_trip_1"
    assert trip_info["is_short_trip"] == True
    print("✓ Trip day correctly returns trip information")
    
    # Test non-trip day
    non_trip_date = date(2023, 5, 15)
    trip_info = classifier.get_day_trip_info(non_trip_date)
    assert trip_info is None
    print("✓ Non-trip day correctly returns None")
    
    # Test trip boundary dates
    departure_date = date(2023, 6, 10)
    return_date = date(2023, 6, 20)
    
    departure_info = classifier.get_day_trip_info(departure_date)
    return_info = classifier.get_day_trip_info(return_date)
    
    assert departure_info is not None and departure_info["id"] == "short_trip_1"
    assert return_info is not None and return_info["id"] == "short_trip_1"
    print("✓ Trip boundary dates correctly included")


def test_trip_classification_methods():
    """Test is_trip_day, is_short_trip_day, is_long_trip_day methods."""
    print("=== Testing Trip Classification Methods ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    # Test short trip day
    short_trip_date = date(2023, 6, 15)  # Middle of short_trip_1
    assert classifier.is_trip_day(short_trip_date) == True
    assert classifier.is_short_trip_day(short_trip_date) == True
    assert classifier.is_long_trip_day(short_trip_date) == False
    print("✓ Short trip day classification correct")
    
    # Test long trip day
    long_trip_date = date(2025, 1, 10)  # Middle of long_trip_1
    assert classifier.is_trip_day(long_trip_date) == True
    assert classifier.is_short_trip_day(long_trip_date) == False
    assert classifier.is_long_trip_day(long_trip_date) == True
    print("✓ Long trip day classification correct")
    
    # Test non-trip day
    non_trip_date = date(2023, 5, 15)
    assert classifier.is_trip_day(non_trip_date) == False
    assert classifier.is_short_trip_day(non_trip_date) == False
    assert classifier.is_long_trip_day(non_trip_date) == False
    print("✓ Non-trip day classification correct")


def test_get_trip_summary():
    """Test comprehensive trip summary generation."""
    print("=== Testing get_trip_summary Method ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    # Test short trip summary
    short_trip_date = date(2023, 6, 15)
    summary = classifier.get_trip_summary(short_trip_date)
    
    expected_short_summary = {
        'classification': 'SHORT_TRIP',
        'is_trip_day': True,
        'trip_id': 'short_trip_1',
        'trip_type': 'short',
        'departure_date': date(2023, 6, 10),
        'return_date': date(2023, 6, 20),
        'trip_length_days': 11,
        'from_airport': 'LHR',
        'to_airport': 'LIS'
    }
    
    for key, expected_value in expected_short_summary.items():
        assert summary[key] == expected_value, f"Expected {key}={expected_value}, got {summary[key]}"
    print("✓ Short trip summary correct")
    
    # Test long trip summary
    long_trip_date = date(2025, 1, 10)
    summary = classifier.get_trip_summary(long_trip_date)
    
    expected_long_summary = {
        'classification': 'LONG_TRIP',
        'is_trip_day': True,
        'trip_id': 'long_trip_1',
        'trip_type': 'long',
        'departure_date': date(2024, 12, 1),
        'return_date': date(2025, 1, 15),
        'trip_length_days': 46,
        'from_airport': 'LHR',
        'to_airport': 'OPO'
    }
    
    for key, expected_value in expected_long_summary.items():
        assert summary[key] == expected_value, f"Expected {key}={expected_value}, got {summary[key]}"
    print("✓ Long trip summary correct")
    
    # Test UK residence day summary
    non_trip_date = date(2023, 5, 15)
    summary = classifier.get_trip_summary(non_trip_date)
    
    expected_uk_summary = {
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
    
    for key, expected_value in expected_uk_summary.items():
        assert summary[key] == expected_value, f"Expected {key}={expected_value}, got {summary[key]}"
    print("✓ UK residence day summary correct")


def test_get_all_trips():
    """Test retrieving all loaded trip data."""
    print("=== Testing get_all_trips Method ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    all_trips = classifier.get_all_trips()
    assert len(all_trips) == 3
    assert all_trips == trips_data
    
    # Verify trip IDs are present
    trip_ids = {trip["id"] for trip in all_trips}
    expected_ids = {"short_trip_1", "long_trip_1", "short_trip_2"}
    assert trip_ids == expected_ids
    print("✓ get_all_trips returns correct data")


def test_get_trips_in_date_range():
    """Test retrieving trips within specific date ranges."""
    print("=== Testing get_trips_in_date_range Method ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    # Test range that includes short_trip_1 only
    range_start = date(2023, 6, 1)
    range_end = date(2023, 6, 30)
    trips_in_range = classifier.get_trips_in_date_range(range_start, range_end)
    
    assert len(trips_in_range) == 1
    assert trips_in_range[0]["id"] == "short_trip_1"
    print("✓ Date range correctly filters trips (June 2023)")
    
    # Test range that includes multiple trips
    range_start = date(2024, 1, 1)
    range_end = date(2025, 12, 31) 
    trips_in_range = classifier.get_trips_in_date_range(range_start, range_end)
    
    assert len(trips_in_range) == 2
    trip_ids = {trip["id"] for trip in trips_in_range}
    expected_ids = {"long_trip_1", "short_trip_2"}
    assert trip_ids == expected_ids
    print("✓ Date range correctly includes multiple trips (2024-2025)")
    
    # Test range with no trips
    range_start = date(2023, 1, 1)
    range_end = date(2023, 5, 31)
    trips_in_range = classifier.get_trips_in_date_range(range_start, range_end)
    
    assert len(trips_in_range) == 0
    print("✓ Date range with no trips returns empty list")
    
    # Test partial overlap
    range_start = date(2023, 6, 15)  # Overlaps with middle of short_trip_1
    range_end = date(2023, 6, 25)
    trips_in_range = classifier.get_trips_in_date_range(range_start, range_end)
    
    assert len(trips_in_range) == 1
    assert trips_in_range[0]["id"] == "short_trip_1"
    print("✓ Partial date range overlap correctly detected")


def test_validate_trip_data():
    """Test trip data validation."""
    print("=== Testing validate_trip_data Method ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    trips_data = create_test_trip_data()
    classifier = TripClassifier(config, trips_data)
    
    # Test valid trip data
    is_valid, errors = classifier.validate_trip_data()
    assert is_valid == True
    assert len(errors) == 0
    print("✓ Valid trip data passes validation")
    
    # Test trip before first entry date
    config_late_entry = MockAppConfig(2023, 2025, "01-07-2023")  # After short_trip_1
    invalid_trips = create_test_trip_data()
    
    classifier_invalid = TripClassifier(config_late_entry, invalid_trips)
    is_valid, errors = classifier_invalid.validate_trip_data()
    
    assert is_valid == False
    assert len(errors) > 0
    assert "starts before first entry date" in errors[0]
    print("✓ Trip before first entry date correctly flagged as invalid")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("=== Testing Edge Cases ===")
    
    config = MockAppConfig(2023, 2025, "01-01-2023")
    
    # Test with empty trips data
    empty_classifier = TripClassifier(config, [])
    assert empty_classifier.is_trip_day(date(2023, 6, 15)) == False
    assert empty_classifier.get_day_trip_info(date(2023, 6, 15)) is None
    print("✓ Empty trips data handled correctly")
    
    # Test single day trip
    single_day_trip = [{
        "id": "single_day",
        "departure_date": "15-06-2023",
        "return_date": "15-06-2023",
        "departure_date_obj": date(2023, 6, 15),
        "return_date_obj": date(2023, 6, 15),
        "trip_length_days": 1,
        "is_short_trip": True
    }]
    
    single_day_classifier = TripClassifier(config, single_day_trip)
    assert single_day_classifier.is_trip_day(date(2023, 6, 15)) == True
    assert single_day_classifier.is_trip_day(date(2023, 6, 14)) == False
    assert single_day_classifier.is_trip_day(date(2023, 6, 16)) == False
    print("✓ Single day trip handled correctly")
    
    # Test trip on year boundary
    year_boundary_trip = [{
        "id": "year_boundary",
        "departure_date": "30-12-2023",
        "return_date": "02-01-2024",
        "departure_date_obj": date(2023, 12, 30),
        "return_date_obj": date(2024, 1, 2),
        "trip_length_days": 4,
        "is_short_trip": True
    }]
    
    boundary_classifier = TripClassifier(config, year_boundary_trip)
    assert boundary_classifier.is_trip_day(date(2023, 12, 31)) == True
    assert boundary_classifier.is_trip_day(date(2024, 1, 1)) == True
    print("✓ Year boundary trip handled correctly")


def run_all_trips_tests():
    """Run all TripClassifier tests."""
    print("Starting TripClassifier Test Suite...")
    print("=" * 50)
    
    try:
        test_trip_classifier_initialization()
        print()
        
        test_overlapping_trips_error()
        print()
        
        test_get_day_trip_info()
        print()
        
        test_trip_classification_methods()
        print()
        
        test_get_trip_summary()
        print()
        
        test_get_all_trips()
        print()
        
        test_get_trips_in_date_range()
        print()
        
        test_validate_trip_data()
        print()
        
        test_edge_cases()
        print()
        
        print("=" * 50)
        print("✅ ALL TRIPCLASSIFIER TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_trips_tests()