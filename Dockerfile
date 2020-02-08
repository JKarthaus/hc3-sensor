FROM seblucas/alpine-python3

WORKDIR /usr/src/app

RUN pip install --no-cache-dir pika

COPY ds18b20Pusher.py ./

CMD [ "python3", "./ds18b20Pusher.py" ]
