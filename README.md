# MQTT Producer & Consumer with SQLite

This project consists of two parts: an MQTT producer that generates sample sensor data and publishes it to an MQTT broker, and an MQTT consumer that receives the data, stores it in an SQLite database, and processes it.

## Features
- **Generates random sample data** for different types of sensors (temperature, humidity, pressure, light).
- **Publishes data to MQTT topics** (either fixed or dynamic).
- **Stores incoming MQTT messages in SQLite database**.
- **Handles graceful shutdown** when receiving termination signals (SIGINT, SIGTERM).
- **Custom logging** for MQTT events, errors, and shutdowns.

## Requirements
- **Python 3.x**: The project is written in Python 3.x.
- **Paho MQTT client library**: Used to interact with the MQTT broker.
- **Python environment variables support**: Managed via `python-dotenv` to load configuration from `.env` files.
- **Colorama**: Used for adding color to terminal outputs for better visibility and ease of use.
- **SQLite**: A lightweight database to store the incoming MQTT messages.
- **Logging**: Built-in Python logging module to capture logs and trace events.

### Install Dependencies
To install the required dependencies, you can use the following command:

```bash
pip install -r requirements.txt
