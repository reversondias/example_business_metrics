FROM python:3.8.2

WORKDIR /root/app

COPY list_1.json .
COPY list_2.json .
COPY main.py .
COPY requirements.txt .

RUN pip3.8 install -r requirements.txt
RUN apt-get update && apt-get install -y vim telnet && apt-get clean all && rm -vrf /var/cache/apt/

CMD python3.8 main.py