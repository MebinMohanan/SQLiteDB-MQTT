# logger.py

import logging
import os

# Create log directory if it doesn't exist
log_dir = "log"
os.makedirs(log_dir, exist_ok=True)

# Application Logger
app_log_path = os.path.join(log_dir, "app_log.log")
app_logger = logging.getLogger('app')
app_logger.setLevel(logging.DEBUG)
app_handler = logging.FileHandler(app_log_path)
app_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
app_handler.setFormatter(app_formatter)
app_logger.addHandler(app_handler)

# MQTT Logger
mqtt_log_path = os.path.join(log_dir, "mqtt_log.log")
mqtt_logger = logging.getLogger('mqtt')
mqtt_logger.setLevel(logging.DEBUG)
mqtt_handler = logging.FileHandler(mqtt_log_path)
mqtt_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
mqtt_handler.setFormatter(mqtt_formatter)
mqtt_logger.addHandler(mqtt_handler)

# Database Logger
db_log_path = os.path.join(log_dir, "db_log.log")
db_logger = logging.getLogger('database')
db_logger.setLevel(logging.DEBUG)
db_handler = logging.FileHandler(db_log_path)
db_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
db_handler.setFormatter(db_formatter)
db_logger.addHandler(db_handler)

# Return all loggers
def get_app_logger():
    return app_logger

def get_mqtt_logger():
    return mqtt_logger

def get_db_logger():
    return db_logger
