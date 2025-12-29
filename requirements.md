# Visa Residence Calendar App – Requirements

## 1. Domain assumptions

- The user is pursuing UK Indefinite Leave to Remain (ILR) and may be eligible under a **5‑year** or **10‑year** continuous residence route, depending on future rule changes.
- The user wants the app to support up to **objective_years** of qualifying residence, plus up to **processing_buffer_years** to allow for ILR processing time (both configured in **[`config.json`](#2-configuration)**).
- For the user’s personal tracking rules:
  - Any single trip abroad **shorter than 14 days** is treated as:
    - Days spent **abroad** but still **counting** toward ILR total days.
    - Days that should be tracked separately as "short trip days".
    - Days that do **not** contribute to pure "ILR in-UK days".
  - Any trip abroad **14 days or longer** is treated as:
    - Days **not counting** towards any ILR metrics.
    - Days that should be tracked as “long trip days”.
- The user holds multiple **visa periods**, each with a start and end (expiry) date (e.g. 10‑01‑2023 to 14‑09‑2024, and 15‑09‑2024 to 30‑09‑2027).
- The first visa started on **10 Jan 2023**, but the first **physical entry** into the UK and the start of ILR day counting is **29 Mar 2023**, which must be configurable.
- The main calendar timeline should cover **1 Jan 2023 to 31 Dec 2040**.

## 1.5. Key Definitions

**Date Formats:**
- JSON storage: DD-MM-YYYY (e.g., "29-03-2023")
- User interface: DD-MM-YYYY consistently
- Internal calculations: Python `datetime.date` objects

**Trip Classifications:**
- **Short trip:** <14 days duration - days spent abroad but count toward ILR total
- **Long trip:** ≥14 days duration - days spent abroad, do not count toward any ILR metrics

**ILR Day Metrics:**
- **ILR in-UK days:** Pure UK residence days (no trips)
- **Short trip days:** Days on trips <14 days (abroad but count toward ILR)
- **ILR total days:** Sum of ILR in-UK days + short trip days
- **Long trip days:** Days on trips ≥14 days (abroad, do not count toward ILR)

**ILR Counting Rules:**
- Counting starts from `first_entry_date` only (configurable)
- Days before first entry never count toward any ILR metrics
- Target calculation uses exact date arithmetic including leap years
- **Two scenarios tracked due to regulatory uncertainty:**
  - **Scenario 1 (In-UK Only):** Short trips do NOT count toward ILR → only pure UK residence days count
  - **Scenario 2 (Total Days):** Short trips DO count toward ILR → UK residence + short trips count
  - **Both scenarios:** Same target days requirement, long trips never count in either scenario

**ILR Scenario Implications:**
- **In-UK scenario:** More conservative - any travel (short or long) delays completion
- **Total scenario:** More optimistic - only long trips delay completion, short trips help reach target
- **Both scenarios:** Track progress toward dynamically calculated target based on `objective_years` accounting for actual leap years in the period

## 2. Configuration

Core configuration is stored in **[`config.json`](#2-configuration)**:

- `travel_pdf_folder`: Folder path for travel PDFs.
- `objective_years`: Integer (e.g. 5 or 10) representing the desired qualifying residence duration.
- `processing_buffer_years`: Integer (e.g. 1) representing extra years allowed for application processing.
- `start_year`: 2023 (fixed for v1).
- `end_year`: 2040 (fixed for v1).
- `first_entry_date`: Date string specifying when qualifying days start counting (format defined in **[Key Definitions](#15-key-definitions)**).

The **ILR target days** calculation and rules are defined in **[Key Definitions](#15-key-definitions)**. The target is computed by adding exactly `objective_years` to `first_entry_date` using proper date arithmetic.

The effective **planning horizon** is `objective_years + processing_buffer_years`, bounded by the timeline range.

## 3. Functional requirements

### FR‑1: Hardcoded calendar timeline

- The application must build a day‑level timeline for the range defined in **[Key Definitions](#15-key-definitions)**.
- For each day, the app must know:
  - Its classification:
    - In UK – normal residence.
    - Abroad – part of a short trip (<14 days, counts toward ILR total).
    - Abroad – part of a long trip (≥14 days, does not count toward ILR).
  - Which visa period (if any) covers that day.
  - Which trip (if any) that day belongs to.
- ILR counting must **not** start before `first_entry_date`:
  - Days before `first_entry_date` are always treated as non‑qualifying for ILR day totals, even if a visa existed.

### FR‑2: Trip definition and classification

- Trips are stored in `trips.json` and contain at minimum:
  - `id`
  - `departure_date`
  - `return_date`
  - `from_airport`
  - `to_airport`
  - Optional `notes`
- The application must:
  - Compute `trip_length_days` = (`return_date` - `departure_date`) + 1 (inclusive of both dates).
  - Apply trip classifications as defined in **[Key Definitions](#15-key-definitions)**.
  - For each day between `departure_date` and `return_date` inclusive:
    - Mark as “abroad”.
    - Tag with the trip’s short/long classification.

### FR‑3: ILR day counting logic

- The app must compute ILR‑counted days only for dates on or after `first_entry_date`.
- For ILR‑style progress, days are classified and counted using the metrics defined in **[Key Definitions](#15-key-definitions)**:
  - Days that are not part of any trip and are ≥ `first_entry_date` are counted as **ILR in‑UK days**.
  - Days belonging to a **short trip** and ≥ `first_entry_date`:
    - Are counted separately as **short trip days**.
    - Do **not** contribute to "ILR in‑UK days".
  - Days belonging to a **long trip** and ≥ `first_entry_date`:
    - Are **not** counted towards any ILR metrics.
    - Contribute to the "long trip days" metric.
- For each ILR metric type, the app must provide:
  - Current count of days achieved.
  - Target end date when `ilr_target_days` will be reached.
  - Remaining days to reach `ilr_target_days`.
- The application must calculate, over the fixed 2023–2040 range:
  - Total ILR in‑UK days (from `first_entry_date` onwards).
  - Total short trip days.
  - Total ILR total days (sum of above two).
  - Total long trip days.
  - Target completion dates and remaining days for both ILR scenarios:
    - **In-UK scenario:** Based on pure UK residence days only (conservative estimate)
    - **Total scenario:** Based on UK residence + short trips (optimistic estimate)
    - **Both scenarios:** Same target requirement, different counting rules due to regulatory uncertainty

### FR‑4: Visa period management

- Visa periods are stored in `visaPeriods.json` with:
  - `id`
  - `label`
  - `start_date`
  - `end_date`
- The application must:
  - Store multiple visa periods, including the two given examples.
  - Determine which visa period a given date belongs to (or none).
  - Be able to:
    - Highlight the currently active visa period based on today’s date.
    - Compute ILR‑counted days and absence metrics per visa period.
    - Show days remaining until the current visa’s `end_date`.

### FR‑5: Calendar views (month and year)

- The application must provide at least two main views:
  - **Month view**:
    - Shows a standard calendar grid for a single month between 2023 and 2040.
  - **Year view**:
    - Shows a 12-month grid (3x4 or 4x3 layout) for a selected year between 2023 and 2040.
    - Each month shows a mini-calendar with day classifications visible.
- In both views, each day must be visually marked according to its classification:
  - In UK – normal residence.
  - Abroad – short trip day (counts toward ILR total).
  - Abroad – long trip day (does not count toward ILR).
  - Visa period boundaries (start and end).
  - Trip period boundaries (start and end) - able to be clicked and open the respective pdf.
- The UI must allow navigation:
  - Changing month and year within the 2023–2040 range.
  - Switching between month view and year view.

### FR‑6: Statistics panels and UI layout

- **Primary 2x2 Grid Layout:**
  - **Top-left (Primary):** ILR Statistics Module - main focus panel with comprehensive ILR progress tracking
  - **Top-right:** Calendar Component with integrated navigation controls
  - **Bottom-left:** Day Information Module - details for selected day (initially empty/placeholder)
  - **Bottom-right:** Reserved for future expansion (currently hidden)

- **ILR Statistics Module (Top-left - Primary Panel):**
  - **Configuration Section:**
    - Objective years and buffer years from configuration
    - Timeline range display
    - First entry date and days since entry
    - Key configuration parameters for user reference
  - **Dual Scenario Tracking (regulatory uncertainty handling):**
    - **UK Scenario (Conservative):** Only pure UK residence days count toward ILR
      - Current count display with colored indicators
      - Target completion date (clickable, highlights target day on calendar)
      - Remaining days calculation
      - Progress indicators and visual feedback
    - **Total Scenario (Optimistic):** UK residence + short trips count toward ILR
      - Current count display with colored indicators
      - Target completion date (clickable, highlights target day on calendar)
      - Remaining days calculation
      - Progress indicators and visual feedback
    - **Visual Design Requirements:**
      - Yellow highlighting for UK scenario elements
      - Orange highlighting for Total scenario elements
      - Clear section separation and professional styling
      - Target date buttons with raised appearance for interaction feedback
      - Color-coded progress indicators for quick visual assessment
  - **Statistics Display:**
    - Current day counts for all classification types
    - Progress percentages and visual indicators
    - Time-to-completion estimates for both scenarios
    - Leap year accurate calculations with proper date arithmetic

- **Calendar Component (Top-right):**
  - **Integrated Navigation Header:**
    - Month/year navigation controls
    - View switching (Month/Year views)
    - Date selection and highlighting functionality
  - **Calendar Display:**
    - Month view with day-by-day classification coloring
    - Year view support (placeholder implementation)
    - Day selection and interaction capabilities
    - Visual feedback for target dates from ILR statistics

- **Day Information Module (Bottom-left):**
  - Selected day details display
  - Trip information when applicable
  - Visa period information
  - PDF association and opening functionality
  - Currently placeholder implementation for future enhancement

- **Month/Year Context Stats (Integrated into Calendar Component):**
  - For displayed month/year: classification counts and metrics
  - Contextual information relative to current calendar view
  - Integration with main ILR statistics for consistency

### FR‑7: Day details and PDF association

- When a user clicks on a day in the calendar:
  - If the day is part of a trip:
    - Display:
      - Trip type (short or long).
      - From and to airport codes.
      - Departure and return dates.
    - Look up any associated travel PDFs in the configured `travel_pdf_folder`.
  - If the day is not part of a trip:
    - Display that it is an “In UK – normal day” and basic date/visa info.
- PDF association rules:
  - Travel PDFs must be named using one of the patterns:
    - One‑way: `SOR_DES_DD-MM-YYYY`
    - Return: `SOR_DES_DD-MM-YYYY_DD-MM-YYYY`
  - When showing a trip or a travel day, the app should:
    - Identify PDFs whose dates and airports match the trip’s departure/return and airport codes.
    - List matching PDFs (by filename).
    - Provide a way to open a selected PDF externally in the system's default PDF viewer/browser when a day of a trip is clicked.

## 4. Data & storage requirements (JSON)

### NFR‑DATA‑1: JSON‑only persistence

- All persistent data must be stored in JSON files:
  - `config.json` - single object with configuration key-value pairs
  - `visaPeriods.json` - array of visa period objects
  - `trips.json` - array of trip objects
- JSON must be human‑readable and hand‑editable (simple structures, no complex nesting).
- Date formats are defined in **[Key Definitions](#15-key-definitions)**.
- Invalid JSON files should display user-friendly error messages with file name and line number.

### NFR‑DATA‑2: Derived data

- Day‑by‑day classifications and statistics can be calculated on startup and/or on demand from the base JSON data.
- Caching/storing derived data is **encouraged** if it improves performance, provided correctness and accuracy are maintained as the primary focus.
- JSON file modification detection via file timestamps on app startup and/or manual refresh action.
- When JSON changes detected: clear all cached data and recalculate from source files.
- **Manual refresh via UI button** - user clicks "Refresh" button after editing JSON files to reload data.
- App should display last refresh timestamp for user awareness.

## 5. Technical and non‑functional requirements

### NFR‑UI‑1: Platform and technology

- Language: Python 3.x.
- Platform: Windows 10/11 desktop.
- GUI toolkit:
  - **tkinter** (built-in Python GUI) chosen for:
    - Zero external dependencies - works out of the box
    - Simple, predictable API with minimal debugging
    - Built-in Calendar widget via `tkinter.ttk`
    - Perfectly adequate for read-only data visualization
    - Reliable cross-platform file opening via `os.startfile()`
    - Lightweight and stable for personal use

### NFR‑UI‑2: Read‑only v1

- v1 is strictly **read‑only** for data:
  - No GUI‑based creation or editing of trips or visa periods.
- All data entry is performed by:
  - Editing JSON files directly.
  - Placing PDFs in the correct folder with the correct filename pattern.

### NFR‑UI‑3: Front-end Architecture and Design Requirements

- **Modular Component Architecture:**
  - Component-based UI system with clear separation of concerns
  - Reusable components: NavigationHeader, CalendarComponent, StatisticsPanel
  - Module-based approach: individual modules for different UI sections
  - Callback-driven communication between components for loose coupling

- **Grid Layout Management:**
  - 2x2 grid layout managed by GridLayoutManager as main coordinator
  - Dynamic module switching and view management
  - Proper module lifecycle management and cleanup
  - Module isolation: each module self-contained with clear interfaces

- **Visual Design Standards:**
  - **Color Coding System:**
    - Day classifications: distinct colors for UK residence, short trips, long trips, pre-entry
    - ILR scenario differentiation: yellow for UK scenario, orange for Total scenario
    - Visual consistency across all components and modules
  - **Interactive Elements:**
    - Clickable target date buttons with raised styling and hover feedback
    - Calendar day buttons with proper state management and visual feedback
    - Navigation controls with clear visual hierarchy and usability
  - **Typography and Layout:**
    - Fixed header heights for consistency (height=1 for weekday headers)
    - Professional spacing and alignment throughout interface
    - Clear section separation with appropriate padding and margins
    - Consistent font usage and sizing for information hierarchy

- **Responsive Interaction Design:**
  - Calendar navigation: month/year switching with smooth transitions
  - Day selection: visual feedback and information updating
  - Target date highlighting: calendar navigation from statistics to specific dates
  - Error state handling: graceful degradation and user feedback

- **Information Architecture:**
  - **Primary Focus:** ILR statistics and progress tracking prominently displayed
  - **Secondary Information:** Calendar navigation and day classification
  - **Contextual Details:** Day-specific information available on demand
  - **Configuration Transparency:** Key configuration parameters visible for user awareness
  - **Progress Visualization:** Clear progress indicators and completion projections

- **Module Communication Standards:**
  - Callback-based event system for inter-module communication
  - Standardized interfaces for module switching and state management
  - Clean separation between UI state and business logic
  - Consistent error handling and validation across all modules

### NFR‑PERF‑1: Performance

- The app must remain responsive when:
  - Handling the entire 2023–2040 range (18 years) of day‑level data.
  - Navigating between months and years.
- Initial loading and processing of JSON and derived day data should complete in a reasonable time.

### NFR‑SEC‑1: Local‑only, privacy

- All data (JSON, PDFs) remains local on the user’s machine.
- The application must not:
  - Send data over the network.
  - Require any online services or accounts.

### NFR‑EXT‑1: Extensibility

- The codebase should be structured to allow future enhancements, such as:
  - GUI‑based editing of trips and visa periods.
  - Additional ILR‑related checks (e.g. 180‑day rolling absences).
  - Data export (CSV/Excel).
  - Support for multiple user profiles.

## 7. Software Architecture Requirements

### AR-1: Modular Architecture

- **AR-1.1: Single Responsibility Principle**
  - Each module must have a single, well-defined responsibility
  - Classes and functions must not handle multiple unrelated concerns
  - Separation of data models, business logic, storage, and UI layers

- **AR-1.2: Configuration-Driven Design**
  - All configurable parameters must be externalized to `config.json`
  - Business logic must not contain hardcoded values (dates, thresholds, ranges)
  - Timeline creation must require and validate `AppConfig` instance
  - No optional configuration parameters that undermine architectural consistency

- **AR-1.3: Explicit Dependencies**
  - All module dependencies must be explicitly declared through imports
  - No implicit dependencies or global state access
  - Function parameters must be explicit rather than optional when they represent required business context

### AR-2: Date Timeline Foundation

- **AR-2.1: Day-by-Day Data Structure**
  - Complete timeline must be generated for configured date range (e.g., 2023-2040)
  - Each day must be represented as individual `Day` object with classification state
  - Timeline must support day-level granularity for all business operations

- **AR-2.2: Classification System**
  - Implement enum-based `DayClassification` system with values:
    - `UK_RESIDENCE`: Normal UK residence day
    - `SHORT_TRIP`: Day during short trip (<14 days) - counts toward ILR total
    - `LONG_TRIP`: Day during long trip (≥14 days) - does not count toward ILR
    - `PRE_ENTRY`: Before first UK entry date
    - `UNKNOWN`: Classification not yet determined
  - All days must eventually be classified (no `UNKNOWN` days in production)

- **AR-2.3: ILR Business Rules Integration**
  - Business rules are defined authoritatively in **[Key Definitions](#15-key-definitions)** and **[FR-3](#fr3-ilr-day-counting-logic)**
  - Architecture must implement these rules without hardcoding thresholds or logic

### AR-3: Error Handling and Validation

- **AR-3.1: Upward Error Propagation**
  - Modules must propagate errors upward without internal error swallowing
  - Lower-level modules must not handle errors meant for higher-level decision making
  - Validation errors must be descriptive and include context (file names, line numbers, values)

- **AR-3.2: Configuration Validation**
  - `AppConfig` must validate all business rules during initialization
  - Date range validation: years must be within reasonable bounds (2000-2100)
  - Date format validation: formats defined in **[Key Definitions](#15-key-definitions)**
  - First entry date must not allow trips before UK entry

- **AR-3.3: Data Integrity Enforcement**
  - JSON loading must require valid configuration for validation context
  - Trip validation must prevent trips occurring before `first_entry_date`
  - Visa period validation must enforce timeline range boundaries:
    - No visa periods starting before `start_year` (Jan 1)
    - No visa periods extending beyond `end_year` (Dec 31)
  - All date parsing must be consistent and validated

### AR-4: Factory Pattern and Object Creation

- **AR-4.1: Configuration-Only Creation**
  - `DateTimeline` must only be created through `DateTimeline.from_config(config, trip_classifier)`
  - Direct constructor calls must be private/discouraged to enforce validation
  - All business objects must derive their parameters from validated configuration
  - TripClassifier is required parameter (not Optional) to enforce proper error handling

- **AR-4.2: Singleton Pattern (Optional)**
  - `DateTimeline` may implement optional singleton behavior for memory efficiency
  - Singleton must validate configuration consistency across requests
  - Must provide mechanism to reset singleton for testing (`reset_singleton()`)

- **AR-4.3: Initialization-Time Data Building**
  - All data structures must be built during object initialization (constructor)
  - No lazy-loading patterns - all expensive operations happen at creation time
  - Methods should only access pre-built data structures for predictable performance
  - Fail-fast behavior preferred - detect errors at object creation time
  - Clear error messages for missing or invalid required parametersrentation
  - Supports refresh functionality: objects can be recreated to reload data

- **AR-4.4: Data Refresh Architecture**
  - Application must support refresh functionality to reload JSON data changes
  - Refresh must recreate all data-dependent objects (TripClassifier, DateTimeline)
  - UI state must be preserved during refresh (current month view, etc.)
  - All data objects must be designed for recreation without side effects

- **AR-4.5: Required Parameters Policy**
  - Constructor parameters must not use Optional where the parameter is essential for operation
  - Required business objects (TripClassifier, AppConfig) must be mandatory parameters
  - Optional parameters only allowed for genuinely optional features (UI defaults, debugging flags)
  - Maximizes error detection at initialization time rather than runtime

### AR-5: Code Organization and Modularity

- **AR-5.1: Modular Architecture**
  - Core model classes separated into focused modules:
    - `day.py`: Day class and DayClassification enum
    - `timeline.py`: DateTimeline class for day-by-day timeline management
    - `trips.py`: TripClassifier for trip-based logic
    - `visaPeriods.py`: VisaClassifier for visa period logic
    - `ilr_statistics.py`: ILRStatisticsEngine for ILR business logic and completion projections
  - UI architecture:
    - `ui/grid_layout_manager.py`: Main coordinator for 2x2 grid layout
    - `ui/components/`: Reusable UI components
      - `calendar_component.py`: Calendar display with integrated navigation
      - `navigation_header.py`: Reusable navigation controls for date/view switching  
      - `statistics_panel.py`: (deprecated - functionality moved to modules)
      - `month_year_info_panel.py`: (deprecated - functionality moved to modules)
    - `ui/modules/`: Self-contained UI modules for grid sections
      - `ilr_statistics_module.py`: Primary ILR progress tracking panel (top-left)
      - `calendar_month_module.py`: Month calendar grid with day classification
      - `calendar_year_module.py`: Year view implementation (placeholder)
      - `day_info_module.py`: Day details display (placeholder) 
      - `month_info_module.py`: Month context information (placeholder)
      - `year_info_module.py`: Year context information (placeholder)
  - Each module has single responsibility principle
  - Clear separation of concerns between data classification, business logic, and UI presentation

- **AR-5.2: Component-Based UI Architecture**
  - **GridLayoutManager** serves as main coordinator:
    - Manages 2x2 grid layout with module switching capabilities
    - Coordinates inter-module communication through callbacks
    - Handles module lifecycle (creation, switching, cleanup)
    - Provides centralized callback management for date selection and navigation
  - **CalendarComponent** combines navigation and calendar display:
    - Integrates NavigationHeader for date/view switching controls
    - Manages calendar module switching (month/year views)
    - Provides callbacks for date selection and target highlighting
    - Self-contained unit for right side of grid layout
  - **Module Architecture:**
    - Each module is self-contained with clear interface contracts
    - Modules accept callbacks for communication with other components
    - Standardized module creation and switching patterns
    - Support for both active and placeholder module implementations
  - **Callback Communication System:**
    - `on_day_selected`: Day selection events from calendar to info modules
    - `highlight_date`: Target date highlighting from statistics to calendar
    - `switch_to_date`: Navigation requests for month/year switching
    - Clean separation between UI events and business logic responses

- **AR-5.3: Test Code Separation**
  - Test code must be in separate files matching pattern `test_*.py`:
    - `test_day.py`: Tests for Day class and DayClassification
    - `test_timeline.py`: Tests for DateTimeline functionality
    - `test_trips.py`: Tests for TripClassifier functionality
    - `test_visaPeriods.py`: Tests for VisaClassifier functionality
    - `test_ilr_requirement.py`: Tests for ILR statistics and completion calculations
  - Production modules must not contain test functions or main blocks for testing
  - Debug functionality must be controlled by explicit debug flags, not mixed with production code

- **AR-5.4: Import Structure and Current Architecture**
  - Standard Python imports used throughout: `from calendar_app.config import AppConfig`
  - Clear module hierarchy: model layer imports from config layer
  - No circular dependencies between modules
  - Current modular UI architecture:
    - GridLayoutManager handles overall layout coordination and module switching
    - CalendarComponent provides integrated calendar display with navigation
    - NavigationHeader extracted as reusable component across different contexts
    - Module-based approach for different UI sections with clean interfaces
  - Separation of concerns:
    - Timeline handles data classification only
    - ILRStatisticsEngine handles all ILR business logic and completion projections
    - TripClassifier focuses on trip-related functionality only
    - DateTimeline handles day classification using trip data
    - UI modules focus on presentation with business logic accessed through engines


### AR-6: Error Handling and Validation

- **AR-6.1: Constructor Parameter Validation**
  - No Optional parameters for essential business objects in constructors
  - Required dependencies (AppConfig, TripClassifier) must be mandatory parameters
  - Early validation and fail-fast behavior at object creation time
  - Clear error messages for missing or invalid required parameters

- **AR-6.2: Data Validation**
  - JSON data must be validated before object creation
  - Business rule violations must raise appropriate exceptions
  - Configuration consistency must be enforced across all components
  - Type validation and range checking for all user-provided data

### AR-7: Data Consistency and Calculation Accuracy

- **AR-7.1: Avoid Double Counting**
  - ILR total calculations must not double-count computed values
  - When summing day counts, exclude derived totals from sum calculations
  - Example: `total_days = ilr_in_uk_days + short_trip_days + long_trip_days + pre_entry_days` (excludes `ilr_total_days`)

- **AR-7.2: Date Format Standardization**
  - Date formats are defined in **[Key Definitions](#15-key-definitions)** and must be used consistently
  - Internal date objects use Python `datetime.date` for calculations

### AR-8: Debugging and Development Features

- **AR-8.1: Debug Flag System**
  - Debug features must be controlled by explicit boolean flags
  - Debug output must not appear in production unless specifically requested
  - Example: `get_classification_summary(debug=True)` includes detailed statistics

- **AR-8.2: Development vs Production Separation**
  - Production code paths must be clean and performant
  - Debug information available on demand but not by default
  - Validation warnings acceptable in debug mode, silent in production

### AR-9: Dynamic ILR Calculation Requirements

- **AR-9.1: Leap Year Accurate Calculations**
  - ILR requirement calculated dynamically from `objective_years` configuration
  - Accounts for actual leap years in the target period from `first_entry_date`
  - No hardcoded day requirements - adapts to any objective timeframe
  - Proper date arithmetic ensuring accuracy across leap year boundaries

- **AR-9.2: Dual Scenario Architecture**
  - UK scenario: Conservative tracking (only UK residence days count)
  - Total scenario: Optimistic tracking (UK residence + short trips count)
  - Both scenarios use identical target requirement with different counting rules
  - Completion date projections account for scenario-specific implications
  - Visual differentiation in UI (yellow for UK scenario, orange for Total scenario)
  
- **AR-9.3: Statistics Engine Integration**
  - ILRStatisticsEngine provides centralized calculations for all ILR metrics
  - Timeline provides raw day classification data without ILR-specific business logic
  - Clean separation between day classification (Timeline) and ILR calculations (Statistics Engine)
  - Completion date projections with proper leap year handling and future date validation
  
## 6. MVP scope

The minimum viable product (MVP) for this app includes:

- **Data Management:**
  - JSON‑based storage of config, visa periods, and trips
  - Automatic data refresh and validation with file modification detection
  - Configuration-driven timeline generation and business rule application

- **Core ILR Logic:**
  - ILR day counting logic with dual scenario support (UK vs Total scenarios)
  - Short vs long trips based on 14‑day threshold
  - ILR‑counted days vs non‑counted days starting from `first_entry_date`
  - Dynamic target calculation with leap year accuracy
  - Completion date projections for both conservative and optimistic scenarios

- **Primary UI (2x2 Grid Layout):**
  - **ILR Statistics Module (Primary Focus):** Comprehensive progress tracking with:
    - Configuration information display
    - Dual scenario progress with color coding (yellow/orange)
    - Clickable target completion dates
    - Progress indicators and remaining days calculations
  - **Calendar Component:** Month view with integrated navigation:
    - Day classifications with color coding
    - Interactive navigation header
    - Day selection and highlighting capabilities
    - Target date highlighting from statistics module
  - **Day Information Module:** Selected day details (placeholder implementation)
  - **Modular Architecture:** Clean component separation with callback communication

- **Calendar Views:**
  - Month calendar view within 2023–2040 range with day classifications
  - Year view framework (placeholder implementation for future enhancement)
  - Context-aware statistics for displayed month/year periods

- **Interactive Features:**
  - Day click functionality for trip details
  - PDF association and system opening functionality  
  - Calendar navigation from statistics target dates
  - Visual feedback for user interactions

- **Technical Implementation:**
  - Local‑only, read‑only GUI using tkinter
  - Modular component architecture with clear separation of concerns
  - Configuration-driven design with external JSON parameter storage
  - Professional visual design with consistent color coding and styling

**Current Implementation Status:**
- ✅ Complete: Core data models, ILR statistics engine, timeline management
- ✅ Complete: Primary UI layout with ILR statistics focus and calendar navigation
- ✅ Complete: Month view calendar with day classification and interaction
- 🔄 Placeholder: Year view, day details, and advanced PDF integration (ready for future enhancement)
- ✅ Complete: Modular architecture supporting easy feature extension
