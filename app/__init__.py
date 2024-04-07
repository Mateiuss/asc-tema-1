"""
This is the __init__.py file that will be used to initialize the Flask application
and set up the logger, ThreadPool, and DataIngestor objects.
"""

from logging.handlers import RotatingFileHandler
from time import gmtime, strftime
from threading import Lock
import logging
import os
from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool

if not os.path.exists("results"):
    os.mkdir("results")

class UTCFormatter(logging.Formatter):
    """
    UTCFormatter class that will be used to format the log messages.
    """
    def formatTime(self, record, datefmt=None):
        """
        Function that formats the time in the log message.
        """
        return strftime('%Y-%m-%d %H:%M:%S GMT', gmtime(record.created))

webserver = Flask(__name__)

# Create a logger object and set it up
webserver.logger = logging.getLogger('server_logger')
webserver.logger.setLevel(logging.DEBUG)

# Set the log file and its handler
LOG_FILE = 'webserver.log'
handler = RotatingFileHandler(LOG_FILE, maxBytes=1024 * 64, backupCount=10)
handler.setLevel(logging.DEBUG)

# Set the formatter for the logger
formatter = UTCFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
webserver.logger.addHandler(handler)

# Initialize the ThreadPool
webserver.tasks_runner = ThreadPool(webserver.logger)
webserver.tasks_runner.start()

# Initialize the DataIngestor
webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

# Initialize the job counter and its lock
webserver.job_counter = 1
webserver.job_lock = Lock()

from app import routes
