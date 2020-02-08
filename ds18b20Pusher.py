#!/usr/bin/env python
import pika
import sys
from threading import Thread
import threading
import time
import logging
import os

w1Devices = []
rabbitMqHost = os.environ['RABBIT_MQ_HOST']
rabbitMqExchange = os.environ['RABBIT_MQ_EXCHANGE']
connection = pika.BlockingConnection


def checkDevices():
    ct = threading.currentThread()
    while getattr(ct, "do_checking", True):
        logging.info("Checking for new One Wire Devices...")
        global w1Devices
        w1Devices = []
        try:
            listOfFiles = os.listdir('/sys/bus/w1/devices')
            for entry in listOfFiles:
                if entry != "w1_bus_master1":
                    logging.info("Found Device :" + entry)
                    w1Devices.append(entry)
        except Exception as e:
            logging.error(
                "Error while try to get OneWire Device List:" + str(e))
        finally:
            logging.info("Check for new Sensors in 10 Minutes...")
            time.sleep(600)


def openConnection():
    global connection
    global rabbitMqHost
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=rabbitMqHost))


def closeConnection():
    global connection
    connection.close


def getTemp(channel):
    global w1Devices
    global rabbitMqExchange
    if len(w1Devices) == 0:
        logging.info("Sorry, no Sensors found :-(")
    try:
        for device in w1Devices:
            # 1-wire Slave Datei lesen
            file = open('/sys/bus/w1/devices/' + device + '/w1_slave')
            filecontent = file.read()
            file.close()
            # Temperaturwerte auslesen und konvertieren
            stringvalue = filecontent.split("\n")[1].split(" ")[9]
            temp = float(stringvalue[2:]) / 1000
            # Temperatur ausgeben
            temp = '%6.2f' % temp
            channel.basic_publish(
                exchange=rabbitMqExchange, routing_key=device, body=temp)
            logging.info("Publish Temp " + temp + " from Sensor:" + device)
    except Exception as e:
        logging.error("Error while Readding OneWireDevices" + str(e))
        time.sleep(1000)


def main():
    logging.basicConfig(level=logging.INFO)
    logging.info("---------------------------------------------")
    logging.info('Started')
    # -
    checkDevicesThread = Thread(target=checkDevices)
    checkDevicesThread.join
    checkDevicesThread.daemon = True
    checkDevicesThread.start()
    # -
    openConnection()
    channel = connection.channel()

    logging.info("Start Reading from Sensor in 10 Seconds...")
    time.sleep(10)
    while True:
        getTemp(channel)
        time.sleep(8)

    logging.info('Finished')
    closeConnection()
    logging.info("---------------------------------------------")


if __name__ == '__main__':
    try:
        main()
    except:
        logging.info("---------------------------------------------")
        logging.info("-- CRITICAL ERROR OCCURED...")
        logging.info("---------------------------------------------")
        time.sleep(5)
        sys.exit(2)
