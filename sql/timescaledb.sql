-- config for tracking the number of vehicles parked per zone.
CREATE TABLE stats_number_of_vehicles_parked (
  time TIMESTAMPTZ NOT NULL,
  zone_id INTEGER NOT NULL,
  system_id VARCHAR(30) NOT NULL,
  modality VARCHAR(20) NOT NULL,
  number_of_vehicles_parked INT NOT NULL
);

SELECT create_hypertable('stats_number_of_vehicles_parked', 'time');

CREATE INDEX stats_number_of_vehicles_parked__zone_id__system_id__modality__time_idx 
ON stats_number_of_vehicles_parked (zone_id, system_id, modality, time DESC);

ALTER TABLE stats_number_of_vehicles_parked SET (
  timescaledb.compress,
  timescaledb.compress_orderby = 'time DESC',
  timescaledb.compress_segmentby = 'zone_id,system_id,modality'
);

SELECT add_compression_policy('stats_number_of_vehicles_parked', INTERVAL '2 days');


-- config for tracking the number of vehicles departing and arriving on a certain location
CREATE TABLE stats_number_of_trips (
  time TIMESTAMP NOT NULL,
  zone_id INTEGER NOT NULL,
  system_id VARCHAR(30) NOT NULL,
  modality VARCHAR(20) NOT NULL,
  number_of_trips_started INT NOT NULL,
  number_of_trips_ended INT NOT NULL
);

SELECT create_hypertable('stats_number_of_trips', 'time');

CREATE INDEX stats_number_of_trips__zone_id__system_id__modality__time_idx 
ON stats_number_of_trips (zone_id, system_id, modality, time DESC);

ALTER TABLE stats_number_of_trips SET (
  timescaledb.compress,
  timescaledb.compress_orderby = 'time DESC',
  timescaledb.compress_segmentby = 'zone_id,system_id,modality'
);

SELECT add_compression_policy('stats_number_of_trips', INTERVAL '2 days');