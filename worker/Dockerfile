FROM python:3.8.2

WORKDIR /root/app

COPY celery_config.py .
COPY worker.py .
COPY requirements.txt .

RUN pip3.8 install -r requirements.txt
RUN apt-get update && apt-get install -y vim telnet && apt-get clean all && rm -vrf /var/cache/apt/

CMD celery -A celery_config worker -c 5