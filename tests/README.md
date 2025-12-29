# Tests Directory

This directory contains all test files for the Calendar App project, organized following Python testing best practices.

## Structure

```
tests/
├── run_all_tests.py          # Main test runner - executes all tests
├── test_ilr_requirement.py   # Integration tests for ILR calculations
└── model/                    # Unit tests for model components
    ├── test_day.py           # Day class and DayClassification tests
    ├── test_timeline.py      # DateTimeline class tests (core timeline functionality)
    ├── test_ilr_statistics.py # ILRStatisticsEngine tests (ILR business logic)
    ├── test_trips.py         # TripClassifier class tests
    └── test_visaPeriods.py   # VisaClassifier class tests
```

## Test Coverage

- **Day Model**: Comprehensive testing of Day class functionality, classification methods, and basic data properties
- **Timeline**: Core DateTimeline testing including singleton behavior, date range operations, classification methods, and auto-classification
- **ILR Statistics Engine**: Complete ILR business logic testing including progress calculations, leap year requirements, counting methods, projections, and eligibility checking
- **Trip Classifier**: TripClassifier functionality with real/mock data, overlapping trip detection, and edge cases
- **Visa Classifier**: VisaClassifier operations, period validation, salary transitions, and timeline coverage
- **Integration**: End-to-end ILR requirement calculations with leap year handling and comprehensive scenarios

## Test Dependencies

Tests use mock objects where appropriate to avoid file system dependencies:
- `MockAppConfig` for configuration testing
- `MockTripClassifier` for timeline tests
- `MockVisaPeriodClassifier` for timeline tests

All tests can run independently without requiring real JSON configuration files.

## Architectural Changes

This test organization represents a move from production-embedded tests to a separate test directory structure, following Python best practices:

- ✅ Separation of concerns (tests vs production code)
- ✅ Clear test discovery and execution  
- ✅ Maintainable test organization
- ✅ Comprehensive coverage reporting
- ✅ Separated ILR business logic from core timeline functionality

## Key Testing Architecture

- **Timeline Tests**: Focus on core timeline functionality (date management, classification, auto-classification)
- **ILR Statistics Tests**: Focus on ILR business logic (progress tracking, leap year calculations, projections)
- **Integration Tests**: End-to-end scenarios combining timeline and ILR statistics
- **Mock Objects**: Clean separation using MockAppConfig, MockTripClassifier, and MockVisaPeriodClassifier