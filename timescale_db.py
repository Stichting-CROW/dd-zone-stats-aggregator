from db_helper import timescale_db_helper

def execute(stmt):
    with timescale_db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)

def delete_trip_stats_on_timestamp(timestamp):
    with timescale_db_helper.get_resource() as (cur, conn):
        try:
            stmt = """
                DELETE 
                FROM stats_number_of_trips 
                WHERE time = %s
            """
            cur.execute(stmt, (timestamp,))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)

