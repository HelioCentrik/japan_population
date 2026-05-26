# Japan Population Dashboard — Agent Instructions

This repository contains the implementation for the Japan Population Dashboard.

Use this repo for application code, Dash callbacks, Plotly figures, DuckDB logic, ETL scripts, validation queries, runtime AI integration, deployment behavior, and debugging.

Use `HelioCentrik/personal-projects/Japan Population/` for planning docs, roadmap, data dictionary, source notes, modeling decisions, dashboard design notes, and project direction.

## Navigation

Start in the folder most relevant to the task:

- `main.py` — app entrypoint and Gunicorn `server`
- `app/data/` — DuckDB access, SQL views, data loading, cache behavior
- `app/viz/` — chart and figure builders
- `callbacks/` — Dash interactions, filters, playback, map clicks, reset behavior
- `app/aesthetics/` — theme, colors, Plotly template, visual configuration
- `assets/` — static CSS, JavaScript, and images served by Dash
- `scripts/` — ETL/build scripts for database and derived assets
- `data/` — committed database, geospatial files, and generated data assets
- `knowledge/` — runtime AI Q&A context for the dashboard assistant

## Runtime AI Context

`knowledge/AGENT.md` is the system/context prompt for the in-app Gemini Q&A assistant.

`AGENTS.md` is for repository navigation by coding agents.

If `knowledge/AGENT.md` is moved or renamed, update `app/ai.py`.

When loading `knowledge/*.md`, do not include `knowledge/AGENT.md` twice if it is already loaded separately.

## Do Not Use by Default

Do not treat these as normal context unless the user explicitly asks:

- `data/` database or geospatial artifacts
- generated exports
- cache folders
- screenshots, images, videos, or large binary assets
- underscore folders such as `_legacy/`, `_archive/`, or `_evidence/`

Do not regenerate, overwrite, delete, or restructure committed data assets unless the task is explicitly data-pipeline work.

Stay inside this repository unless the user explicitly asks to inspect another repo.