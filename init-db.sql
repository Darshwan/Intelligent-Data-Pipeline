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

-- Create Weather Table
CREATE TABLE IF NOT EXISTS weather_measurements (
    time TIMESTAMPTZ NOT NULL,
    city TEXT NOT NULL,
    temperature DOUBLE PRECISION,
    humidity DOUBLE PRECISION,
    pressure DOUBLE PRECISION,
    condition TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (city, time)
);

-- Turn into Hypertable partitioned by time
SELECT create_hypertable('weather_measurements', 'time', if_not_exists => TRUE);

-- Indexes for Weather
CREATE INDEX IF NOT EXISTS ix_weather_city_time ON weather_measurements (city, time DESC);

-- Create Flood Alerts Table
CREATE TABLE IF NOT EXISTS flood_alerts (
    time TIMESTAMPTZ NOT NULL,
    station TEXT NOT NULL,
    water_level DOUBLE PRECISION,
    warning_level DOUBLE PRECISION,
    danger_level DOUBLE PRECISION,
    status TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (station, time)
);

-- Turn into Hypertable partitioned by time
SELECT create_hypertable('flood_alerts', 'time', if_not_exists => TRUE);

-- Indexes for Flood
CREATE INDEX IF NOT EXISTS ix_flood_station_time ON flood_alerts (station, time DESC);

-- Create Forex Table
CREATE TABLE IF NOT EXISTS forex_rates (
    time TIMESTAMPTZ NOT NULL,
    currency TEXT NOT NULL,
    buy DOUBLE PRECISION,
    sell DOUBLE PRECISION,
    unit INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    PRIMARY KEY (currency, time)
);

-- Turn into Hypertable partitioned by time
SELECT create_hypertable('forex_rates', 'time', if_not_exists => TRUE);

-- Indexes for Forex
CREATE INDEX IF NOT EXISTS ix_forex_currency_time ON forex_rates (currency, time DESC);

-- Metadata & Data Catalog Tables
CREATE TABLE IF NOT EXISTS datasets (
    id SERIAL PRIMARY KEY,
    name TEXT UNIQUE NOT NULL,
    description TEXT,
    schema_version TEXT,
    owner TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS data_quality_logs (
    id SERIAL PRIMARY KEY,
    dataset_name TEXT,
    status TEXT, -- 'PASS', 'FAIL'
    error_details TEXT,
    record_content TEXT,
    timestamp TIMESTAMPTZ DEFAULT NOW()
);

-- Seed Datasets
INSERT INTO datasets (name, description, schema_version, owner) VALUES
('earthquakes', 'USGS Real-time Feeds', 'v1', 'Earthquake Pipeline'),
('weather', 'OpenWeatherMap Cities', 'v1', 'Weather Pipeline'),
('flood_alerts', 'DHM River Levels', 'v1', 'Hydrology Pipeline'),
('forex_rates', 'NRB Exchange Rates', 'v1', 'Forex Pipeline')
ON CONFLICT (name) DO NOTHING;
