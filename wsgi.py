import sys
sys.path.insert(0,'deep_predictor')

"""
# activate_this = "venv/bin/activate_this.py"
activate_this = r"C:\Users\can\ProjectDependencies\virtualenvs\venv\Scripts\activate_this.py"
with open(activate_this) as file_:
    execfile(file_.read(), dict(__file__=activate_this))
"""

from deep_predictor import create_app
application = create_app("deep_predictor/cfg/deep_predictor.cfg")

# application.run()