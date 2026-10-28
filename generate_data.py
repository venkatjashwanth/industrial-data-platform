"""Seeded simulator for the smart-factory test database (Assignment 4, Part D).

Usage (from the repository root):
    python python/generate_data.py data/factory.db

Creates 10 machines (M01-M10) x 7 days x 1 row per minute = 100,800 rows,
starting 22 Oct 2026 00:00. The data is SYNTHETIC: it shows that the SQL
queries work, it does not describe a real plant.
Production_Count / Rejected_Count are per-minute increments, and
Production_Count includes rejected parts.
The table is created from sql/schema.sql (MySQL syntax is converted to
SQLite syntax: AUTO_INCREMENT -> AUTOINCREMENT).
"""
import os
import sqlite3
import sys
from datetime import datetime, timedelta

import numpy as np

SEED = 217
N_MACHINES = 10
DAYS = 7
START = datetime(2026, 10, 22, 0, 0, 0)

STATES = ["Running", "Idle", "Stopped", "Fault"]
# Per-minute transition probabilities (rows: from, columns: to)
TRANS = np.array([
    [0.985, 0.008, 0.004, 0.003],   # from Running
    [0.040, 0.950, 0.005, 0.005],   # from Idle
    [0.030, 0.010, 0.960, 0.000],   # from Stopped
    [0.000, 0.050, 0.050, 0.900],   # from Fault
])


def load_schema(path):
    sql = open(path, encoding="utf-8").read()
    return sql.replace("INT AUTO_INCREMENT PRIMARY KEY",
                       "INTEGER PRIMARY KEY AUTOINCREMENT")


def simulate_machine(rng, mid):
    # Each machine gets its own personality so the queries have something to find.
    base_temp = 50 + rng.uniform(0, 6)
    vib_base = 1.4 + rng.uniform(0, 1.4)
    reject_p = rng.uniform(0.02, 0.07)
    fault_boost = rng.uniform(0.7, 2.2)   # scales the chance of entering Fault
    trans = TRANS.copy()
    trans[0, 3] *= fault_boost
    trans[0, 0] = 1 - trans[0, 1:].sum()

    rows, state = [], 0
    for k in range(DAYS * 1440):
        state = rng.choice(4, p=trans[state])
        s = STATES[state]
        if s == "Running":
            temp = rng.normal(base_temp + 10, 1.5)
            vib = rng.normal(vib_base, 0.3)
            rpm = int(rng.normal(1450, 25))
            cur = rng.normal(12, 1)
            prod = int(rng.choice([0, 1, 2], p=[0.10, 0.80, 0.10]))
            rej = int(rng.binomial(prod, reject_p))
        elif s == "Idle":
            temp, vib, rpm, cur = rng.normal(base_temp, 1), rng.normal(0.2, 0.05), 0, rng.normal(1.2, 0.2)
            prod = rej = 0
        elif s == "Stopped":
            temp, vib, rpm, cur = rng.normal(base_temp - 8, 1), rng.normal(0.05, 0.02), 0, rng.normal(0.1, 0.05)
            prod = rej = 0
        else:  # Fault
            temp = rng.normal(base_temp + 16, 2)
            vib = rng.normal(vib_base * 2, 0.5)
            rpm = max(0, int(rng.normal(1200, 100)))
            cur = rng.normal(15, 1.5)
            prod = int(rng.choice([0, 1], p=[0.7, 0.3]))
            rej = int(rng.binomial(prod, min(1.0, reject_p * 4)))
        vib = max(0.0, vib)
        cur = max(0.0, cur)
        alarm = int(s == "Fault" and rng.random() < 0.8
                    or vib > 3.5 or temp > base_temp + 14
                    or rng.random() < 0.002)
        ts = (START + timedelta(minutes=k)).strftime("%Y-%m-%d %H:%M:%S")
        rows.append((mid, ts, round(float(temp), 2), round(float(vib), 2), rpm,
                     round(float(cur), 2), prod, rej, s, alarm))
    return rows


def main(db_path):
    root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    schema = load_schema(os.path.join(root, "sql", "schema.sql"))
    os.makedirs(os.path.dirname(os.path.abspath(db_path)), exist_ok=True)
    if os.path.exists(db_path):
        os.remove(db_path)
    rng = np.random.default_rng(SEED)
    con = sqlite3.connect(db_path)
    con.executescript(schema)
    for m in range(1, N_MACHINES + 1):
        con.executemany(
            "INSERT INTO manufacturing_data (Machine_ID, Timestamp, Temperature, Vibration, RPM, "
            "Current, Production_Count, Rejected_Count, Machine_Status, Alarm) "
            "VALUES (?,?,?,?,?,?,?,?,?,?)",
            simulate_machine(rng, f"M{m:02d}"))
    con.commit()
    n = con.execute("SELECT COUNT(*) FROM manufacturing_data").fetchone()[0]
    con.close()
    print(f"Wrote {n:,} rows to {db_path}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "data/factory.db")
