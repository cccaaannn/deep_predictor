import sys
sys.path.insert(0, "deep_predictor")
# from deep_predictor import create_app
from deep_predictor import flask_app
from waitress import serve

# add logger file to waitress logger
import logging
logger = logging.getLogger("waitress")
logger.setLevel(logging.WARN)
file_handler = logging.FileHandler("deep_predictor/logs/waitress.log")
logger.addHandler(file_handler)

# serveing options
deep_predictor = flask_app("deep_predictor/cfg/deep_predictor_small.cfg")
app = deep_predictor.create_app()
host = "0.0.0.0"
port = 5000
threads = 5
# url_scheme = "https"

# start server
serve(app, host=host, port=port, threads=threads)