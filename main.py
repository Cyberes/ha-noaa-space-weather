import logging
import os
import sys
import time

import numpy as np
import paho.mqtt.client as mqtt

from lib.cddis_fetch import fetch_latest_ionex
from lib.tecmap import get_tecmaps, plot_tec_map

logging.basicConfig(level=logging.INFO)

MQTT_BROKER_HOST = os.getenv('MQTT_BROKER_HOST', "")
MQTT_BROKER_PORT = int(os.getenv('MQTT_BROKER_PORT', 1883))
MQTT_CLIENT_ID = os.getenv('MQTT_CLIENT_ID', "space_weather")
MQTT_USERNAME = os.getenv('MQTT_USERNAME', "")
MQTT_PASSWORD = os.getenv('MQTT_PASSWORD', "")
MQTT_TOPIC_PREFIX = os.getenv('MQTT_TOPIC_PREFIX', "space-weather")

LAT_RANGE_MIN = os.getenv('LAT_RANGE_MIN')
LAT_RANGE_MAX = os.getenv('LAT_RANGE_MAX')
LON_RANGE_MIN = os.getenv('LON_RANGE_MIN')
LON_RANGE_MAX = os.getenv('LON_RANGE_MAX')
if not LAT_RANGE_MIN or not LAT_RANGE_MAX or not LON_RANGE_MIN or not LON_RANGE_MAX:
    logging.critical('Must set LAT_RANGE_MIN, LAT_RANGE_MAX, LON_RANGE_MIN, and LON_RANGE_MAX environment variables')
    sys.exit(1)

CDDIS_USERNAME = os.getenv('CDDIS_USERNAME')
CDDIS_PASSWORD = os.getenv('CDDIS_PASSWORD')
if not CDDIS_USERNAME or not CDDIS_PASSWORD:
    logging.critical('Must set CDDIS_USERNAME and CDDIS_PASSWORD environment variables')
    sys.exit(1)

client = mqtt.Client(client_id=MQTT_CLIENT_ID)
if MQTT_USERNAME and MQTT_PASSWORD:
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    logging.info("Username and password set.")
client.will_set(MQTT_TOPIC_PREFIX + "/status", payload="Offline", qos=1, retain=True)  # set LWT
client.connect(MQTT_BROKER_HOST, port=MQTT_BROKER_PORT)
client.loop_start()


def publish(topic: str, msg):
    topic_expanded = MQTT_TOPIC_PREFIX + '/' + topic
    result = client.publish(topic_expanded, msg)
    status = result[0]
    if status == 0:
        logging.info(f"Sent {msg} to topic {topic_expanded}")
    else:
        logging.error(f"Failed to send message to topic {topic_expanded}")


def main():
    while True:
        logging.info('Fetching latest IONEX data')
        ionex_data = fetch_latest_ionex(CDDIS_USERNAME, CDDIS_PASSWORD)
        tec_data = []
        for tecmap, epoch in get_tecmaps(ionex_data):
            avg_tec = np.mean(plot_tec_map(tecmap, [float(LON_RANGE_MIN), float(LON_RANGE_MAX)], [float(LAT_RANGE_MIN), float(LAT_RANGE_MAX)]))
            tec_data.append(avg_tec)
        daily_avg = round(np.mean(tec_data), 1)
        publish('vtec', daily_avg)
        time.sleep(1800)


if __name__ == '__main__':
    main()
