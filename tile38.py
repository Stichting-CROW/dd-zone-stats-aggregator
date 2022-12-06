import asyncio
from tile38_helper import tile38_helper
from geojson_pydantic import Feature, Polygon
import time

async def get_vehicles_per_area(zones):
    with tile38_helper.get_resource() as tile38_client:
        result = []
        for i in range(0, len(zones), 100):
            result.extend(
                get_vehicles_per_area_sub(tile38_client, zones[i:i + 100])
            )
        return result
        

def get_vehicles_per_area_sub(tile38_client, zones):
    start_time = time.time()
    pipe = tile38_client.pipeline(transaction=False)
    for zone in zones:
        if type(zone.area.geometry) is Polygon:
            pipe.execute_command('WITHIN', 'vehicles', 'OBJECT', zone.area.geometry.json())
    result = pipe.execute()
    print(f"Tile38 took  {time.time() - start_time}s")
    return result

async def insert_trips(trips):
    with tile38_helper.get_resource() as tile38_client:
        pipe = tile38_client.pipeline(transaction=False)
        pipe.execute_command('DROP', "start_location")
        pipe.execute_command('DROP', "end_location")

        for trip in trips:
            type_of_location = "start_location" if trip.is_start_location else "end_location"
            key = trip.system_id + ":" + trip.trip_id + ":" + trip.form_factor
            coordinates = trip.location.coordinates
            pipe.execute_command('SET', type_of_location, key, 'POINT', coordinates[1], coordinates[0])
    pipe.execute()

async def get_trips_per_area(zones):
    with tile38_helper.get_resource() as tile38_client:
        result = []
        for i in range(0, len(zones), 100):
            result.extend(
                get_trips_per_area_sub(tile38_client, zones[i:i + 100])
            )
        return result

def get_trips_per_area_sub(tile38_client, zones):
    start_time = time.time()
    pipe = tile38_client.pipeline(transaction=False)
    for zone in zones:
        if type(zone.area.geometry) is Polygon:
            pipe.execute_command('WITHIN', 'start_location', 'OBJECT', zone.area.geometry.json())
            pipe.execute_command('WITHIN', 'end_location', 'OBJECT', zone.area.geometry.json())
    result = pipe.execute()
    print(f"Tile38 took get_trips_per_area_sub {time.time() - start_time}s")
    return result
