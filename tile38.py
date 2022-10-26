import asyncio
from tile38_helper import tile38_helper
from geojson_pydantic import Feature, Polygon
import time

async def get_vehicles_per_area(zones):
    with tile38_helper.get_resource() as tile38_client:
        print(len(zones))
        for i in range(0, len(zones), 100):
            print(i)
            get_per_thousand(tile38_client, zones[i:i + 100])
        

def get_per_thousand(tile38_client, zones):
    start_time = time.time()
    pipe = tile38_client.pipeline(transaction=False)
    for zone in zones:
        if type(zone.area.geometry) is Polygon:
            pipe.execute_command('WITHIN', 'vehicles', 'OBJECT', zone.area.geometry.json())
    pipe.execute()
    print(f"Tile38 took {time.time() - start_time}s")
    return 
