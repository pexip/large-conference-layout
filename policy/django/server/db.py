import os
import logging
import psycopg2
import psycopg2.extras
import json
from typing import Container, Iterable

def get_env(var: str) -> str:
    env = os.environ.get(var, None)
    if not env:
        logging.info(f"client.get_env: Missing " "{var}" " environment variable")
        raise Exception("Missing environment variable")
    return env

def db_open():
    db_user = get_env("POSTGRES_USER")
    db_pw = get_env("POSTGRES_PASSWORD")
    db_name = get_env("POSTGRES_DB")
    
    return psycopg2.connect(f"postgresql://{db_user}:{db_pw}@db:5432/{db_name}")

# Add object to specified container, generate an id if it is not defined
def db_add(table: str, data: dict) -> None:
    db = db_open()
    cursor = db.cursor()
    
    cols = data.keys()
    vals = [json.dumps(data[c]) if type(data[c]) is dict else data[c] for c in cols]
    vals_str_list = ["%s"] * len(vals)
    vals_str = ", ".join(vals_str_list)
    
    try:
        insert_query = f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({vals_str});"
        cursor.execute(insert_query, vals)
        db.commit()
        logging.info(f"{data} added to {table}")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        logging.info(f"Error adding data to database: {error}")
    finally:
        cursor.close()
        db.close()
        
    return


# Update object in specified container, generate an id if it is not defined
def db_update(table: str, data: dict, condition: dict) -> None:
    db = db_open()
    cursor = db.cursor()
    
    cols = data.keys()
    vals = [f"{c} = '{json.dumps(data[c])}'" if type(data[c]) is dict else f"{c} = '{data[c]}'" for c in cols]
    vals_str = ", ".join(vals)

    conds = condition.keys()
    cond_vals = [f"{c} = '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} = '{condition[c]}'" for c in conds]
    cond_vals_str = ", ".join(cond_vals)
    
    try:
        update_query = f"UPDATE {table} SET {vals_str} WHERE {cond_vals_str};"
        cursor.execute(update_query, vals)
        db.commit()
        logging.info(f"{data} modified in {table}")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        logging.info(f"Error modifying data in database: {error}")
    finally:
        cursor.close()
        db.close()
        
    return


# Delete object from specified container
def db_delete(table: str, condition: dict) -> None:
    db = db_open()
    cursor = db.cursor()
    
    conds = condition.keys()
    cond_vals = [f"{c} = '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} = '{condition[c]}'" for c in conds]
    cond_vals_str = ", ".join(cond_vals)
    
    try:
        delete_query = f"DELETE FROM {table} WHERE {cond_vals_str};"
        cursor.execute(delete_query)
        db.commit()
        logging.info(f"{condition} deleted from {table}")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        logging.info(f"Error modifying data in database: {error}")
    finally:
        cursor.close()
        db.close()
        
    return


# Query database to return data from passed SQL query string
def db_query(table: str, condition: dict, regex = False):
    db = db_open()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    conds = condition.keys()
    if not regex:
        cond_vals = [f"{c} = '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} = '{condition[c]}'" for c in conds]
    else:
        cond_vals = [f"{c} ~ '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} ~ '{condition[c]}'" for c in conds]
    cond_vals_str = " AND ".join(cond_vals)
    
    try:
        select_query = f"SELECT * FROM {table} WHERE {cond_vals_str};"
        cursor.execute(select_query)
        results = cursor.fetchall()
        logging.info(f"{condition} searched for in {table}")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        results = []
        logging.info(f"Error querying data in database: {error}")
    finally:
        cursor.close()
        db.close()
        
    return results

# Query database to return count of data from passed SQL query string
def db_count(table: str, condition: dict, column: str, regex=False):
    db = db_open()
    cursor = db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
    
    conds = condition.keys()
    if not regex:
        cond_vals = [f"{c} = '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} = '{condition[c]}'" for c in conds]
    else:
        cond_vals = [f"{c} ~ '{json.dumps(condition[c])}'" if type(condition[c]) is dict else f"{c} ~ '{condition[c]}'" for c in conds]
    cond_vals_str = " AND ".join(cond_vals)
    
    try:
        count_query = f"SELECT {column}, COUNT(*) FROM {table} WHERE {cond_vals_str} GROUP BY {column};"
        cursor.execute(count_query)
        results = cursor.fetchall()
        logging.info(f"{condition} counted in {table}")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        results = []
        logging.info(f"Error counting data in database: {error}")
    finally:
        cursor.close()
        db.close()
        
    return results

# # Delete passed container
def db_clean(table: str) -> None:
    db = db_open()
    cursor = db.cursor()
   
    try:
        delete_table = f"DELETE FROM {table};"
        cursor.execute(delete_table)
        db.commit()
        logging.info(f"{table} table deleted")
    except (Exception, psycopg2.Error) as error:
        db.rollback()
        logging.info(f"Error deleting table {table}: {error}")
    finally:
        cursor.close()
        db.close()
        
    return
