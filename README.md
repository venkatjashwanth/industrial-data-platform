# industrial-data-platform

Smart factory cloud and data infrastructure for 100 CNC machines across three plants.
Course: Industrial Data Analytics (ME 217), Assignment 4.
Repository: https://github.com/venkatjashwanth/industrial-data-platform

## Problem statement
A manufacturer needs a scalable, secure and affordable infrastructure for monitoring, analytics, storage,
dashboards, AI/ML development and remote access. This project sizes the data, compares AWS, Azure and
Google Cloud, designs a SQL schema for machine data, and proposes an edge-cloud architecture.

## Industrial scenario
- 100 CNC machines in 3 plants (about 33 per plant)
- 10 sensor streams per machine at 1 Hz, plus one 100 Hz vibration sensor per machine (extension)
- Raw volume about 15.2 GB a day; about 0.76 GB a day after edge processing (95% reduction)

## Dataset description
Synthetic data from a seeded simulator (seed 217): 10 machines (M01-M10), one row per machine per minute,
7 days from 22 Oct 2026, 100,800 rows. It shows that the queries work; it does not describe a real plant.
Production_Count and Rejected_Count are per-minute increments. Production_Count includes rejected parts.

## Software and libraries
Python 3, numpy and matplotlib (see requirements.txt), SQLite 3 for testing, MySQL 8.0+ syntax for the SQL files.

## How to run
1. `pip install -r requirements.txt`
2. `python python/generate_data.py data/factory.db` rebuilds the test database.
3. `python dashboard/make_dashboard.py` draws the query-result chart into `dashboard/`.

## SQL database instructions
- `sql/schema.sql` creates the table, constraints and indexes (MySQL 8 syntax).
- `sql/queries.sql` holds queries Q1 to Q8 (one per question in the brief). "Highest" questions use RANK(),
  so tied machines are all returned.
- To run on SQLite: `sqlite3 data/factory.db < sql/queries.sql`
- Testing note: queries were run on SQLite, not on a MySQL server.

## Key findings
- Recommended platform: Microsoft Azure (weighted score 4.15, AWS 3.95, Google Cloud 3.35). The margin is
  narrow; the report shows where it holds and where it flips.
- A 100 Hz sensor produces as much data as 100 slow sensors; edge feature extraction cuts the data sent by 95%.
- Hard real-time protection stays in the PLC; the edge gateway raises alerts and buffers data; the cloud does
  fleet analytics and model training.

## Architecture overview
See `diagrams/F1_azure_architecture.png` (nine blocks from machine to decision) and
`diagrams/G1_hybrid_edge_cloud.png` (edge versus cloud split). Full explanation in `report.pdf`.

## Repository structure
```
industrial-data-platform/
├── data/        factory.db (generated test database)
├── python/      generate_data.py
├── sql/         schema.sql, queries.sql
├── dashboard/   make_dashboard.py, query_results_dashboard.png
├── diagrams/    F1_azure_architecture.png, G1_hybrid_edge_cloud.png
├── README.md
├── requirements.txt
└── report.pdf
```

## Group
Jashwanth, Aksah, Ayush, Tulasi, Kushal, Benedict, Hoysala
