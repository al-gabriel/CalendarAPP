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

**Timeline Range:** 01-01-2023 to 31-12-2040 (18 years, fixed for v1)

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
  - Target completion dates and remaining days for both "ILR in‑UK days" and "ILR total days" scenarios.

### FR‑4: Visa period management

- Visa periods are stored in `visa_periods.json` with:
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

### FR‑6: Statistics panels

- **Month view stats:**
  - For the displayed month only, show counts of all ILR metrics defined in **[Key Definitions](#15-key-definitions)**
- **Year view stats:**
  - For the displayed year only, show counts of all ILR metrics defined in **[Key Definitions](#15-key-definitions)**
- **Global stats:**
  - For the timeline range defined in **[Key Definitions](#15-key-definitions)**, show all ILR metrics since `first_entry_date`
    - **Dual scenario tracking:**
      - ILR in-UK scenario: current count, target end date, remaining days to reach `ilr_target_days`
      - ILR total scenario: current count, target end date, remaining days to reach `ilr_target_days`
  - The app should allow:
    - Filtering global stats by visa period selection:
      - "All periods" (default) - shows metrics across all visa periods
      - Single period selection (e.g. "visa_1 only")  
      - Multiple period selection (e.g. "visa_1 + visa_2")
      - UI should provide checkboxes or dropdown for period selection

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
  - `visa_periods.json` - array of visa period objects
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
  - `DateTimeline` must only be created through `DateTimeline.from_config(config)`
  - Direct constructor calls must be private/discouraged to enforce validation
  - All business objects must derive their parameters from validated configuration

- **AR-4.2: Singleton Pattern (Optional)**
  - `DateTimeline` may implement optional singleton behavior for memory efficiency
  - Singleton must validate configuration consistency across requests
  - Must provide mechanism to reset singleton for testing (`reset_singleton()`)

### AR-5: Code Organization and Modularity

- **AR-5.1: Test Code Separation**
  - Test code must be in separate files (e.g., `test_dates.py`)
  - Production modules must not contain test functions or main blocks for testing
  - Debug functionality must be controlled by explicit debug flags, not mixed with production code

- **AR-5.2: No Duplicate Functionality**
  - Avoid convenience functions that simply wrap class methods without added value
  - Maintain single source of truth for business logic
  - Class-based APIs preferred over parallel functional APIs

- **AR-5.3: Import Structure**
  - Relative imports within package: `from ..config import AppConfig`
  - Clear module hierarchy: model layer imports from config layer
  - No circular dependencies between modules

### AR-6: Data Consistency and Calculation Accuracy

- **AR-6.1: Avoid Double Counting**
  - ILR total calculations must not double-count computed values
  - When summing day counts, exclude derived totals from sum calculations
  - Example: `total_days = ilr_in_uk_days + short_trip_days + long_trip_days + pre_entry_days` (excludes `ilr_total_days`)

- **AR-6.2: Date Format Standardization**
  - Date formats are defined in **[Key Definitions](#15-key-definitions)** and must be used consistently
  - Internal date objects use Python `datetime.date` for calculations

### AR-7: Debugging and Development Features

- **AR-7.1: Debug Flag System**
  - Debug features must be controlled by explicit boolean flags
  - Debug output must not appear in production unless specifically requested
  - Example: `get_classification_summary(debug=True)` includes detailed statistics

- **AR-7.2: Development vs Production Separation**
  - Production code paths must be clean and performant
  - Debug information available on demand but not by default
  - Validation warnings acceptable in debug mode, silent in production

## 6. MVP scope

The minimum viable product (MVP) for this app includes:

- JSON‑based storage of config, visa periods, and trips.
- Core ILR day counting logic:
  - Short vs long trips based on 14‑day threshold.
  - ILR‑counted days vs non‑counted days starting from `first_entry_date`.
- Month and year calendar views within 2023–2040:
  - Day classifications.
  - Month/year/global statistics panels.
- Day click:
  - Trip details.
  - PDF association and open functionality.
- Local‑only, read‑only GUI.
