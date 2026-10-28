-- =====================================================
-- queries.sql  |  Q1-Q8 for Assignment 4, Part D
-- Written for MySQL 8.0+ (CTEs and RANK() need 8.0).
-- Also tested on SQLite 3 (see README).
-- "Highest" questions use RANK(), so tied machines are all returned.
-- =====================================================

-- Q1. Average temperature of each machine
SELECT Machine_ID,
       ROUND(AVG(Temperature), 2) AS Avg_Temperature
FROM manufacturing_data
GROUP BY Machine_ID
ORDER BY Avg_Temperature DESC;


-- Q2. Machine that produced the highest number of parts
WITH totals AS (
    SELECT Machine_ID, SUM(Production_Count) AS Total_Parts
    FROM manufacturing_data
    GROUP BY Machine_ID
), ranked AS (
    SELECT Machine_ID, Total_Parts,
           RANK() OVER (ORDER BY Total_Parts DESC) AS rnk
    FROM totals
)
SELECT Machine_ID, Total_Parts
FROM ranked
WHERE rnk = 1;


-- Q3. Machine with the highest average vibration
-- Rank on the unrounded average so rounding cannot create false ties.
WITH avgs AS (
    SELECT Machine_ID, AVG(Vibration) AS Avg_Vib_Raw
    FROM manufacturing_data
    GROUP BY Machine_ID
), ranked AS (
    SELECT Machine_ID, Avg_Vib_Raw,
           RANK() OVER (ORDER BY Avg_Vib_Raw DESC) AS rnk
    FROM avgs
)
SELECT Machine_ID, ROUND(Avg_Vib_Raw, 2) AS Avg_Vibration
FROM ranked
WHERE rnk = 1;


-- Q4. Number of alarms per machine
SELECT Machine_ID,
       SUM(Alarm) AS Alarm_Count
FROM manufacturing_data
GROUP BY Machine_ID
ORDER BY Alarm_Count DESC;


-- Q5. Parts produced on a selected day (change the two dates)
-- Half-open range: every minute of the day is counted exactly once
-- and the index on Timestamp can be used.
-- Per machine:
SELECT Machine_ID,
       SUM(Production_Count) AS Parts_On_Day
FROM manufacturing_data
WHERE Timestamp >= '2026-10-26 00:00:00'
  AND Timestamp <  '2026-10-27 00:00:00'
GROUP BY Machine_ID
ORDER BY Parts_On_Day DESC, Machine_ID;

-- Plant-wide total for the same day:
SELECT SUM(Production_Count) AS Total_Parts_On_Day
FROM manufacturing_data
WHERE Timestamp >= '2026-10-26 00:00:00'
  AND Timestamp <  '2026-10-27 00:00:00';


-- Q6. Running duration per machine (each Running row = one minute)
SELECT Machine_ID,
       COUNT(*)                   AS Running_Minutes,
       ROUND(COUNT(*) / 60.0, 2)  AS Running_Hours
FROM manufacturing_data
WHERE Machine_Status = 'Running'
GROUP BY Machine_ID
ORDER BY Running_Minutes DESC;


-- Q7. Average RPM during running conditions
-- Overall:
SELECT ROUND(AVG(RPM), 1) AS Avg_RPM_Running
FROM manufacturing_data
WHERE Machine_Status = 'Running';

-- Per machine:
SELECT Machine_ID,
       ROUND(AVG(RPM), 1) AS Avg_RPM_Running
FROM manufacturing_data
WHERE Machine_Status = 'Running'
GROUP BY Machine_ID
ORDER BY Machine_ID;


-- Q8. Machine with the highest rejection rate
-- Production_Count includes rejected parts, so rate = rejected / produced.
WITH rates AS (
    SELECT Machine_ID,
           SUM(Rejected_Count)   AS Total_Rejected,
           SUM(Production_Count) AS Total_Produced,
           100.0 * SUM(Rejected_Count) / SUM(Production_Count)
                                 AS Rate_Raw
    FROM manufacturing_data
    GROUP BY Machine_ID
    HAVING SUM(Production_Count) > 0
), ranked AS (
    SELECT *, RANK() OVER (ORDER BY Rate_Raw DESC) AS rnk
    FROM rates
)
SELECT Machine_ID, Total_Rejected, Total_Produced,
       ROUND(Rate_Raw, 2) AS Rejection_Rate_Pct
FROM ranked
WHERE rnk = 1;
