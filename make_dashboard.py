"""Build the dashboard chart from the SQLite test database.

Run from the repository root:
    python dashboard/make_dashboard.py

Reads data/factory.db and writes dashboard/query_results_dashboard.png
(rejection rate per machine = Q8, alarms per machine = Q4).
"""
import sqlite3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

DB = "data/factory.db"
OUT = "dashboard/query_results_dashboard.png"

con = sqlite3.connect(DB)
rej = con.execute("""
    SELECT Machine_ID,
           100.0 * SUM(Rejected_Count) / SUM(Production_Count)
    FROM manufacturing_data
    GROUP BY Machine_ID
    HAVING SUM(Production_Count) > 0
    ORDER BY Machine_ID""").fetchall()
alm = con.execute("""
    SELECT Machine_ID, SUM(Alarm)
    FROM manufacturing_data
    GROUP BY Machine_ID
    ORDER BY Machine_ID""").fetchall()
con.close()

fig, ax = plt.subplots(1, 2, figsize=(11, 4.2))
m, v = zip(*rej)
bars = ax[0].bar(m, v, color="#4C78A8")
bars[max(range(len(v)), key=v.__getitem__)].set_color("#E45756")
ax[0].set_title("Q8: Rejection rate per machine")
ax[0].set_ylabel("Rejected / produced (%)")
for b, x in zip(bars, v):
    ax[0].text(b.get_x() + b.get_width() / 2, x, f"{x:.2f}", ha="center", va="bottom", fontsize=8)

m, v = zip(*alm)
bars = ax[1].bar(m, v, color="#59A14F")
bars[max(range(len(v)), key=v.__getitem__)].set_color("#E45756")
ax[1].set_title("Q4: Alarms per machine")
ax[1].set_ylabel("Alarm count")
for b, x in zip(bars, v):
    ax[1].text(b.get_x() + b.get_width() / 2, x, f"{int(x)}", ha="center", va="bottom", fontsize=8)

fig.suptitle("Smart factory test data (synthetic, 10 machines, 7 days). Red = highest.")
plt.tight_layout()
plt.savefig(OUT, dpi=150)
print("saved", OUT)
