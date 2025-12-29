#!/usr/bin/env python3
"""
Comprehensive Test Runner for Calendar App
Runs all tests in the proper order with clear reporting.
"""

import sys
import os
from pathlib import Path

# Add the src directory to Python path
project_root = Path(__file__).parent.parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

def run_all_tests():
    """Run all test suites in the proper order."""
    print("🔬 Starting Calendar App Comprehensive Test Suite")
    print("=" * 60)
    
    # Import test modules
    try:
        # Model tests
        from model.test_day import run_all_day_tests
        from model.test_timeline import run_all_timeline_tests  
        from model.test_trips import run_all_trips_tests
        from model.test_visaPeriods import run_all_visaPeriod_tests
        from model.test_ilr_statistics import run_all_ilr_statistics_tests
        
        # Integration tests
        from test_ilr_requirement import test_ilr_requirement_calculation, test_leap_year_scenarios
        
        print("✅ All test modules imported successfully\n")
        
    except ImportError as e:
        print(f"❌ Failed to import test modules: {e}")
        return False
    
    # Test execution order (dependencies matter)
    test_suites = [
        ("Day Model Tests", run_all_day_tests),
        ("Trip Classifier Tests", run_all_trips_tests),
        ("Visa Classifier Tests", run_all_visaPeriod_tests),
        ("Timeline Tests", run_all_timeline_tests),
        ("ILR Statistics Engine Tests", run_all_ilr_statistics_tests),
        ("ILR Requirement Tests", test_ilr_requirement_calculation),
        ("Leap Year ILR Tests", test_leap_year_scenarios)
    ]
    
    passed_tests = 0
    failed_tests = 0
    
    for suite_name, test_function in test_suites:
        print(f"\n🧪 Running {suite_name}")
        print("-" * 50)
        
        try:
            test_function()
            print(f"✅ {suite_name} PASSED")
            passed_tests += 1
            
        except Exception as e:
            print(f"❌ {suite_name} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed_tests += 1
            
        print("-" * 50)
    
    # Final summary
    total_tests = passed_tests + failed_tests
    print(f"\n{'='*60}")
    print(f"🏁 TEST SUITE SUMMARY")
    print(f"{'='*60}")
    print(f"Total Test Suites: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print(f"\n🎉 ALL TESTS PASSED! Calendar App is working correctly.")
        return True
    else:
        print(f"\n⚠️  {failed_tests} test suite(s) failed. Please review the errors above.")
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)