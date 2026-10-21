-- Schema migration for activity history
CREATE INDEX IF NOT EXISTS idx_activity_ts ON activity_log(timestamp);
CREATE INDEX IF NOT EXISTS idx_scanned_cat ON scanned_files(category);
