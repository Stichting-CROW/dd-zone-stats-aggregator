import db
import timescale_db
from datetime import datetime
import tile38
import asyncio
from redis_helper import redis_helper
from pydantic import BaseModel
import time
import sys

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

def prepare_value(timestamp, zone_id, provider, mode, mode_count):
    time = timestamp
    zone_id = zone_id
    system_id = provider
    modality = mode
    number_of_vehicles_parked = mode_count
    print(f"({time}, {zone_id}, {system_id}, {modality}, {number_of_vehicles_parked})")
    return f"('{time}', {zone_id}, '{system_id}', '{modality}', {number_of_vehicles_parked})"

def get_zone_stat_insert_string(zone_id, zone_stats, timestamp):
    all_insert_commands = []
    # Loop all providers
    for provider in zone_stats.keys():
        # Loop all modes
        for mode, mode_count in zone_stats[provider].items():
            # For every provider/mode combination: Create insert command
            values_string = prepare_value(timestamp, zone_id, provider, mode, mode_count)
            all_insert_commands.append(values_string)

    return all_insert_commands

async def update():
    start_time = time.time()

    # Get all zones
    zones = db.get_all_zones_from_db()
    sys.getsizeof(zones)
    print(f"Loading zones from database took {time.time() - start_time}s")

    # Get timestamp of moment of count
    timestamp = datetime.now().isoformat()

    # Get all vehicles for all zones
    result = await tile38.get_vehicles_per_area(zones)
    if result == None:
        return

    # INSERT string
    insert_values = []

    # Count modes
    for index, x in enumerate(result):
        vehicles_in_zone = x[1]
        count_per_zone = count_modes_per_operator(vehicles=vehicles_in_zone)
        zone_id = zones[index].zone_id

        # Insert into database
        # voor elke zone en system Id en modality: insert
        zone_stat_insert_commands = get_zone_stat_insert_string(zone_id, count_per_zone, timestamp)
        if len(zone_stat_insert_commands) > 0:
            insert_values.extend(zone_stat_insert_commands)

    print("INSERT VALUES")
    print(insert_values)

    if len(insert_values) <= 0:
        return

    # Create INSERT query
    query = f"""INSERT INTO stats_number_of_vehicles_parked
      VALUES {','.join(insert_values)}
    """

    # Execute INSERT query
    timescale_db.execute(query)

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