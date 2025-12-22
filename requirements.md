# Visa Residence Calendar App – Requirements

## 1. Domain assumptions

- The user is pursuing UK Indefinite Leave to Remain (ILR) and may be eligible under a **5‑year** or **10‑year** continuous residence route, depending on future rule changes.
- The user wants the app to support up to **objective_years** of qualifying residence, plus up to **processing_buffer_years** to allow for ILR processing time (both configured in **[`config.json`](#2-configuration)**).
- For the user’s personal tracking rules:
  - Any single trip abroad **shorter than 14 days** is treated as:
    - Days still **counting** as in‑UK for ILR days.
    - Days that should also be tracked separately as “short trip days”.
  - Any trip abroad **14 days or longer** is treated as:
    - Days **not counting** towards ILR days.
    - Days that should be tracked as “long trip days”.
- The user holds multiple **visa periods**, each with a start and end (expiry) date (e.g. 2023‑01‑10 to 2024‑09‑14, and 2024‑09‑15 to 2027‑09‑30).
- The first visa started on **10 Jan 2023**, but the first **physical entry** into the UK and the start of ILR day counting is **29 Mar 2023**, which must be configurable.
- The main calendar timeline should cover **1 Jan 2023 to 31 Dec 2040**.

## 2. Configuration

Core configuration is stored in **[`config.json`](#2-configuration)**:

- `travel_pdf_folder`: Folder path for travel PDFs.
- `objective_years`: Integer (e.g. 5 or 10) representing the desired qualifying residence duration.
- `processing_buffer_years`: Integer (e.g. 1) representing extra years allowed for application processing.
- `start_year`: 2023 (fixed for v1).
- `end_year`: 2040 (fixed for v1).
- `first_entry_date`: Date string (e.g. `"2023-03-29"`) specifying when qualifying days start counting.

The **ILR target days** must be computed as:

- `ilr_target_days` = exact count of days from `first_entry_date` + (`objective_years` * 365 days)
- This gives the target completion date by adding exactly N years to the first entry date
- Leap years within this period are automatically included in the date arithmetic
- Example: first_entry_date="2023-03-29" + 10 years = target date "2033-03-29" = 3653 total days

and used in all progress calculations.

The effective **planning horizon** is:

- `objective_years + processing_buffer_years` (e.g. up to 11 years), bounded by the fixed calendar range 2023–2040.

## 3. Functional requirements

### FR‑1: Hardcoded calendar timeline

- The application must build a day‑level timeline for the fixed range:
  - From **2023‑01‑01** to **2040‑12‑31**.
- For each day, the app must know:
  - Its classification:
    - In UK – normal.
    - In UK – part of a short trip (<14 days).
    - Abroad – part of a long trip (≥14 days).
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
  - Classify each trip as:
    - **Short trip** if `trip_length_days < 14`.
    - **Long trip** if `trip_length_days >= 14`.
  - For each day between `departure_date` and `return_date` inclusive:
    - Mark as “abroad”.
    - Tag with the trip’s short/long classification.

### FR‑3: ILR day counting logic

- The app must compute ILR‑counted days only for dates on or after `first_entry_date`.
- For ILR‑style progress, days are classified and counted separately:
  - Days that are not part of any trip and are ≥ `first_entry_date` are counted as **ILR in‑UK days**.
  - Days belonging to a **short trip** (<14 days) and ≥ `first_entry_date`:
    - Are counted separately as **short trip days**.
    - Do **not** contribute to "ILR in‑UK days".
  - Days belonging to a **long trip** (≥14 days) and ≥ `first_entry_date`:
    - Are **not** counted towards any ILR metrics.
    - Contribute to the "long trip days" metric.
- The application must calculate three distinct ILR metrics:
  - **ILR in‑UK days**: Pure UK residence days (excluding short trips).
  - **Short trip days**: Days spent on trips <14 days.
  - **ILR total days**: Sum of "ILR in‑UK days" + "short trip days".
  - **Long trip days**: Days spent on trips ≥14 days.
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
  - In UK – normal.
  - In UK – short trip day.
  - Abroad – long trip day.
  - Visa period boundaries (start and end).
  - Trip period boundaries (start and end) - able to be clicked and open the respective pdf.
- The UI must allow navigation:
  - Changing month and year within the 2023–2040 range.
  - Switching between month view and year view.

### FR‑6: Statistics panels

- **Month view stats:**
  - For the displayed month only (e.g., January 2024), show counts of:
    - ILR in-UK days, Short trip days, ILR total days, Long trip days
- **Year view stats:**
  - For the displayed year only (e.g., all of 2024), show counts of:
    - ILR in-UK days, Short trip days, ILR total days, Long trip days
- **Global stats:**
  - For the full range from 2023‑01‑01 to 2040‑12‑31, the app must show:
    - Total ILR in-UK days since `first_entry_date`
    - Total short trip days since `first_entry_date`
    - Total ILR total days (sum of above two)
    - Total long trip days since `first_entry_date`
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
    - One‑way: `SOR_DES_DD_MM_YYYY`
    - Return: `SOR_DES_DD_MM_YYYY_DD_MM_YYYY`
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
- All dates in JSON must use "YYYY-MM-DD" format.
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
