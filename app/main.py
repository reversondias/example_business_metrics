import json
import os
import psycopg2
from psycopg2 import Error
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
from influxdb import InfluxDBClient
from worker import send_metrics

def return_json(path):

    with open(path) as json_file:
        data = json.load(json_file)

    return(data)

def db_create():


    DB_USER = os.getenv('DB_USER')
    DB_PASSWD = os.getenv('DB_PASSWD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT',"5432")

    try:
       connection_db = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
       connection_db.close()
    except (Exception, Error):
        connection_db_create = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT)
        connection_db_create.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor_db_create = connection_db_create.cursor()
        cursor_db_create.execute("CREATE DATABASE "+DB_NAME+";")
        cursor_db_create.close()
        connection_db_create.close()

    try:
        connection_table = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
        cursor_table = connection_table.cursor()
        cursor_table.execute("SELECT * FROM sales LIMIT 1;")
        cursor_table.close()
        connection_table.close()
    except (Exception, Error):
        connection_table_create = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT,database=DB_NAME)
        connection_table_create.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor_table_create = connection_table_create.cursor()
        cursor_table_create.execute("CREATE TABLE sales (id SERIAL PRIMARY KEY, orderId varchar(255), statusOrder boolean, valueOrder varchar(255), clientId varchar(255), clientName varchar(255), state varchar(255), country varchar(255), phoneNumber varchar(255),statusCode int);")
        cursor_table_create.close()
        connection_table_create.close()

def db_register(query):

    
    DB_USER = os.getenv('DB_USER')
    DB_PASSWD = os.getenv('DB_PASSWD')
    DB_NAME = os.getenv('DB_NAME')
    DB_HOST = os.getenv('DB_HOST')
    DB_PORT = os.getenv('DB_PORT',"5432")

    try:
        connection = psycopg2.connect(user=DB_USER, password=DB_PASSWD, host=DB_HOST, port=DB_PORT, database=DB_NAME)
        
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    except (Exception, Error) as error:
        print("Error while connecting to PostgreSQL", error)
    finally:
        if (connection):
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")


def app(path):
    db_create()
    json_data = return_json(path)
    for el in json_data:
        query = "INSERT INTO sales (orderid, statusorder, valueorder, clientid, clientname, state, country, phoneNumber,statusCode) \
VALUES ('"+el['orderId']+"','"+str(el['statusOrder']).lower()+"','"+el['valueOrder']+"','"+el["clientId"]+"','"+el['clientName']+"',\
'"+el['state'].replace("'","")+"','"+el['country'].replace("'","")+"','"+el['phoneNumber']+"','"+str(el['statusCode'])+"');"
        db_register(query)
        send_metrics.delay(el)
        if send_metrics.delay(el) : 
            print("Sent metric to InfluxDB")
        else:
            print("[WARN] It wasn't possible sent metric to InfluxDB!")
        time.sleep(2)


if __name__ == "__main__":
    app("./list_1.json")