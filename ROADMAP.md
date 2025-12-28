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
- [ ] **Trip Classification System**
  - `model/trips.py` - short vs long trip logic
  - `model/visa_periods.py` - visa period matching
  - Assign each day its proper classification (UK/short trip/long trip)
  - **Test:** Verify trip classifications match your data

- [ ] **Visual Day Classification**
  - Color-code calendar days based on classification:
    - Normal UK days: Light gray/white
    - Short trip days: Light blue
    - Long trip days: Light red
    - Pre-first-entry: Disabled/gray
  - **Test:** Calendar visually shows your trip patterns

### Afternoon Session (2-3 hours)
- [ ] **ILR Statistics Engine**
  - `model/stats.py` - core ILR counting logic
  - Calculate separate metrics: ILR in-UK days, Short trip days, ILR total days
  - Month/Year/Global statistics calculations
  - **Test:** Verify statistics match manual calculations

- [ ] **Statistics UI Panel**
  - `ui/stats_panel.py` - display statistics for current month
  - Show both ILR scenarios (in-UK vs total)
  - Target completion dates and remaining days
  - **Test:** See real progress numbers for your ILR journey

### Evening Session (1-2 hours)
- [ ] **Basic Day Interaction**
  - Click any day to show basic popup
  - Normal day: "UK residence day + date"
  - Trip day: "Trip day + basic info"
  - **Test:** Click interaction works on different day types

**Day 2 Deliverable:** Full-featured calendar showing your real ILR progress with visual day classification and statistics

---

## 🎯 **Day 3: Polish & Complete Features**
**Goal:** Production-ready app with all MVP features

### Morning Session (2-3 hours)
- [ ] **Complete Day Details**
  - Enhanced day popup with full trip information
  - Trip type (short/long), airports, departure/return dates
  - Visa period information for each day
  - **Test:** Rich day details match your trip data

- [ ] **Year View**
  - `ui/calendar_view.py` - add year view mode
  - 12-month mini-calendar grid (3x4 layout)
  - Month/Year view toggle buttons
  - **Test:** Switch between month and year views smoothly

### Afternoon Session (2-3 hours)
- [ ] **Global Statistics & Filtering**
  - Global statistics panel (full 2023-2040 range)
  - Visa period filtering (checkboxes for multiple selection)
  - Dual scenario tracking (in-UK vs total scenarios)
  - **Test:** Filter statistics by different visa combinations

- [ ] **PDF Integration**
  - `storage/pdf_index.py` - filename pattern matching
  - External PDF opening via `os.startfile()`
  - List matching PDFs for trip days
  - **Test:** Click trip day opens correct PDF files

### Evening Session (1-2 hours)
- [ ] **Final Polish**
  - Refresh button to reload JSON files
  - Last refresh timestamp display
  - Error messages for missing files
  - Window sizing and layout improvements
  - **Test:** Complete user workflow (edit JSON → refresh → view changes)

**Day 3 Deliverable:** Complete, production-ready Calendar App v1.0

---

## ✅ **Success Criteria**
By end of Day 3, the app must:
- [X] Load and display your real ILR data accurately
- [ ] Show visually distinct day classifications
- [ ] Calculate correct ILR progress statistics
- [ ] Provide both month and year calendar views
- [ ] Support day-click interactions with trip details
- [ ] Open your travel PDFs externally
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