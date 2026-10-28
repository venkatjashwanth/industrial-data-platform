-- =====================================================
-- schema.sql  |  Smart factory machine data (MySQL 8.0.16+)
-- One row = one machine reading, logged every minute.
-- Production_Count and Rejected_Count are per-minute increments
-- (not running totals). Production_Count INCLUDES rejected parts.
-- =====================================================

CREATE TABLE manufacturing_data (
    Record_ID        INT AUTO_INCREMENT PRIMARY KEY,
    Machine_ID       VARCHAR(10)  NOT NULL,
    Timestamp        DATETIME     NOT NULL,
    Temperature      DECIMAL(5,2),
    Vibration        DECIMAL(5,2),
    RPM              INT,
    Current          DECIMAL(6,2),
    Production_Count INT NOT NULL DEFAULT 0,
    Rejected_Count   INT NOT NULL DEFAULT 0,
    Machine_Status   VARCHAR(10)  NOT NULL,
    Alarm            TINYINT      NOT NULL DEFAULT 0,

    CONSTRAINT chk_machine_status
        CHECK (Machine_Status IN ('Running', 'Idle', 'Stopped', 'Fault')),
    CONSTRAINT chk_alarm
        CHECK (Alarm IN (0, 1)),
    CONSTRAINT chk_counts
        CHECK (Production_Count >= 0 AND Rejected_Count >= 0
               AND Rejected_Count <= Production_Count)
);

-- Per-machine time-range queries
CREATE INDEX idx_machine_time ON manufacturing_data (Machine_ID, Timestamp);
-- Queries that filter only by date/time (e.g. Q5)
CREATE INDEX idx_time ON manufacturing_data (Timestamp);
