import db
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
        print("Updating stops took", end_time - start_time, "ms")
        time.sleep(60*5)

def prepare_value(timestamp, zone_id, provider, mode, mode_count):
    time = timestamp
    zone_id = zone_id
    system_id = provider
    modality = mode
    number_of_vehicles_parked = mode_count
    print(f"({time}, {zone_id}, {system_id}, {modality}, {number_of_vehicles_parked})")
    return f"('{time}', {zone_id}, '{system_id}', '{modality}', {number_of_vehicles_parked})"

def get_zone_stat_insert_string(zone_id, zone_stats, timestamp):
    all_insert_commands = [];
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
        return;

    # Create INSERT query
    query = f"""INSERT INTO stats_number_of_vehicles_parked
      VALUES {','.join(insert_values)}
    """

    # Execute INSERT query
    db.execute(query)

            #print(test)
#             pipe.get("stop:" + stop.stop_id + ":status")
#         res = pipe.execute()

#         deltas_states = []
#         # Determine new state.
#         for index, stop in enumerate(stops):
#             print(stop.stop_id)
#             old_state = res[index]
#             if old_state == None:
#                 old_state = get_initial_state(stop.capacity)
#             else:
#                 old_state = json.loads(res[index])
#             print("OLD")
#             print(old_state)
#             new_state = calculate_available_places(stop.capacity, stop.num_vehicles_available, stop.status)
#             print("NEW")
#             print(new_state)
#             new_state = check_flippering(new_state=new_state, old_state=old_state, capacity=stop.capacity)
            
#             is_returning = check_if_any_place_is_available(new_state)
#             stop.status["is_returning"] = is_returning
#             stop.num_places_available = new_state
#             print(stops[index].num_places_available)
            
#             state_change = get_state_changes(stop, old_state, new_state)
#             if state_change:
#                 deltas_states.append(state_change)

#         print(deltas_states)
#         store_stops(r, stops)
#         notifications.send_notifications(deltas_states)
        

# def store_stops(r, stops):
#     pipe = r.pipeline()

#     pipe.set("stops_last_updated", round(time.time() * 1000))
#     municipalities = {}

#     # Delete previous et.
#     pipe.delete("all_stops")
#     for stop in stops:
#         pipe.setex("stop:" + stop.stop_id, 300, stop.json())
#         pipe.setex("stop:" + stop.stop_id + ":status", 3600 * 24, json.dumps(stop.num_places_available))
#         pipe.sadd("all_stops", stop.stop_id)
#         # Remove set before updating it with new values.
#         key_stops_per_municipality = "stops_per_municipality:" + stop.municipality
#         # Remove existing data to replace it with new data.
#         if stop.municipality not in municipalities:
#             pipe.delete(key_stops_per_municipality)
#             municipalities[stop.municipality] = True
#         pipe.sadd(key_stops_per_municipality, stop.stop_id)
#         pipe.expire(key_stops_per_municipality, 300)
#     pipe.execute()

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

# def calculate_available_places(capacity, counted_vehicles, status):
#     if "is_returning" in status and status["is_returning"] == False:
#         return {
#             "moped": 0,
#             "cargo_bicycle": 0,
#             "bicycle": 0,
#             "car": 0,
#             "other": 0
#         }
#     # When a zone is manually opened, the available places are 'infinite', of course there is a capacity but a zone will not be closed after reaching this capacity.
#     if "control_automatic" in status and status["control_automatic"] == False: 
#         return return_available_places_for_zone_that_is_always_open(capacity)
#     if "combined" in capacity:
#         return calculate_places_available_combined(capacity["combined"], counted_vehicles)
#     return calculate_places_available_per_mode(capacity, counted_vehicles)

# def return_available_places_for_zone_that_is_always_open(capacity):
#     # Default for The Hague for now.
#     if "combined" in capacity: 
#         return {
#             "moped": 9999,
#             "cargo_bicycle": 9999,
#             "bicycle": 9999,
#             "car": 0,
#             "other": 9999
#         }
#     places_available = {
#         "moped": 0,
#         "cargo_bicycle": 0,
#         "bicycle": 0,
#         "car": 0,
#         "other": 0
#     }
#     for k, v in capacity.items():
#         if v > 0:
#             places_available[k] = 9999
#     return places_available

# def calculate_places_available_per_mode(capacity, counted_vehicles):
#     print("CHECK")
#     places_available = {
#         "moped": 0,
#         "cargo_bicycle": 0,
#         "bicycle": 0,
#         "car": 0,
#         "other": 0
#     }
#     # Add other temporarily to moped as long gosharing is not delivering correct data.
#     if "other" in counted_vehicles:
#         counted_vehicles["moped"] += counted_vehicles["other"]
#     for mode, vehicles_capacity in capacity.items():
#         if mode == "combined":
#             continue
#         elif mode not in counted_vehicles:
#             places_available[mode] = vehicles_capacity
#         else:
#             places_available[mode] = max(vehicles_capacity - counted_vehicles[mode], 0)
#     return places_available

# def calculate_places_available_combined(combined_capacitiy, counted_vehicles):
#     total = 0
#     modes_to_include_in_combined = ["moped", "cargo_bicycle", "bicycle", "other"]
#     for mode in modes_to_include_in_combined:
#         if mode in counted_vehicles:
#             total += counted_vehicles[mode]
    
#     places_available = {
#         "moped": 0,
#         "cargo_bicycle": 0,
#         "bicycle": 0,
#         "car": 0,
#         "other": 0
#     }
#     if total >= combined_capacitiy:
#         return places_available

#     available_space = combined_capacitiy - total
#     for mode in modes_to_include_in_combined:
#         places_available[mode] = available_space
                
#     return places_available


# def get_current_vehicles():
#     pass

# def get_initial_state(capacity):
#     state_per_mode = {
#         "moped": -1,
#         "cargo_bicycle": -1,
#         "bicycle": -1,
#         "car": -1,
#         "other": -1
#     }
#     for key, value in capacity.items():
#         if key in state_per_mode and value == 0:
#             state_per_mode[key] = 0
#         if key == "combined" and value == 0:
#             return {
#                 "moped": 0,
#                 "cargo_bicycle": 0,
#                 "bicycle": 0,
#                 "car": 0,
#                 "other": 0
#             }
#     return state_per_mode



# # A zone should only be opened if number of vehicles < x% (start with 95)
# def check_flippering(new_state, old_state, capacity):
#     if "combined" in capacity:
#         return check_flippering_combined(new_state=new_state, old_state=old_state, capacity=capacity["combined"])
#     return check_flippering_per_mode(new_state=new_state, old_state=old_state, capacity=capacity)

# def check_flippering_per_mode(new_state, old_state, capacity):
#     for mode, value in new_state.items():
#         if value > 0 and mode in old_state and old_state[mode] == 0 and mode in capacity and value < 0.05 * capacity[mode]:
#             print("Anti-flipper for mode", mode)
#             new_state[mode] = 0
#     return new_state

# def check_flippering_combined(new_state, old_state, capacity):
#     old_places_available = sum(old_state.values())
#     if old_places_available > 0:
#         return new_state
#     # moped is arbitrary in this situation, when a combined capacity is setted every mode can be used.
#     new_places_available = new_state["moped"]
#     if new_places_available < 0.05 * capacity:
#         return {
#             "moped": 0,
#             "cargo_bicycle": 0,
#             "bicycle": 0,
#             "car": 0,
#             "other": 0
#         }
#     return new_state

# class StateChange(BaseModel):
#     stop: stop.MdsStop
#     opened: list[str] = []
#     closed: list[str] = []

# def get_state_changes(stop, old_state, new_state):
#     state_changes = StateChange(stop=stop)
#     for mode, old_value in old_state.items():
#         new_value = new_state[mode]
#         if mode not in new_state:
#             state_changes.closed.append(mode)
#         elif old_value > 0 and new_value == 0:
#             state_changes.closed.append(mode)
#         elif old_value == 0 and new_value > 0:
#             state_changes.opened.append(mode)
#     new_modes = set(new_state.keys()) - set(old_state.keys())
#     for new_mode in new_modes:
#         if new_state[new_mode] > 0:
#             state_changes.opened.append(new_mode)
#     if not state_changes.closed and not state_changes.opened:
#         return None
#     return state_changes

# def check_if_any_place_is_available(available_places):
#     for _, value in available_places.items():
#         if value > 0:
#             return True
#     return False

asyncio.run(start_updating())
  


#  select st_asgeojson(st_buffer(area::geography, 10)) from zones where zone_id = 51297;

# Haal alle park stops op:
#
# SELECT stop_id, stops.name, ST_X(location) as stop_lng, ST_Y(location) stop_lat, capacity, stops.geography_id, ST_AsGeoJSON(
#     ST_Buffer(area::geography, 10)
# ) as area
# FROM geographies
# JOIN zones
# USING (zone_id) 
# JOIN stops
# USING (geography_id);
# # Bepaal per stop hoeveel voertuigen er in die zone staan.
# tile38 trucje

# Haal per stop op wat de vorige status was.  
# Wanneer het aantal voertuigen in de stop >= capaciteit sluit stop.
# 1. combined.
# 2. per modaliteit.
# Wanneer hub gesloten en het aantal voertuigen in de stop < 0.95 * capaciteit open hub.

# Wanneer status hub veranderd, stuur email.

# Sla stop opbject op in redis met alle logische parameters. 
# Sla stopId op in list van stops per gemeente en landelijk. 
