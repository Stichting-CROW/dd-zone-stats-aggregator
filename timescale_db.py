from db_helper import timescale_db_helper

def execute(stmt):
    with timescale_db_helper.get_resource() as (cur, conn):
        try:
            cur.execute(stmt)
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(e)

