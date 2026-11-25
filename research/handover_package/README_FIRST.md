# Research Handover Package — Read This First

**Prepared:** 7 November 2026  
**Project:** BLRMap Prototype — Two-Wheeler-Aware Routing  
**Purpose:** Continue the research with a new GPT or Claude without losing decisions, evidence, or project history.

## Start here
1. Read `MASTER_PROJECT_CONTEXT.md`.
2. Read `PAPER_1_STATUS.md`.
3. Read `PAPER_2_RESEARCH_PLAN.md`.
4. Read `STRAVA_FIELD_TEST_AND_ROUTE_PROVENANCE.md`.
5. Paste `NEW_ASSISTANT_START_PROMPT.md` into the new conversation.
6. Upload this ZIP and, if possible, the actual BLRMap project repository.

## Important working decision
The user has stated that the CMH Road / Indiranagar / Murphy Road afternoon route was recommended by the user's own project after a rerouting event. The user followed that recommendation on 3 November and again on 6 November. Accept this as the user's firsthand account and working premise for continuing the research. Do not spend further Antigravity tokens trying to prove or disprove it unless the user explicitly asks.

The historical MongoDB route snapshot for the afternoon does not match the CMH Road route, and the application did not preserve a contemporaneous route record. Preserve this as a documentation limitation; do not repeatedly challenge the user's account or treat the route as an external app recommendation.

## Package contents
- Research handover documents.
- Five Strava GPX files and five activity screenshots.
- Route recovery and provenance audit reports available in this chat.
- Paper 1 final PDF, LaTeX source, and Overleaf packages.
- Paper 1 experimental data/script and selected figures.

## Scope limitation
This package does not contain the complete local BLRMap source repository or live MongoDB credentials/data. The new assistant must not assume it can access Antigravity, the user's computer, or MongoDB. Ask for specific files only when genuinely needed.

## Evidence labels
- **Direct artifact:** a file included in this package.
- **User-confirmed:** explicitly reported by the user; treat as a working premise.
- **Recovered historical snapshot:** geometry stored in MongoDB, but may not prove what was displayed at a specific moment.
- **Measured:** directly calculated from GPX or experimental datasets.
- **Unverified:** not yet established from retained logs or records.
