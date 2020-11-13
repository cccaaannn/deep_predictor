# flask
from flask import Flask, request, render_template, redirect, abort, url_for
from werkzeug.utils import secure_filename

# other imports
import uuid
import sys
import os

# my classes
sys.path.insert(0,'deep_predictor')
from logger_creator import logger_creator
from database_handler import database_handler
from prediction_thread import prediction_thread
from predictor import predictor as deep_predictor

# helpers
from helpers.file_folder_operations import file_folder_operations
from helpers.image_operations import image_operations


# create app
def create_app(deep_predictor_cfg_path):
    # create logger
    logger = logger_creator().flask_logger()
    logger.info("creating flask app with cfg file on path:{0}".format(deep_predictor_cfg_path))

    # set config options
    cfg = file_folder_operations.read_json_file(deep_predictor_cfg_path)

    # flask options
    secret_key = cfg["deep_predictor_options"]["flask_options"]["secret_key"]
    debug = cfg["deep_predictor_options"]["flask_options"]["debug"]

    # upload options
    max_content_length = eval(cfg["deep_predictor_options"]["upload_options"]["max_content_length"])
    supported_extensions = cfg["deep_predictor_options"]["upload_options"]["supported_extensions"]

    # api options
    prediction_id_length = cfg["deep_predictor_options"]["api_options"]["prediction_id_length"]
    default_api_response = cfg["deep_predictor_options"]["api_options"]["default_api_response"]
    get_prediction_endpoint = cfg["deep_predictor_options"]["api_options"]["get_prediction_endpoint"]
    get_predictors_endpoint = cfg["deep_predictor_options"]["api_options"]["get_predictors_endpoint"]

    # path options
    temp_save_path = cfg["deep_predictor_options"]["path_options"]["temp_save_path"]
    database_path = cfg["deep_predictor_options"]["path_options"]["database_path"]

    # prediction options
    default_predictor_name = cfg["deep_predictor_options"]["prediction_options"]["default_predictor_name"]


    # create instace of db class
    db = database_handler(database_path = database_path, check_connection = True, create_table = True)

    # create predictors
    predictors = {}
    for predictor in cfg["deep_predictor_options"]["prediction_options"]["predictors"]:
        predictors.update({
            predictor : deep_predictor(cfg["deep_predictor_options"]["prediction_options"]["predictors"][predictor])
        })



    # flask app
    app = Flask(__name__)
    app.config["DEBUG"] = debug
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    app.secret_key = secret_key

    @app.route('/', methods=['GET'])
    def home():
        logger.debug("function: {0} method: {1}".format("home", request.method))
        return render_template("index.html"), 200


    @app.route('/result', methods=['GET'])
    def result():
        logger.debug("function: {0} method: {1}".format("result", request.method))
        return redirect(url_for("home")), 308


    @app.route('/upload', methods=['POST', 'GET'])
    def upload_image():
        logger.debug("function: {0} method: {1}".format("upload_files", request.method))
        if(request.method == 'POST'):
            
            # get elements form form
            uploaded_file = request.files['image']
            filename = secure_filename(uploaded_file.filename)
            model_name = request.form['model_name']
            prediction_id = request.form['prediction_id']


            # check form elements
            if(model_name == ""):
                model_name = default_predictor_name

            if(filename == "" or prediction_id == ""):
                logger.warning("required form elements are empty")
                return render_template("upload.html", models=predictors.keys()), 400

            if(len(prediction_id) != prediction_id_length):
                logger.warning("prediction_id length is wrong")
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
            if(not image_operations.validate_extension(supported_extensions, filename, is_case_sensitive=False)):
                logger.warning("image extension is not supported")
                abort(400, description="image extension is not supported")

            
            # generate unique id
            # unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(temp_save_path, filename))
            unique_filename = str(uuid.uuid4())
            _, file_extension = os.path.splitext(filename)
            unique_full_filename = os.path.join(temp_save_path, unique_filename + file_extension)
            uploaded_file.save(unique_full_filename)


            # check image resizability
            status, unique_full_filename = image_operations.validate_image(unique_full_filename, try_to_convert = True, delete_unresizable = True)
            if(not status):
                logger.warning("image is not supported")
                abort(400, description="image is not supported")

            # prepare preediction
            model_info, model_id = predictors[model_name].get_model_info()
            db.create_prediction(prediction_id, model_info, model_id)

            # start prediction on thread
            pred_thread = prediction_thread(
                database_path, 
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
        logger.debug("function: {0} method: {1}".format("api", request.method))

        # get args
        arguments = request.args
        prediction_id = arguments.get(get_prediction_endpoint)

        if(prediction_id):
            prediction = db.get_prediction_json(prediction_id)
            return prediction, 200

        elif(get_predictors_endpoint in arguments):
            return {get_predictors_endpoint : list(predictors.keys())}, 200

        else:
            logger.warning("prediction_id is not provided")
            return default_api_response, 400

    return app



if __name__ == '__main__':
    create_app("deep_predictor/cfg/deep_predictor_small.cfg").run()