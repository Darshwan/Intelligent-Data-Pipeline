-- Enable TimescaleDB and PostGIS
CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS postgis;

-- Create Earthquakes Table
CREATE TABLE IF NOT EXISTS earthquakes (
    id TEXT NOT NULL,
    time TIMESTAMPTZ NOT NULL,
    latitude DOUBLE PRECISION NOT NULL,
    longitude DOUBLE PRECISION NOT NULL,
    depth DOUBLE PRECISION,
    magnitude DOUBLE PRECISION,
    place TEXT,
    location GEOMETRY(POINT, 4326),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (id, time)
);

-- Turn into Hypertable partitioned by time
SELECT create_hypertable('earthquakes', 'time', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS ix_earthquakes_location ON earthquakes USING GIST (location);
CREATE INDEX IF NOT EXISTS ix_earthquakes_time ON earthquakes (time DESC);
