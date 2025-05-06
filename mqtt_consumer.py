import paho.mqtt.client as mqtt
import json
import signal
import os
import time
from dotenv import load_dotenv
from database import create_connection, insert_device_data, setup_database
from logger import get_app_logger, get_mqtt_logger, get_db_logger  # Import the loggers

# Load environment variables from .env file
load_dotenv()

# Initialize loggers
app_logger = get_app_logger()
mqtt_logger = get_mqtt_logger()
db_logger = get_db_logger()

# MQTT Configuration
MQTT_BROKER = os.getenv("MQTT_BROKER", "localhost")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_FIXED_TOPIC", "test/custom/topic")
MQTT_CLIENT_ID = f"windows-consumer-{os.getpid()}"
MQTT_USERNAME = os.getenv("MQTT_USERNAME")
MQTT_PASSWORD = os.getenv("MQTT_PASSWORD")

# Database file path and commit interval
DB_FILE = os.getenv("DB_FILE", "mqtt_data.db")
COMMIT_INTERVAL = int(os.getenv("COMMIT_INTERVAL", 5))

# Global flag to control running loop
running = True
message_count = 0

def on_connect(client, userdata, flags, rc):
    """Callback when connected to the MQTT broker."""
    if rc == 0:
        mqtt_logger.info(f" Connected to MQTT broker at {MQTT_BROKER}:{MQTT_PORT}")
        client.subscribe(MQTT_TOPIC)
        mqtt_logger.info(f" Subscribed to topic: {MQTT_TOPIC}")
    else:
        mqtt_logger.error(f" Failed to connect to MQTT broker with code: {rc}")

def on_disconnect(client, userdata, rc):
    """Callback when disconnected from the MQTT broker."""
    if rc != 0:
        mqtt_logger.warning("! Unexpected disconnection from MQTT broker")
        mqtt_logger.info("i Attempting to reconnect...")
        try:
            client.reconnect()
        except Exception as e:
            mqtt_logger.error(f" Failed to reconnect: {e}")

def on_message(client, userdata, msg):
    """Callback when a message is received from subscribed topics."""
    global message_count
    topic = msg.topic
    try:
        payload_str = msg.payload.decode('utf-8')
        payload = json.loads(payload_str)
        
        device = payload.get('device', 'unknown')
        status = payload.get('status', 'unknown')
        value = payload.get('value', 0)
        timestamp = payload.get('timestamp', time.ctime())
        
        # Create a new SQLite connection in this thread
        db_conn = create_connection(DB_FILE)
        insert_device_data(db_conn, device, status, value, timestamp)
        db_conn.close()

        mqtt_logger.info(f"Received message on {topic}")
        mqtt_logger.info(f"  {device} status: {status}, value: {value}, timestamp: {timestamp}")

        # Commit after every 5 messages
        message_count += 1
        if message_count >= COMMIT_INTERVAL:
            mqtt_logger.info(f"Committed {message_count} messages to database")
            message_count = 0

    except json.JSONDecodeError:
        mqtt_logger.warning(f"! Received non-JSON message on {topic}")
        db_conn = create_connection(DB_FILE)
        insert_device_data(db_conn, "raw", "non-json", 0, time.ctime())
        db_conn.close()
        
    except Exception as e:
        mqtt_logger.error(f" Error processing message: {e}")

def signal_handler(sig, frame):
    """Handle termination signals gracefully."""
    global running
    app_logger.info("\nReceived termination signal. Cleaning up...")
    running = False

def main():
    """Main function to set up and start the MQTT client."""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Set up the database
    setup_database(DB_FILE)

    # Set up MQTT client
    client = mqtt.Client(client_id=MQTT_CLIENT_ID, protocol=mqtt.MQTTv311)

    # Set username and password if provided
    if MQTT_USERNAME and MQTT_PASSWORD:
        client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

    # Set up callbacks
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    # Connect to the broker
    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
    except Exception as e:
        mqtt_logger.error(f"Failed to connect to broker: {e}")
        return

    # Start the loop
    client.loop_start()
    app_logger.info("MQTT consumer started. Waiting for messages...")

    # Keep the main thread alive
    try:
        while running:
            time.sleep(1)
    finally:
        client.loop_stop()
        client.disconnect()
        app_logger.info("MQTT consumer stopped")

if __name__ == "__main__":
    app_logger.info("MQTT Consumer for Windows")
    main()
