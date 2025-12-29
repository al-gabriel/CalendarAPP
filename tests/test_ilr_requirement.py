#!/usr/bin/env python3
"""
Quick test for ILR requirement calculation with leap years.
"""

import sys
import os
from datetime import date
from pathlib import Path

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calendar_app.config import AppConfig
from calendar_app.model.timeline import DateTimeline
from calendar_app.model.trips import TripClassifier
from calendar_app.model.visaPeriods import VisaClassifier
from calendar_app.model.ilr_statistics import ILRStatisticsEngine

def test_ilr_requirement_calculation():
    """Test the ILR requirement calculation with different scenarios."""
    print("=== Testing ILR Requirement Calculation ===")
    
    # Get project root path
    project_root = Path(__file__).parent.parent
    
    # Test with a first entry date that spans a leap year
    config = AppConfig(project_root)
    config.start_year = 2020
    config.end_year = 2030
    config.first_entry_date = "01-03-2020"  # March 1, 2020 (2020 is leap year)
    config.objective_years = 5
    
    # Initialize required components
    trip_classifier = TripClassifier(config, [])  # Empty trips data for testing
    visa_classifier = VisaClassifier(config, [])  # Empty visa data for testing
    timeline = DateTimeline.from_config(config, trip_classifier, visa_classifier)
    
    # Create ILR Statistics Engine
    ilr_engine = ILRStatisticsEngine(timeline, config)
    
    # Get requirement info
    req_info = ilr_engine.get_ilr_requirement_info()
    
    print(f"First entry date: {req_info['first_entry_date']}")
    print(f"Objective years: {req_info['objective_years']}")
    print(f"Exact days required: {req_info['days_required']:,}")
    print(f"Average days per year: {req_info['average_days_per_year']:.2f}")
    print(f"Calculation method: {req_info['calculation_method']}")
    
    # Manual verification: March 1, 2020 to March 1, 2025 (5 complete years)
    # Year 1: March 1, 2020 to February 29, 2021 = 366 days (2020 is leap year)
    # Year 2: March 1, 2021 to February 28, 2022 = 365 days
    # Year 3: March 1, 2022 to February 28, 2023 = 365 days
    # Year 4: March 1, 2023 to February 29, 2024 = 366 days (2024 is leap year)
    # Year 5: March 1, 2024 to February 28, 2025 = 365 days
    # Total expected: 366 + 365 + 365 + 366 + 365 = 1827 days
    
    expected_days = 366 + 365 + 365 + 366 + 365  # Manual calculation
    print(f"\nManual verification: {expected_days} days expected")
    print(f"Calculation matches: {'✅' if req_info['days_required'] == expected_days else '❌'}")
    
    # Test with different objective years
    print(f"\n=== Testing Different Objective Years ===")
    for years in [5, 6, 10]:
        config.objective_years = years
        engine = ILRStatisticsEngine(timeline, config)
        info = engine.get_ilr_requirement_info()
        print(f"{years} years: {info['days_required']:,} days ({info['average_days_per_year']:.2f} avg/year)")
    
    print("\n✅ ILR requirement calculation test completed")


def test_leap_year_scenarios():
    """Test ILR calculations with specific leap year scenarios."""
    print("\n=== Testing Leap Year Scenarios ===")
    
    # Get project root path
    project_root = Path(__file__).parent.parent
    
    # Test 1: Entry on leap day (Feb 29, 2020)
    print("\n--- Test 1: Entry on Leap Day (Feb 29, 2020) ---")
    config1 = AppConfig(project_root)
    config1.start_year = 2020
    config1.end_year = 2030
    config1.first_entry_date = "29-02-2020"  # Leap day entry
    config1.objective_years = 5
    
    trip_classifier1 = TripClassifier(config1, [])
    visa_classifier1 = VisaClassifier(config1, [])
    timeline1 = DateTimeline.from_config(config1, trip_classifier1, visa_classifier1, use_singleton=False)
    ilr_engine1 = ILRStatisticsEngine(timeline1, config1)
    req_info1 = ilr_engine1.get_ilr_requirement_info()
    
    print(f"Entry: Feb 29, 2020 | Days required: {req_info1['days_required']:,}")
    
    # Test 2: Entry just before leap day (Feb 28, 2020)
    print("\n--- Test 2: Entry Before Leap Day (Feb 28, 2020) ---")
    config2 = AppConfig(project_root)
    config2.start_year = 2020
    config2.end_year = 2030
    config2.first_entry_date = "28-02-2020"
    config2.objective_years = 5
    
    trip_classifier2 = TripClassifier(config2, [])
    visa_classifier2 = VisaClassifier(config2, [])
    timeline2 = DateTimeline.from_config(config2, trip_classifier2, visa_classifier2, use_singleton=False)
    ilr_engine2 = ILRStatisticsEngine(timeline2, config2)
    req_info2 = ilr_engine2.get_ilr_requirement_info()
    
    print(f"Entry: Feb 28, 2020 | Days required: {req_info2['days_required']:,}")
    
    # Test 3: Entry in non-leap year for comparison (Feb 28, 2021)
    print("\n--- Test 3: Non-Leap Year Entry (Feb 28, 2021) ---")
    config3 = AppConfig(project_root)
    config3.start_year = 2021
    config3.end_year = 2030
    config3.first_entry_date = "28-02-2021"
    config3.objective_years = 5
    
    trip_classifier3 = TripClassifier(config3, [])
    visa_classifier3 = VisaClassifier(config3, [])
    timeline3 = DateTimeline.from_config(config3, trip_classifier3, visa_classifier3, use_singleton=False)
    ilr_engine3 = ILRStatisticsEngine(timeline3, config3)
    req_info3 = ilr_engine3.get_ilr_requirement_info()
    
    print(f"Entry: Feb 28, 2021 | Days required: {req_info3['days_required']:,}")
    
    # Analysis
    print(f"\n--- Leap Year Impact Analysis ---")
    leap_day_diff = req_info1['days_required'] - req_info2['days_required']
    print(f"Leap day entry vs day before: {leap_day_diff} day difference")
    
    leap_vs_nonleap = req_info2['days_required'] - req_info3['days_required']  
    print(f"Leap year vs non-leap year entry: {leap_vs_nonleap} day difference")
    
    print("\n✅ Leap year scenario tests completed")

if __name__ == "__main__":
    test_ilr_requirement_calculation()
    test_leap_year_scenarios()