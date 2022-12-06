import db
import timescale_db
from datetime import datetime, timezone, timedelta
import tile38
import asyncio
from redis_helper import redis_helper
from pydantic import BaseModel
import time
import sys
import util
import trip

# Every 5 minutes: update
async def start_updating():
    while True:
        start_time = round(time.time() * 1000)
        await update()
        end_time = round(time.time() * 1000)
        duration = end_time - start_time
        duration_in_secs = duration / 1000.0
        print("Updating stops took", duration, "ms")
        time_to_sleep = 60*5
        if  duration_in_secs / 1000.0 > time_to_sleep:
            time_to_sleep -= duration_in_secs
        time.sleep(time_to_sleep)

def prepare_value_number_of_vehicles_parked(timestamp, zone_id, provider, mode, mode_count):
    time = timestamp
    zone_id = zone_id
    system_id = provider
    modality = mode
    number_of_vehicles_parked = mode_count
    return f"('{time}', {zone_id}, '{system_id}', '{modality}', {number_of_vehicles_parked})"

def get_zone_stat_insert_string_number_of_vehicles_parked(zone_id, zone_stats, timestamp):
    all_insert_commands = []
    # Loop all providers
    for provider in zone_stats.keys():
        # Loop all modes
        for mode, mode_count in zone_stats[provider].items():
            # For every provider/mode combination: Create insert command
            values_string = prepare_value_number_of_vehicles_parked(timestamp, zone_id, provider, mode, mode_count)
            all_insert_commands.append(values_string)

    return all_insert_commands

async def update():
    start_time = time.time()

    # Get all zones
    zones = db.get_all_zones_from_db()
    # Get timestamp of moment of count
    timestamp = datetime.now(timezone.utc)
    rounded_timestamp = util.five_minute_floorer(timestamp - timedelta(hours=0, minutes=30)) 

    await import_trips_in_tile38(rounded_timestamp)
    
    #print(len(db.get_all_trips_that_started_a_hour_ago()))
    print(f"Loading zones from database took {time.time() - start_time}s")
    trip_results = await tile38.get_trips_per_area(zones)
    count_and_store_trip_stats(trip_results, zones, rounded_timestamp)

    start_measurement = datetime.now(timezone.utc)
    result = await tile38.get_vehicles_per_area(zones)
    count_and_store_vehicles_stats(result, zones=zones, timestamp=start_measurement)

async def import_trips_in_tile38(timestamp):
    trip_locations = []
    start_locations_trips = db.get_all_trips_that_started_at_timestamp(timestamp)
    trip_locations.extend(trip.convert_records(start_locations_trips, is_start_location=True))
    end_locations_trips = db.get_all_trips_that_ended_at_timestamp(timestamp)
    
    trip_locations.extend(trip.convert_records(end_locations_trips, is_start_location=False))
    await tile38.insert_trips(trip_locations)

def count_and_store_vehicles_stats(vehicles_per_area, zones, timestamp):
    # Get all vehicles for all zones
    if len(vehicles_per_area) < 1:
        print("NO VEHICLES counted.")
        return

    # INSERT string
    insert_values = []

    # Count modes
    for index, x in enumerate(vehicles_per_area):
        vehicles_in_zone = x[1]
        count_per_zone = count_modes_per_operator(vehicles=vehicles_in_zone)
        zone_id = zones[index].zone_id

        # Insert into database
        # voor elke zone en system Id en modality: insert
        zone_stat_insert_commands = get_zone_stat_insert_string_number_of_vehicles_parked(zone_id, count_per_zone, timestamp)
        insert_values.extend(zone_stat_insert_commands)

    if len(insert_values) <= 0:
        return

    #Create INSERT query
    query = f"""INSERT INTO stats_number_of_vehicles_parked
      VALUES {','.join(insert_values)}
    """

    # Execute INSERT query
    timescale_db.execute(query)

def count_and_store_trip_stats(trip_results, zones, timestamp):
    insert_values = []
    for index, zone in enumerate(zones):
        started_trips = trip_results[index * 2][1]
        ended_trips = trip_results[index * 2 + 1][1]

        number_of_starting_trips_per_zone = count_modes_per_operator(vehicles=started_trips)
        number_of_ending_trips_per_zone = count_modes_per_operator(vehicles=ended_trips)
        
        zone_stat_insert_commands = get_zone_stat_insert_string_number_of_trips(
            zone.zone_id, 
            number_of_starting_trips_per_zone, 
            number_of_ending_trips_per_zone, 
            timestamp
        )
        insert_values.extend(zone_stat_insert_commands)
    
    if len(insert_values) <= 0:
        return

    # Delete trips on timestamp to prevent double values in stats.
    timescale_db.delete_trip_stats_on_timestamp(timestamp=timestamp)

    # Create INSERT query
    query = f"""INSERT INTO stats_number_of_trips
      VALUES {','.join(insert_values)}
    """

    # Execute INSERT query
    timescale_db.execute(query)


    # for index, x in enumerate(result):
    #     vehicles_in_zone = x[1]
    #     count_per_zone = count_modes_per_operator(vehicles=vehicles_in_zone)
    #     zone_id = zones[index].zone_id

    #     # Insert into database
    #     # voor elke zone en system Id en modality: insert
    #     zone_stat_insert_commands = get_zone_stat_insert_string(zone_id, count_per_zone, timestamp)
    #     if len(zone_stat_insert_commands) > 0:
    #         insert_values.extend(zone_stat_insert_commands)

def prepare_value_number_of_trips(timestamp, zone_id, provider, mode, number_of_trips_started, number_of_trips_ended):
    time = timestamp
    zone_id = zone_id
    system_id = provider
    modality = mode
    return f"('{time}', {zone_id}, '{system_id}', '{modality}', {number_of_trips_started}, {number_of_trips_ended})"

def get_zone_stat_insert_string_number_of_trips(zone_id, starting_trips_count, ending_trips_count, timestamp):
    all_insert_commands = []
    # Loop all providers
    providers = set(list(starting_trips_count.keys()) + list(ending_trips_count.keys()))
    for provider in providers:
        starting_trips_counts_per_provider = None
        if provider in starting_trips_count:
            starting_trips_counts_per_provider = starting_trips_count[provider]
        ending_trips_counts_per_provider = None
        if provider in ending_trips_count:
            ending_trips_counts_per_provider = ending_trips_count[provider]
        modes_to_loop = starting_trips_counts_per_provider.keys() if provider in starting_trips_count else ending_trips_counts_per_provider.keys()    

        # Loop all modes
        for mode in modes_to_loop:
            number_of_starting_trips = 0
            number_of_ending_trips = 0
            if starting_trips_counts_per_provider:
                number_of_starting_trips = starting_trips_counts_per_provider[mode]
            if ending_trips_counts_per_provider:
                number_of_ending_trips = ending_trips_counts_per_provider[mode]

            # For every provider/mode combination: Create insert command
            values_string = prepare_value_number_of_trips(
                timestamp, zone_id, provider, mode, number_of_starting_trips, number_of_ending_trips)
            all_insert_commands.append(values_string)
    return all_insert_commands

def count_modes_per_operator(vehicles):
    # Create dict with amount of vehicles per operator
    modes_per_operator = {}
    for vehicle in vehicles:
        vehicleId = vehicle[0].decode('UTF-8');

        operatorId = vehicleId.split(":")[0];
        # If operator key does not exist: create one
        if operatorId not in modes_per_operator:
            modes_per_operator[operatorId] = {
                "moped": 0,
                "cargo_bicycle": 0,
                "bicycle": 0,
                "car": 0,
                "other": 0
            }
        mode = vehicleId.split(":")[2]
        # Increment counter for this vehicle mode
        if mode in modes_per_operator[operatorId]:
            modes_per_operator[operatorId][mode] += 1
        else:
            modes_per_operator[operatorId]["other"] += 1
    # Return
    return modes_per_operator


asyncio.run(start_updating())

# Todo
# 1. Count per start en eind!
# 2. Insert in DB
# 3. voeg samen met bestaande code.
# 4. Voeg logica toe om lege gaten op te vullen. 
"""
 SELECT count(*)
FROM generate_series
        ( '2022-07-01'::timestamp 
        , NOW()
        , '5 minute'::interval) dd
;
"""

# 5. schrijf query. 