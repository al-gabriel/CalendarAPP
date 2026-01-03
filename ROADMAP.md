# Calendar App Development Roadmap
**Target Timeline: 3 Days Maximum**

*AI does heavy lifting, user tests/debugs/provides direction*

---

## 🚀 **Day 1: Foundation & Core Calendar**
**Goal:** Working calendar app that loads real data

### Morning Session (2-3 hours)
- [X] **Project Structure Setup**
  - Create all Python files in `src/calendar_app/`
  - `main.py`, `config.py`, basic module structure
  - Basic tkinter window with title

- [X] **JSON Loading System**
  - Implement `config.py` - load and validate `config.json`
  - Implement `storage/json_loader.py` for trips and visa periods
  - Error handling for invalid JSON files
  - **Test:** App starts, loads your real JSON files, shows basic info

### Afternoon Session (2-3 hours)
- [X] **Basic Month Calendar**
  - `ui/calendar_view.py` - month grid using tkinter
  - Show current month (December 2025)
  - Basic date navigation (Previous/Next month buttons)
  - Date range validation (2023-2040 only)
  - **Test:** Navigate through months, see proper date grids

### Evening Session (1-2 hours)
- [X] **Date Timeline Foundation**
  - `model/dates.py` - generate 2023-2040 day-by-day timeline
  - Each day knows its date and basic classification
S  - Full classification integration with counting and querying methods
  - **Test:** App can identify any date within range and count classifications

**Day 1 Deliverable:** Working calendar app that loads your data and shows navigable month views

---

## ⚡ **Day 2: Smart Calendar & Statistics**
**Goal:** Visually meaningful calendar with ILR progress tracking

### Morning Session (2-3 hours)
- [X] **Trip Classification System**
  - `model/trips.py` - short vs long trip logic
  - `model/visaPeriods.py` - visa period matching
  - Assign each day its proper classification (UK/short trip/long trip)
  - **Test:** Verify trip classifications match your data

- [X] **Visual Day Classification**
  - Color-code calendar days based on classification:
    - Normal UK days: Light gray/white
    - Short trip days: Light blue
    - Long trip days: Light red
    - Pre-first-entry: Disabled/gray
  - **Test:** Calendar visually shows your trip patterns

### Afternoon Session (2-3 hours)
- [X] **ILR Statistics Engine**
  - `model/ilr_statistics.py` - core ILR counting logic and dual scenario support
  - Calculate separate metrics: ILR in-UK days, Short trip days, ILR total days
  - Month/Year/Global statistics calculations with progress tracking
  - **Test:** Verify statistics match manual calculations

- [X] **Statistics UI Panel**
  - `ui/components/statistics_panel.py` - display statistics component  
  - Show both ILR scenarios (in-UK vs total) with completion dates
  - Target completion dates and remaining days for each scenario
  - **Test:** See real progress numbers for your ILR journey

### Evening Session (1-2 hours)
- [X] **Basic Day Interaction** ✅ *ENHANCED - Complete day information module implemented*
  - Click any day to show detailed day information panel
  - Trip days: Full flight routes (outbound/inbound), trip classification, clickable dates
  - Visa period information display with date navigation
  - Back button to return to month view
  - **Test:** Click interaction works with rich trip details, proper multi-airport routing

**Day 2 Deliverable:** Full-featured calendar showing your real ILR progress with visual day classification and statistics

---

## 🎯 **Day 3: Polish & Complete Features**
**Goal:** Production-ready app with all MVP features

### Morning Session (2-3 hours)
- [X] **New Day Classification: Days Without Visa Coverage** ⚠️ *CRITICAL ADDITION*
  - Add `NO_VISA_COVERAGE` classification to `day.py` for UK residence days not covered by any visa period
  - These days **count toward ILR totals** but are **tracked separately for visa requirement planning**
  - Update throughout project: ILR statistics engine, calendar view (light red color)
  - **Test:** Days without visa coverage properly included in ILR counts but tracked as separate metric

- [ ] **Year View Implementation**
  - Implement full `calendar_year_module.py` using whole column 2 (cells 2x2 and 1x2 in 2x2 grid)
  - 12-month mini-calendar grid (3x4 layout) similar to `calendar_month_module.py`
  - Month/Year view toggle integration with existing navigation
  - **Test:** Switch between month and year views smoothly with proper day classifications

- [ ] **Visa Period Visual Integration**
  - Add different colors for visa period start/end days in calendar views
  - Integrate visa coverage validation with new day classification
  - **Test:** Visa periods clearly visible in both month and year views

### Afternoon Session (2-3 hours)
- [ ] **PDF Integration in Day Info Module**
  - Implement "View" buttons in `day_info_module.py` for specific outbound/inbound flights
  - Create `storage/pdf_index.py` for filename pattern matching
  - External PDF opening via `os.startfile()` - same PDF opens for both flights if they share same document
  - **Test:** Click "View" button on trip day opens correct PDF files

### Evening Session (1-2 hours)
- [ ] **Data Refresh System**
  - Add "Refresh" button to main UI (likely in navigation header)
  - Implement JSON file reload functionality without app restart
  - Recreate all data objects (TripClassifier, DateTimeline, ILRStatisticsEngine)
  - Last refresh timestamp display
  - **Test:** Edit JSON files → click refresh → see changes immediately

**Day 3 Deliverable:** Complete, production-ready Calendar App v1.0

---

## ✅ **Success Criteria**
By end of Day 3, the app must:
- [X] Load and display your real ILR data accurately
- [X] Show visually distinct day classifications
- [X] Calculate correct ILR progress statistics
- [X] Support day-click interactions with trip details ✅ *ENHANCED - Complete day info module*
- [X] Handle days without visa coverage (new classification)
- [ ] Provide both month and year calendar views
- [ ] Show visa period boundaries in calendar
- [ ] Open your travel PDFs externally from day details
- [ ] Handle data refresh without restart
- [ ] Work reliably for daily use

---

## 🔧 **Development Notes**
- **AI Focus:** Core logic, data processing, UI implementation
- **User Focus:** Testing, feedback, direction changes, edge case identification
- **Daily Check-ins:** End of each day demo and feedback session
- **Scope Control:** If features take longer, prioritize core calendar + statistics over polish features
- **Quality Target:** Working reliably for personal daily use, not commercial polish

**Ready to build your ILR tracking app in 3 days!** 🚀