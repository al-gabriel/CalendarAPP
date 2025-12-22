# Data files overview

This folder contains all the JSON files the app reads.  
You edit these by hand; the app never writes to them in v1.

## config.json

Global settings for how the app behaves.

Fields:

- **travel_pdf_folder** (string, path)  
  Folder where your travel PDFs live (e.g. `"../travel_pdfs"`).

- **objective_years** (int)  
  ILR residence objective in years (e.g. `5` or `10`).  
  Target days = `objective_years * 365`.

- **processing_buffer_years** (int)  
  Extra years allowed beyond `objective_years` for ILR processing (e.g. `1`).

- **start_year** (int)  
  First calendar year shown by the app (fixed to `2023` in your case).

- **end_year** (int)  
  Last calendar year shown by the app (fixed to `2040`).

- **first_entry_date** (string, `DD-MM-YYYY`)  
  Date you first physically entered the UK on this route (e.g. `"29-03-2023"`).  
  ILR‑counted days start from here, even if the first visa started earlier.

---

## visa_periods.json

List of your visa periods.

Each element:

- **id** (string)  
  Unique internal ID (e.g. `"visa_1"`).

- **label** (string)  
  Human name (e.g. `"Skilled Worker 1"`).

- **start_date** (string, `DD-MM-YYYY`)  
  Visa start date (e.g. `"10-01-2023"`).

- **end_date** (string, `DD-MM-YYYY`)  
  Visa end/expiry date (e.g. `"14-09-2024"`).

Used for:
- Showing visa boundaries on the calendar.  
- Computing stats per visa period.  

ILR days still start from `first_entry_date` in **[`config.json`](#2-configuration)**.

---

## trips.json

List of all trips abroad.

Each element:

- **id** (string)  
  Unique trip ID (any naming you like).

- **departure_date** (string, `DD-MM-YYYY`)  
  Date you leave the UK.

- **return_date** (string, `DD-MM-YYYY`)  
  Date you arrive back in the UK.  
  Trip length = `(return_date - departure_date) + 1`.

- **from_airport** (string, 3‑letter code)  
  Departure airport (e.g. `"LHR"`).

- **to_airport** (string, 3‑letter code)  
  Destination airport (e.g. `"LIS"`).

- **notes** (string)  
  Free text (reason for trip, etc.).

Trip classification:

- `< 14` days → **short trip**  
  - Days are abroad but still ILR‑counted.  
  - Counted in “short trip days”.

- `>= 14` days → **long trip**  
  - Days are abroad and **not** ILR‑counted.  
  - Counted in “long trip days”.

Only days on or after `first_entry_date` can count towards ILR totals.

---

## Travel PDFs (folder from config)

Files in `travel_pdf_folder` should follow:

- One‑way: `SOR_DES_DD_MM_YYYY`  
- Return: `SOR_DES_DD_MM_YYYY_DD_MM_YYYY`

Where:

- `SOR` – source airport code (e.g. `LHR`).  
- `DES` – destination airport code (e.g. `OPO`).  
- `DD_MM_YYYY` – date of flight.

The app matches filenames to trips using dates and airport codes and shows them when you click a travel day.
