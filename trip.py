from geojson_pydantic import Point
from pydantic import BaseModel
from typing import Dict

class TripLocation(BaseModel):
    trip_id: str
    system_id: str
    form_factor: str
    location: Point
    is_start_location: bool

def convert_records(rows, is_start_location):
    trips = []
    for row in rows:
        trips.append(
            TripLocation(
                trip_id=row["trip_id"],
                system_id=row["system_id"],
                form_factor=row["form_factor"],
                location=row["location"],
                is_start_location=is_start_location
            )
        )
    return trips

