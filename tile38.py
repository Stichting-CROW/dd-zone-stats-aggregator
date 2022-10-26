import asyncio
from tile38_helper import tile38_helper
from geojson_pydantic import Feature, Polygon

async def get_vehicles(area):
    with tile38_helper.get_resource() as tile38:
        if type(area.geometry) is Polygon: 
            response = await tile38.within("vehicles").object(area.geometry).asObjects()
            return response
