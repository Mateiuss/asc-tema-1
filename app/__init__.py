from flask import Flask
from app.data_ingestor import DataIngestor
from app.task_runner import ThreadPool
from logging.handlers import RotatingFileHandler
from time import gmtime, strftime
import logging

class UTCFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        return strftime('%Y-%m-%d %H:%M:%S GMT', gmtime(record.created))

webserver = Flask(__name__)

# Create a logger object and set it up
webserver.logger = logging.getLogger('server_logger')
webserver.logger.setLevel(logging.DEBUG)

log_file = 'webserver.log'
handler = RotatingFileHandler(log_file, maxBytes=1024 * 256, backupCount=3)
handler.setLevel(logging.DEBUG)

formatter = UTCFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

webserver.logger.addHandler(handler)

webserver.tasks_runner = ThreadPool(webserver.logger)

webserver.tasks_runner.start()

webserver.data_ingestor = DataIngestor("./nutrition_activity_obesity_usa_subset.csv")

webserver.job_counter = 1

from app import routes
