import sys
sys.path.insert(0,'deep_predictor')

from deep_predictor import create_app
application = create_app("deep_predictor/cfg/deep_predictor.cfg")

# application.run()