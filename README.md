# Visa Residence Calendar App

A small Python Windows desktop app to help track UK residence days for ILR (Indefinite Leave to Remain) using a calendar‑style interface and simple JSON files.

The app is **read‑only** in v1: all data is stored and edited in JSON by the user, and the GUI focuses on visualizing days in the UK vs abroad, visa periods, and ILR‑relevant statistics over a fixed calendar range (2023–2040).

## Goals

- Track progress towards an ILR objective measured in **years of qualifying residence** (configurable, e.g. 5 or 10 years).
- Allow for an extra **processing buffer** (e.g. 1 year) beyond the main objective to cover ILR processing time.
- Distinguish between:
  - Short trips abroad (<14 days) that still count towards ILR days (but are tracked separately).
  - Long trips abroad (≥14 days) that do **not** count towards ILR days.
- Provide month and year calendar views with per‑period statistics, limited to **2023–2040**.
- Store all configuration and data in easy‑to‑edit JSON files.
- Link travel PDFs (itineraries, tickets) to travel days based on a strict filename convention.

## Timeline and visas

- The **calendar and data model** cover a fixed range: **1 Jan 2023 to 31 Dec 2040**.
- ILR counting starts from the user’s **first physical entry** into the UK (configured in JSON), not necessarily the first visa start date.
- Example visa history:
  - Visa 1: 10 Jan 2023 – 14 Sep 2024.
  - Visa 2: 15 Sep 2024 – 30 Sep 2027.
- The app shows visa periods for context and per‑visa statistics, but qualifying days begin at the configured first‑entry date (e.g. `2023‑03‑29`).

## High‑level behavior

- The app builds a day‑by‑day timeline from 2023‑01‑01 to 2040‑12‑31.
- Each day is classified as:
  - In UK – normal.
  - In UK – part of a short trip (<14 days abroad, still ILR‑counted).
  - Abroad – part of a long trip (≥14 days, not ILR‑counted).
- ILR target days are computed from configuration:
  - `objective_years` × 365
  - For example, 5 years → 1825 days, 10 years → 3650 days.
- ILR‑counted days and absences are derived from a list of trips defined in JSON.

## Data model (JSON)

> v1 design: JSON is the **source of truth** and is edited manually by the user.

### Data files documentation

All JSON files used by the app live in the `data/` folder (`config.json`, `visaPeriods.json`, `trips.json`).  

For a quick description of every field and how to edit them by hand, see:

- [`data\README.md`](data/README.md)

This keeps the JSON files themselves clean and valid while the explanations live in one simple place next to the data.

