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
            'geometry',   ST_AsGeoJSON( ST_Buffer(ST_GeometryN(area, 1)::geography, 30))::json,
            'properties',  json_build_object()
        ) as area, municipality
        FROM zones
        WHERE zone_type IN ('custom');
    """
    cur.execute(stmt)
    return cur.fetchall()

def get_all_trips_that_started_at_timestamp(timestamp):
    with db_helper.get_resource() as (cur, conn):
        try:
            stmt = """
                SELECT trips.trip_id, trips.system_id, 
                ST_AsGeoJSON(trips.start_location)::json as location, 
                form_factor 
                FROM trips 
                JOIN vehicle_type 
                USING (vehicle_type_id) 
                WHERE start_time >= %(timestamp)s 
                AND start_time <= %(timestamp)s + '5 MINUTES';
            """
            cur.execute(stmt, {"timestamp": timestamp})
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)


def get_all_trips_that_ended_at_timestamp(timestamp):
    with db_helper.get_resource() as (cur, conn):
        try:
            stmt = """
                SELECT trips.trip_id, trips.system_id, 
                ST_AsGeoJSON(trips.end_location)::json as location,
                form_factor 
                FROM trips 
                JOIN vehicle_type 
                USING (vehicle_type_id) 
                WHERE end_time >= %(timestamp)s 
                AND end_time <= %(timestamp)s + '5 MINUTES';
            """
            cur.execute(stmt, {"timestamp": timestamp})
            return cur.fetchall()
        except Exception as e:
            conn.rollback()
            print(e)


def execute(stmt):
    with db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)

def convert_zone(row):
    return zone.Zone(
        zone_id=row["zone_id"],
        area = row["area"]
        # num_vehicles_available: Dict[str, int]
        # num_vehicles_disabled: Dict[str, int]
        # num_places_available: Dict[str, int]
    )


