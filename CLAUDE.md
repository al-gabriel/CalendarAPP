# CalendarApp — notes for Claude

Read-only Windows desktop app (Python stdlib + tkinter, no third-party deps) that tracks UK ILR
(Indefinite Leave to Remain) residence days from 2023 to 2040. Spec: `requirements.md`. Plan/progress: `ROADMAP.md`.

## Run
- App (console, shows errors): `CalendarApp.bat`, i.e. `cd src && py -m calendar_app.main`
- App (no console): `CalendarApp_GUI.bat` (`pyw` from `src/`)
- Tests: `py -B tests/run_all_tests.py` (custom runner, plain `assert` tests; register new suites in it)
- `.venv` = Python 3.15 (stdlib only). VS Code: use the "CalendarApp" launch config (F5), not
  "Run Python File" — `main.py` must run as a module (`-m calendar_app.main`) from `src/`.

## Architecture (`src/calendar_app/`)
- `config.py` `AppConfig`: loads `data/config.json`; relative `travel_pdf_folder` resolves against `data/`.
- `storage/json_loader.py` `DataLoader`: loads/validates `trips.json`, `visaPeriods.json`.
- `storage/pdf_index.py` `PDFIndex`: matches travel PDFs by date in filename (e.g. `LGW_LIS_05-11-2023_19-11-2023.pdf`).
- `model/`: `TripClassifier` (trips.py), `VisaClassifier` (visaPeriods.py) → `DateTimeline` singleton
  (timeline.py, every `Day` precomputed) → `ILRStatisticsEngine` (ilr_statistics.py).
- `ui/grid_layout_manager.py`: mediator for a 2×2 grid; modules are wired by constructor callbacks.
  ILRStatisticsModule (top-left), CalendarComponent month/year (right), Month/Year/Day info module (bottom-left).

## Domain
- Day classes: UK_RESIDENCE, SHORT_TRIP (<14 days abroad, counts), LONG_TRIP (≥14 days, does not count),
  NO_VISA_COVERAGE, PRE_ENTRY, UNKNOWN.
- Dates in JSON and filenames are `DD-MM-YYYY`.

## Conventions
- One branch per issue `ISSUE_DD_NN`; PR to `master` titled `Complete ISSUE_DD_NN - <title> (#N)`.
- Never commit personal data: `data/*.json`, `docs/`, `travel_pdfs/` are git-ignored (templates are kept).
- UI modules are not covered by tests. After UI changes, smoke-test by constructing `CalendarApp()`
  with the root withdrawn, or at least import every module.
