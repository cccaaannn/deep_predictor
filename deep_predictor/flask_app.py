# flask
from flask import Flask, request, render_template, redirect, abort, url_for
from werkzeug.utils import secure_filename

# other imports
import uuid
import sys
import os

# my classes
from logger_creator import logger_creator
from database_handler import database_handler
from prediction_thread import prediction_thread

# helpers
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations




# cfg path
flask_cfg_path = "deep_predictor/cfg/flask.cfg"


# create app
app = Flask(__name__)

# set config options
cfg = file_folder_operations.read_json_file(flask_cfg_path)

database_handler_cfg_path = cfg["flask_options"]["database_handler_cfg_path"]
supported_extensions = cfg["flask_options"]["supported_extensions"]
temp_save_path = cfg["flask_options"]["temp_save_path"]
default_api_response = cfg["flask_options"]["default_api_response"]

app.config["DEBUG"] = True
app.config['MAX_CONTENT_LENGTH'] = cfg["flask_options"]["MAX_CONTENT_LENGTH"]
# app.config['UPLOAD_EXTENSIONS'] = cfg["flask_options"]["UPLOAD_EXTENSIONS"]
# app.config['UPLOAD_PATH'] = cfg["flask_options"]["UPLOAD_PATH"]



# create logger and db
logger = logger_creator().flask_logger()
db = database_handler(database_handler_cfg_path)


# create predictors
from deep_predictor import deep_predictor
predictors = {}
for predictor in cfg["predictors"]:
    predictors.update({
        predictor : deep_predictor(cfg["predictors"][predictor], init=True)
    })






@app.route('/', methods=['GET'])
def home():
    logger.info("function: {0} method: {1}".format("home", request.method))
    return render_template("index.html"), 200


@app.route('/result', methods=['GET'])
def result():
    return redirect(url_for("home")), 308


@app.route('/upload', methods=['POST', 'GET'])
def upload_image():
    logger.info("function: {0} method: {1}".format("upload_files", request.method))
    if(request.method == 'POST'):
        
        # get elements form form
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)
        model_name = request.form['model_name']
        prediction_id = request.form['prediction_id']


        # check form elements
        if(filename == "" or model_name == "" or prediction_id == ""):
            logger.warning("required form elements are empty")
            return render_template("upload.html", models=predictors.keys()), 400

        # check model name
        if(model_name not in predictors):
            logger.warning("model name is not exists")
            abort(400, description="model name is not exists")

        # check for collision
        if(db.is_prediction_exists(prediction_id)):
            logger.warning("prediction id exists")
            abort(400, description="prediction id exists")

        # check image extension
        if(not image_operations.validate_extension(supported_extensions, filename)):
            logger.warning("image extension is not supported")
            abort(400, description="image extension is not supported")

        
        # generate unique id
        # unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(temp_save_path, filename))
        unique_filename = str(uuid.uuid4())
        _, file_extension = os.path.splitext(filename)
        unique_full_filename = os.path.join(temp_save_path, unique_filename + file_extension)
        uploaded_file.save(unique_full_filename)


        # check image resizability
        if(not image_operations.validate_image(unique_full_filename, delete = True)):
            logger.warning("image is not supported")
            abort(400, description="image is not supported")


        # prepare preediction
        db.create_prediction(prediction_id)

        # start prediction on thread
        pred_thread = prediction_thread(
            database_handler_cfg_path, 
            unique_full_filename, 
            prediction_id, 
            predictor=predictors[model_name]
            )
        
        pred_thread.start()

        return render_template("result.html", prediction_id=prediction_id), 201
    else:
        return render_template("upload.html", models=predictors.keys()), 200


@app.route('/api', methods=['GET'])
def api():
    logger.info("function: {0} method: {1}".format("api", request.method))

    # get args
    query_parameters = request.args
    prediction_id = query_parameters.get('prediction_id')

    prediction = default_api_response

    if(prediction_id):
        prediction = db.get_prediction_json(prediction_id)

        return prediction, 200
    else:
        return prediction, 500
    # try:



app.run()