"""
Comprehensive Test Suite for visaPeriods.py
Tests all functionality of VisaClassifier class with real and mock JSON data.
"""

import sys
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List

# Add the src directory to Python path to import our modules
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

from calendar_app.model.visaPeriods import VisaClassifier
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


def create_test_visaPeriod_data() -> List[Dict]:
    """Create test visa period data with various scenarios."""
    return [
        {
            "id": "skilled_worker_1",
            "label": "Skilled Worker Visa 1",
            "start_date": "10-01-2023",
            "end_date": "14-09-2024",
            "start_date_obj": date(2023, 1, 10),
            "end_date_obj": date(2024, 9, 14),
            "gross_salary": "£32400.00"
        },
        {
            "id": "skilled_worker_2",
            "label": "Skilled Worker Visa 2",
            "start_date": "15-09-2024",
            "end_date": "30-09-2027",
            "start_date_obj": date(2024, 9, 15),
            "end_date_obj": date(2027, 9, 30),
            "gross_salary": "£40200.00"
        }
    ]


def test_visaPeriod_classifier_initialization():
    """Test VisaClassifier initialization and visa day map building."""
    print("=== Testing VisaClassifier Initialization ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    
    # Test successful initialization
    classifier = VisaClassifier(config, visaPeriod_data)
    assert classifier.config == config
    assert classifier.visaPeriods_data == visaPeriod_data
    assert hasattr(classifier, '_visaPeriod_day_map')
    print("✓ VisaClassifier initialization successful")
    
    # Test visa day map contains expected entries
    # First period: 10-01-2023 to 14-09-2024
    first_period_start = date(2023, 1, 10)
    first_period_end = date(2024, 9, 14)
    
    # Check some sample dates in the first period
    sample_dates = [
        first_period_start,
        date(2023, 6, 15),  # Middle of first period
        first_period_end
    ]
    
    for sample_date in sample_dates:
        assert sample_date in classifier._visaPeriod_day_map
        visaPeriod_info = classifier._visaPeriod_day_map[sample_date]
        assert visaPeriod_info["id"] == "skilled_worker_1"
        assert visaPeriod_info["gross_salary"] == "£32400.00"
    
    print("✓ Visa day map correctly built for first period")
    
    # Test second period dates
    second_period_start = date(2024, 9, 15)
    assert second_period_start in classifier._visaPeriod_day_map
    visaPeriod_info = classifier._visaPeriod_day_map[second_period_start]
    assert visaPeriod_info["id"] == "skilled_worker_2"
    assert visaPeriod_info["gross_salary"] == "£40200.00"
    print("✓ Visa day map correctly built for second period")


def test_overlapping_visaPeriods_error():
    """Test that overlapping visa periods raise appropriate error."""
    print("=== Testing Overlapping Visa Periods Error Handling ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    
    # Create overlapping visa periods
    overlapping_periods = [
        {
            "id": "visa_1",
            "label": "First Visa",
            "start_date": "10-01-2023",
            "end_date": "31-12-2023",
            "start_date_obj": date(2023, 1, 10),
            "end_date_obj": date(2023, 12, 31),
            "gross_salary": "£30000.00"
        },
        {
            "id": "visa_2",
            "label": "Second Visa",
            "start_date": "01-12-2023",  # Overlaps with visa_1
            "end_date": "31-12-2024",
            "start_date_obj": date(2023, 12, 1),
            "end_date_obj": date(2024, 12, 31),
            "gross_salary": "£35000.00"
        }
    ]
    
    try:
        classifier = VisaClassifier(config, overlapping_periods)
        assert False, "Should have raised ValueError for overlapping visa periods"
    except ValueError as e:
        assert "overlaps with" in str(e)
        assert "visa_1" in str(e) and "visa_2" in str(e)
        print("✓ Overlapping visa periods correctly raise ValueError")


def test_gap_in_visaPeriods_error():
    """Test that gaps in visa periods raise appropriate error."""
    print("=== Testing Visa Period Gaps Error Handling ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    
    # Create visa periods with a gap
    periods_with_gap = [
        {
            "id": "visa_1",
            "label": "First Visa", 
            "start_date": "10-01-2023",
            "end_date": "31-08-2024",
            "start_date_obj": date(2023, 1, 10),
            "end_date_obj": date(2024, 8, 31),
            "gross_salary": "£30000.00"
        },
        {
            "id": "visa_2",
            "label": "Second Visa",
            "start_date": "15-10-2024",  # Gap between 31-08-2024 and 15-10-2024
            "end_date": "31-12-2025",
            "start_date_obj": date(2024, 10, 15),
            "end_date_obj": date(2025, 12, 31),
            "gross_salary": "£35000.00"
        }
    ]
    
    try:
        classifier = VisaClassifier(config, periods_with_gap)
        assert False, "Should have raised ValueError for gap in visa periods"
    except ValueError as e:
        assert "Gap found between visa periods" in str(e)
        print("✓ Gap in visa periods correctly raises ValueError")


def test_get_day_visaPeriod_info():
    """Test getting visa period information for specific dates."""
    print("=== Testing get_day_visaPeriod_info Method ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    # Test first period day
    first_period_date = date(2023, 6, 15)
    visaPeriod_info = classifier.get_day_visaPeriod_info(first_period_date)
    assert visaPeriod_info is not None
    assert visaPeriod_info["id"] == "skilled_worker_1"
    assert visaPeriod_info["gross_salary"] == "£32400.00"
    print("✓ First period day correctly returns visa information")
    
    # Test second period day
    second_period_date = date(2024, 12, 15)
    visaPeriod_info = classifier.get_day_visaPeriod_info(second_period_date)
    assert visaPeriod_info is not None
    assert visaPeriod_info["id"] == "skilled_worker_2"
    assert visaPeriod_info["gross_salary"] == "£40200.00"
    print("✓ Second period day correctly returns visa information")
    
    # Test date outside timeline (should return None if not mapped)
    outside_date = date(2022, 1, 1)
    visaPeriod_info = classifier.get_day_visaPeriod_info(outside_date)
    assert visaPeriod_info is None
    print("✓ Date outside timeline correctly returns None")


def test_visaPeriod_helper_methods():
    """Test helper methods for visa period information."""
    print("=== Testing Visa Period Helper Methods ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    test_date = date(2023, 6, 15)  # In first period
    
    # Test is_visaPeriod_day
    assert classifier.is_visaPeriod_day(test_date) == True
    assert classifier.is_visaPeriod_day(date(2022, 1, 1)) == False
    print("✓ is_visaPeriod_day works correctly")
    
    # Test get_visaPeriod_label
    label = classifier.get_visaPeriod_label(test_date)
    assert label == "Skilled Worker Visa 1"
    assert classifier.get_visaPeriod_label(date(2022, 1, 1)) is None
    print("✓ get_visaPeriod_label works correctly")
    
    # Test get_visaPeriod_id
    visaPeriod_id = classifier.get_visaPeriod_id(test_date)
    assert visaPeriod_id == "skilled_worker_1"
    assert classifier.get_visaPeriod_id(date(2022, 1, 1)) is None
    print("✓ get_visaPeriod_id works correctly")
    
    # Test get_visaPeriod_salary
    salary = classifier.get_visaPeriod_salary(test_date)
    assert salary == "£32400.00"
    assert classifier.get_visaPeriod_salary(date(2022, 1, 1)) is None
    print("✓ get_visaPeriod_salary works correctly")

def test_get_visaPeriod_summary():
    """Test comprehensive visa summary generation."""
    print("=== Testing get_visaPeriod_summary Method ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    # Test visa period day summary
    test_date = date(2023, 1, 15)  # 6th day of first period (starts Jan 10)
    summary = classifier.get_visaPeriod_summary(test_date)
    
    expected_summary = {
        'has_visaPeriod': True,
        'visaPeriod_id': 'skilled_worker_1',
        'visaPeriod_label': 'Skilled Worker Visa 1',
        'start_date': date(2023, 1, 10),
        'end_date': date(2024, 9, 14),
        'gross_salary': '£32400.00',
        'day_number_in_period': 6  # 6th day since Jan 10
    }
    
    for key, expected_value in expected_summary.items():
        if key != 'days_in_period':  # Skip this as it's calculated
            assert summary[key] == expected_value, f"Expected {key}={expected_value}, got {summary[key]}"
    
    assert summary['days_in_period'] > 0  # Should be positive number
    print("✓ Visa period day summary correct")
    
    # Test non-visa-period day summary
    non_visaPeriod_date = date(2022, 1, 1)
    summary = classifier.get_visaPeriod_summary(non_visaPeriod_date)
    
    expected_non_visaPeriod_summary = {
        'has_visaPeriod': False,
        'visaPeriod_id': None,
        'visaPeriod_label': None,
        'start_date': None,
        'end_date': None,
        'gross_salary': None,
        'days_in_period': None,
        'day_number_in_period': None
    }
    
    for key, expected_value in expected_non_visaPeriod_summary.items():
        assert summary[key] == expected_value, f"Expected {key}={expected_value}, got {summary[key]}"
    print("✓ Non-visa period day summary correct")


def test_get_visaPeriods_in_date_range():
    """Test retrieving visa periods within specific date ranges."""
    print("=== Testing get_visaPeriods_in_date_range Method ===")
    
    config = MockAppConfig(2023, 2027, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    # Test range that includes only first period
    range_start = date(2023, 1, 1)
    range_end = date(2023, 12, 31)
    periods_in_range = classifier.get_visaPeriods_in_date_range(range_start, range_end)
    
    assert len(periods_in_range) == 1
    assert periods_in_range[0]["id"] == "skilled_worker_1"
    print("✓ Date range correctly filters first period (2023)")
    
    # Test range that includes both periods
    range_start = date(2024, 1, 1)
    range_end = date(2025, 12, 31)
    periods_in_range = classifier.get_visaPeriods_in_date_range(range_start, range_end)
    
    assert len(periods_in_range) == 2
    period_ids = {period["id"] for period in periods_in_range}
    expected_ids = {"skilled_worker_1", "skilled_worker_2"}
    assert period_ids == expected_ids
    print("✓ Date range correctly includes both periods (2024-2025)")
    
    # Test range with no periods
    range_start = date(2028, 1, 1)
    range_end = date(2029, 12, 31)
    periods_in_range = classifier.get_visaPeriods_in_date_range(range_start, range_end)
    
    assert len(periods_in_range) == 0
    print("✓ Date range with no periods returns empty list")


def test_get_visaPeriod_transitions():
    """Test visa period transition analysis."""
    print("=== Testing get_visaPeriod_transitions Method ===")
    
    config = MockAppConfig(2023, 2027, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    transitions = classifier.get_visaPeriod_transitions()
    
    # Should have one transition between the two periods
    assert len(transitions) == 1
    
    transition = transitions[0]
    expected_transition = {
        'from_visaPeriod_id': 'skilled_worker_1',
        'from_visaPeriod_label': 'Skilled Worker Visa 1',
        'from_end_date': date(2024, 9, 14),
        'from_salary': '£32400.00',
        'to_visaPeriod_id': 'skilled_worker_2',
        'to_visaPeriod_label': 'Skilled Worker Visa 2',
        'to_start_date': date(2024, 9, 15),
        'to_salary': '£40200.00',
        'transition_date': date(2024, 9, 15),
        'is_salary_increase': True
    }
    
    for key, expected_value in expected_transition.items():
        assert transition[key] == expected_value, f"Expected {key}={expected_value}, got {transition[key]}"
    
    print("✓ Visa transition information correct")
    
    # Test with single period (no transitions)
    single_period_data = [visaPeriod_data[0]]
    single_classifier = VisaClassifier(config, single_period_data)
    single_transitions = single_classifier.get_visaPeriod_transitions()
    
    assert len(single_transitions) == 0
    print("✓ Single period correctly returns no transitions")


def test_salary_comparison():
    """Test salary comparison functionality."""
    print("=== Testing Salary Comparison ===")
    
    config = MockAppConfig(2023, 2027, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    # Test salary increase detection
    assert classifier._is_salary_increase("£30000.00", "£35000.00") == True
    assert classifier._is_salary_increase("£35000.00", "£30000.00") == False
    assert classifier._is_salary_increase("£30000.00", "£30000.00") == False
    print("✓ Salary increase detection works correctly")
    
    # Test invalid salary formats
    assert classifier._is_salary_increase("invalid", "£30000.00") == None
    assert classifier._is_salary_increase("£30000.00", "invalid") == None
    print("✓ Invalid salary formats handled gracefully")


def test_validate_visaPeriods():
    """Test visa period data validation."""
    print("=== Testing validate_visaPeriods Method ===")
    
    config = MockAppConfig(2023, 2027, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    # Test valid visa data
    is_valid, errors = classifier.validate_visaPeriods()
    assert is_valid == True
    assert len(errors) == 0
    print("✓ Valid visa data passes validation")
    
    # Test period ending before first entry date
    early_config = MockAppConfig(2023, 2027, "01-01-2025")  # After first period ends
    early_classifier = VisaClassifier(early_config, visaPeriod_data)
    is_valid, errors = early_classifier.validate_visaPeriods()
    
    assert is_valid == False
    assert len(errors) > 0
    assert "ends before first entry date" in errors[0]
    print("✓ Period ending before first entry date correctly flagged")


def test_timeline_coverage_summary():
    """Test timeline coverage analysis."""
    print("=== Testing get_timeline_coverage_summary Method ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    visaPeriod_data = create_test_visaPeriod_data()
    classifier = VisaClassifier(config, visaPeriod_data)
    
    coverage = classifier.get_timeline_coverage_summary()
    
    # Verify basic structure
    required_keys = [
        'timeline_start', 'timeline_end', 'total_timeline_days',
        'covered_days', 'uncovered_days', 'coverage_percentage',
        'total_visaPeriods', 'uncovered_date_ranges'
    ]
    
    for key in required_keys:
        assert key in coverage, f"Missing key: {key}"
    
    # Verify logical consistency
    assert coverage['total_timeline_days'] > 0
    assert coverage['covered_days'] >= 0
    assert coverage['uncovered_days'] >= 0
    assert coverage['covered_days'] + coverage['uncovered_days'] == coverage['total_timeline_days']
    assert 0 <= coverage['coverage_percentage'] <= 100
    assert coverage['total_visaPeriods'] == 2
    
    print("✓ Timeline coverage summary structure correct")
    print(f"  Coverage: {coverage['coverage_percentage']}% ({coverage['covered_days']}/{coverage['total_timeline_days']} days)")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    print("=== Testing Edge Cases ===")
    
    config = MockAppConfig(2023, 2025, "10-01-2023")
    
    # Test with empty visa data
    empty_classifier = VisaClassifier(config, [])
    assert empty_classifier.is_visaPeriod_day(date(2023, 6, 15)) == False
    assert empty_classifier.get_day_visaPeriod_info(date(2023, 6, 15)) is None
    print("✓ Empty visa data handled correctly")
    
    # Test single day visa period
    single_day_period = [{
        "id": "single_day_visa",
        "label": "Single Day Visa",
        "start_date": "15-06-2023",
        "end_date": "15-06-2023",
        "start_date_obj": date(2023, 6, 15),
        "end_date_obj": date(2023, 6, 15),
        "gross_salary": "£25000.00"
    }]
    
    single_day_classifier = VisaClassifier(config, single_day_period)
    assert single_day_classifier.is_visaPeriod_day(date(2023, 6, 15)) == True
    assert single_day_classifier.is_visaPeriod_day(date(2023, 6, 14)) == False
    assert single_day_classifier.is_visaPeriod_day(date(2023, 6, 16)) == False
    print("✓ Single day visa period handled correctly")
    
    # Test year boundary visa period
    year_boundary_period = [{
        "id": "year_boundary",
        "label": "Year Boundary Visa",
        "start_date": "30-12-2023",
        "end_date": "02-01-2024",
        "start_date_obj": date(2023, 12, 30),
        "end_date_obj": date(2024, 1, 2),
        "gross_salary": "£30000.00"
    }]
    
    boundary_classifier = VisaClassifier(config, year_boundary_period)
    assert boundary_classifier.is_visaPeriod_day(date(2023, 12, 31)) == True
    assert boundary_classifier.is_visaPeriod_day(date(2024, 1, 1)) == True
    print("✓ Year boundary visa period handled correctly")


def run_all_visaPeriod_tests():
    """Run all VisaClassifier tests."""
    print("Starting VisaClassifier Test Suite...")
    print("=" * 50)
    
    try:
        test_visaPeriod_classifier_initialization()
        print()
        
        test_overlapping_visaPeriods_error()
        print()
        
        test_gap_in_visaPeriods_error()
        print()
        
        test_get_day_visaPeriod_info()
        print()
        
        test_visaPeriod_helper_methods()
        print()
        
        test_get_visaPeriod_summary()
        print()
        
        test_get_visaPeriods_in_date_range()
        print()
        
        test_get_visaPeriod_transitions()
        print()
        
        test_salary_comparison()
        print()
        
        test_validate_visaPeriods()
        print()
        
        test_timeline_coverage_summary()
        print()
        
        test_edge_cases()
        print()
        
        print("=" * 50)
        print("✅ ALL VISA CLASSIFIER TESTS PASSED!")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_visaPeriod_tests()