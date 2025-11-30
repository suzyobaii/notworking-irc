import logging
import os

# Makes sure that the logging directory exists by force
LOG_DIR = os.path.join(os.path.dirname(__file__), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

def setupLogClient():
    log_path = os.path.join(LOG_DIR, "client.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True  # was the main issue, since basicConfig was happening twice and the second wasnt being considered.  now this makes sure it works
    )

def setupLogServer():
    log_path = os.path.join(LOG_DIR, "server.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        force=True
    )
