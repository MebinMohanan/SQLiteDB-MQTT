import sqlite3
import shutil
import os
from dotenv import load_dotenv
from logger import get_db_logger  # Import the database logger

# Load environment variables from .env file
load_dotenv()

DB_FILE = os.getenv("DB_FILE", "db/mqtt_data.db")

# Initialize the database logger
db_logger = get_db_logger()

def create_connection(db_file):
    """Establish a connection to the SQLite database."""
    try:
        conn = sqlite3.connect(db_file)
        conn.row_factory = sqlite3.Row  # Return results as dictionaries
        db_logger.info("Database connection established")
        return conn
    except sqlite3.Error as e:
        db_logger.error(f"Error connecting to database: {e}")
        raise

def close_connection(conn):
    """Close the SQLite database connection."""
    try:
        if conn:
            conn.close()
            db_logger.info("Database connection closed")
    except sqlite3.Error as e:
        db_logger.error(f"Error closing the connection: {e}")

def setup_database(db_file):
    """Create the SQLite database and table if they don't exist."""
    conn = create_connection(db_file)
    cursor = conn.cursor()
    try:
        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS device_data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            device TEXT NOT NULL,
            status TEXT NOT NULL,
            value REAL NOT NULL,
            timestamp TEXT NOT NULL
        )
        ''')
        conn.commit()
        db_logger.info("Database setup complete")
    except sqlite3.Error as e:
        db_logger.error(f" Database setup error: {e}")
    finally:
        close_connection(conn)

def insert_device_data(conn, device, status, value, timestamp):
    """Insert device data into the SQLite database."""
    try:
        cursor = conn.cursor()
        cursor.execute(
            f"""INSERT INTO device_data 
               (device, status, value, timestamp) 
               VALUES (?, ?, ?, ?)""",
            (device, status, value, timestamp)
        )
        conn.commit()
        db_logger.info(f"Data inserted for device {device} with status {status}")
    except sqlite3.Error as e:
        db_logger.error(f" Error inserting data for device {device}: {e}")

def backup_database(db_file):
    """Backup the current SQLite database."""
    backup_file = f"{db_file}.backup"
    try:
        shutil.copy(db_file, backup_file)
        db_logger.info(f"Database backup created at {backup_file}")
    except Exception as e:
        db_logger.error(f" Error creating backup: {e}")

def restore_database(db_file):
    """Restore the SQLite database from the backup."""
    backup_file = f"{db_file}.backup"
    try:
        if os.path.exists(backup_file):
            shutil.copy(backup_file, db_file)
            db_logger.info(" Database restored from backup.")
        else:
            db_logger.warning(f"Backup file {backup_file} not found.")
    except Exception as e:
        db_logger.error(f" Error restoring database: {e}")

def health_check(db_file):
    """Perform a health check on the SQLite database."""
    try:
        conn = create_connection(db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")  # Simple query to check if the database is responsive
        result = cursor.fetchone()
        if result:
            db_logger.info(" Database health check passed")
            close_connection(conn)
            return True
        else:
            db_logger.warning(" Database health check failed: No result")
            close_connection(conn)
            return False
    except sqlite3.Error as e:
        db_logger.error(f" Database health check failed: {e}")
        return False
