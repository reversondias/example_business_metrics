import os
import json
from influxdb import InfluxDBClient
from celery_config import send_influxdb

@send_influxdb.task
def send_metrics(dict_metric,metric_name="app_metrics"):

    INFLUXDB_PORT = os.getenv('INFLUXDB_PORT')
    INFLUXDB_HOST = os.getenv('INFLUXDB_HOST',"8086")

    value_rder_metric = dict_metric['valueOrder'].replace("$","")

    metric = [{"measurement": metric_name,
                "tags":{
                    "order_id": dict_metric["orderId"],
                    "status_order": str(dict_metric['statusOrder']).lower(),
                    "state": dict_metric['state'],
                    "country": dict_metric['country'],
                    "status_code": str(dict_metric['statusCode'])
                },
                "fields": {
                    "value_order": float(value_rder_metric.replace(",",""))
                }}]

    client = InfluxDBClient(host=INFLUXDB_HOST, port=int(INFLUXDB_PORT))
    client.create_database('metrics')
    client.switch_database('metrics')
    client.write_points(metric)

    print(json.dumps(metric))