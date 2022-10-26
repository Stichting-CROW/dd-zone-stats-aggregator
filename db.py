from db_helper import db_helper
import zone

def get_all_zones_from_db():
    with db_helper.get_resource() as (cur, conn):
        try:
            rows = query_all_zones(cur)
            return list(map(convert_zone, rows))
        except Exception as e:
            conn.rollback()
            print(e)

def query_all_zones(cur):
    stmt = """
        SELECT zones.zone_id,
        -- Add margin of 10m's to take GPS inaccuracy into account.
        -- changed 10m to 30m as an experiment. 
        -- this 30m should only be added in case of custom zones. 
        json_build_object(
            'type',       'Feature',
            'geometry',   ST_AsGeoJSON( ST_GeometryN(area, 1)::geography)::json,
            'properties',  json_build_object()
        ) as area, municipality
        FROM zones
        WHERE zone_type IN ('municipality', 'residential_area', 'country', 'custom');
    """
    cur.execute(stmt)
    return cur.fetchall()

def convert_zone(row):
    return zone.Zone(
        zone_id=row["zone_id"],
        area = row["area"]
        # num_vehicles_available: Dict[str, int]
        # num_vehicles_disabled: Dict[str, int]
        # num_places_available: Dict[str, int]
    )
