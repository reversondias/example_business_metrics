import json
import os
import psycopg2
from psycopg2 import Error
import time
from influxdb import InfluxDBClient
from worker import send_metrics

def return_json(path):

    with open(path) as json_file:
        data = json.load(json_file)

    return(data)

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