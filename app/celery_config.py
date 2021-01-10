from celery import Celery
import os

REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT","6379")
REDIS_DB = os.getenv("REDIS_DB","0")

send_influxdb = Celery('celery_config', broker='redis://'+REDIS_HOST+':'+REDIS_PORT+'/'+REDIS_DB, include=['worker'])