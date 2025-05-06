"""
MQTT Producer for Windows
Generates sample data and publishes to a fixed or dynamic MQTT topic
"""

import json
import time
import random
import paho.mqtt.client as mqtt
from datetime import datetime
import os
import signal
from colorama import Fore, Style, init
from dotenv import load_dotenv
from logger import get_mqtt_logger  # Importing the logger from logger.py

# Load environment variables from .env if available
load_dotenv()

# Initialize colorama
init()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_CLIENT_ID = f"windows-producer-{os.getpid()}"
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")
MQTT_FIXED_TOPIC = os.getenv("MQTT_FIXED_TOPIC")  # Optional fixed topic

# Producer Settings
PUBLISH_INTERVAL = int(os.getenv("PUBLISH_INTERVAL", 2))

# Graceful shutdown flag
running = True

# Initialize Logger from logger.py
logger = get_mqtt_logger()  # Use the mqtt_logger defined in logger.py

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logger.info(f"Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
    else:
        logger.error(f"Failed to connect to MQTT broker with code: {rc}")

def on_disconnect(client, userdata, rc):
    if rc != 0:
        logger.warning("! Unexpected disconnection from MQTT broker")
    else:
        logger.info("i Disconnected from MQTT broker")

def on_publish(client, userdata, mid):
    logger.info(f"Message {mid} published successfully")

def generate_sensor_data():
    """Generate test data for either fixed or simulated topics."""
    if MQTT_FIXED_TOPIC:
        topic = MQTT_FIXED_TOPIC
        payload = {
            "device": "test_device",
            "status": "active",
            "value": round(random.uniform(20.0, 30.0), 2),
            "timestamp": datetime.now().isoformat()
        }
    else:
        sensor_type = random.choice(["temperature", "humidity", "pressure", "light"])
        location = random.choice(["living_room", "kitchen", "bedroom", "garage", "outside"])
        topic = f"sensors/{location}/{sensor_type}"

        if sensor_type == "temperature":
            value = round(random.uniform(18.0, 30.0), 1)
            unit = "°C"
        elif sensor_type == "humidity":
            value = round(random.uniform(30.0, 70.0), 1)
            unit = "%"
        elif sensor_type == "pressure":
            value = round(random.uniform(990.0, 1030.0), 1)
            unit = "hPa"
        elif sensor_type == "light":
            value = round(random.uniform(0, 1000), 0)
            unit = "lux"

        payload = {
            "sensor_id": f"{location}_{sensor_type}_1",
            "type": sensor_type,
            "location": location,
            "value": value,
            "unit": unit,
            "timestamp": datetime.now().isoformat()
        }

    return topic, json.dumps(payload)

def signal_handler(sig, frame):
    global running
    logger.info("Received termination signal. Shutting down...")
    running = False

def main():
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)

    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_publish = on_publish

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        logger.error(f"✗ Failed to connect to broker: {e}")
        logger.warning("Is your MQTT broker running? Try installing Mosquitto:")

        return

    client.loop_start()

    logger.info(f"MQTT producer started. Publishing to {MQTT_BROKER}:{MQTT_PORT}")
    logger.info("Press Ctrl+C to stop")

    msg_count = 0

    while running:
        try:
            topic, payload = generate_sensor_data()
            client.publish(topic, payload, qos=0, retain=False)

            msg_count += 1
            logger.info(f"[{msg_count}] Published to topic: {topic}")
            logger.info(f"    Payload: {payload}")
            time.sleep(PUBLISH_INTERVAL)

        except Exception as e:
            logger.error(f"✗ Error publishing message: {e}")
            time.sleep(1)

    logger.info("Stopping MQTT producer...")
    client.loop_stop()
    client.disconnect()
    logger.info("MQTT producer stopped")

if __name__ == "__main__":
    logger.info("***************  MQTT Producer for Windows  ***************")
    main()