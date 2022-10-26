from geojson_pydantic import Feature, Polygon
from pydantic import BaseModel
from typing import Dict

PolygonFeatureModel = Feature
class Zone(BaseModel):
    zone_id: str
    area: PolygonFeatureModel

