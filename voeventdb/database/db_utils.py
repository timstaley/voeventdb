from __future__ import absolute_import

import sqlalchemy
from sqlalchemy.exc import OperationalError


def check_database_exists(db_url):
    engine = sqlalchemy.create_engine(db_url)
    try:
        conn = engine.connect()
        conn.execute("select 1").scalar()
        conn.close()
        return True
    except OperationalError:
        return False
    finally:
        engine.dispose()

def create_database(admin_db_url, new_db_name):
    engine = sqlalchemy.create_engine(admin_db_url)
    conn = engine.connect()
    conn.execute('commit')
    conn.execute('create database "{}"'.format(new_db_name))
    conn.close()
    engine.dispose()
    
    
def delete_database(admin_db_url, drop_db_name):
    engine = sqlalchemy.create_engine(admin_db_url)
    conn = engine.connect()
    conn.execute('commit')
    conn.execute('drop database "{}"'.format(drop_db_name))
    conn.close()
    engine.dispose()




