# flask
from flask import Flask, request, render_template, redirect, abort, url_for
from werkzeug.utils import secure_filename

# other imports
import requests
import json
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


def validate_recaptcha(recaptcha_response, recaptcha_secret_key):
    """validates recaptcha"""
    payload = {"response":recaptcha_response, "secret":recaptcha_secret_key}
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
    response_dict = json.loads(response.text)
    return response_dict["success"]



# create app
def create_app(deep_predictor_cfg_path):
    # create logger
    logger = logger_creator().flask_logger()
    logger.info("creating flask app with cfg file on path:{0}".format(deep_predictor_cfg_path))

    # set config options
    cfg = file_folder_operations.read_json_file(deep_predictor_cfg_path)

    # flask options
    secret_key = cfg["deep_predictor_options"]["flask_options"]["secret_key"]
    max_content_length = eval(cfg["deep_predictor_options"]["flask_options"]["max_content_length"])
    debug = cfg["deep_predictor_options"]["flask_options"]["debug"]


    # ---------- production options ----------

    # recaptcha_options 
    recaptcha_sitekey = cfg["deep_predictor_options"]["production"]["recaptcha_options"]["recaptcha_sitekey"]
    recaptcha_secret_key = cfg["deep_predictor_options"]["production"]["recaptcha_options"]["recaptcha_secret_key"]

    # upload options
    supported_extensions = cfg["deep_predictor_options"]["production"]["upload_options"]["supported_extensions"]

    # api options
    api_key = cfg["deep_predictor_options"]["production"]["api_options"]["api_key"]
    prediction_id_length = cfg["deep_predictor_options"]["production"]["api_options"]["prediction_id_length"]
    default_api_response = cfg["deep_predictor_options"]["production"]["api_options"]["default_api_response"]
    get_prediction_endpoint = cfg["deep_predictor_options"]["production"]["api_options"]["get_prediction_endpoint"]
    get_predictors_endpoint = cfg["deep_predictor_options"]["production"]["api_options"]["get_predictors_endpoint"]

    # path options
    temp_save_path = cfg["deep_predictor_options"]["production"]["path_options"]["temp_save_path"]
    database_path = cfg["deep_predictor_options"]["production"]["path_options"]["database_path"]

    # prediction options
    default_predictor_name = cfg["deep_predictor_options"]["production"]["prediction_options"]["default_predictor_name"]

    # create instace of db class
    db = database_handler(database_path = database_path, check_connection = True, create_table = True)

    # create predictors
    predictors = {}
    for predictor in cfg["deep_predictor_options"]["production"]["prediction_options"]["predictors"]:
        predictors.update({
            predictor : deep_predictor(cfg["deep_predictor_options"]["production"]["prediction_options"]["predictors"][predictor])
        })
    # --------------------------------------------------

    # ---------- test options ----------

    # upload options
    TEST_supported_extensions = cfg["deep_predictor_options"]["test"]["upload_options"]["supported_extensions"]

    # api options
    TEST_key = cfg["deep_predictor_options"]["test"]["api_options"]["api_key"]
    TEST_prediction_id_length = cfg["deep_predictor_options"]["test"]["api_options"]["prediction_id_length"]
    TEST_default_api_response = cfg["deep_predictor_options"]["test"]["api_options"]["default_api_response"]
    TEST_get_prediction_endpoint = cfg["deep_predictor_options"]["test"]["api_options"]["get_prediction_endpoint"]
    TEST_get_predictors_endpoint = cfg["deep_predictor_options"]["test"]["api_options"]["get_predictors_endpoint"]

    # path options
    TEST_temp_save_path = cfg["deep_predictor_options"]["test"]["path_options"]["temp_save_path"]
    TEST_database_path = cfg["deep_predictor_options"]["test"]["path_options"]["database_path"]

    # create instace of db class
    TEST_db = database_handler(database_path = TEST_database_path, check_connection = True, create_table = True)
    
    # create predictors
    TEST_predictors = {}
    for predictor in cfg["deep_predictor_options"]["test"]["prediction_options"]["predictors"]:
        TEST_predictors.update({
            predictor : deep_predictor(cfg["deep_predictor_options"]["test"]["prediction_options"]["predictors"][predictor])
        })
    # --------------------------------------------------


    # flask app
    app = Flask(__name__)
    app.config["DEBUG"] = debug
    app.config['MAX_CONTENT_LENGTH'] = max_content_length
    app.secret_key = secret_key


    # ---------- regular routes ----------
    @app.route('/', methods=['GET'])
    def home():
        logger.debug("function: {0} method: {1}".format("home", request.method))
        return render_template("index.html"), 200

    @app.route('/result', methods=['GET'])
    def result():
        logger.debug("function: {0} method: {1}".format("result", request.method))
        return redirect(url_for("home")), 308

    @app.route('/upload', methods=['POST', 'GET'])
    def upload():
        logger.debug("function: {0} method: {1}".format("upload", request.method))
        if(request.method == 'POST'):
 
            # ---------- check key errors from form ----------
            try:
                uploaded_file = request.files['image']
                filename = secure_filename(uploaded_file.filename)
                model_name = request.form['model_name']
                prediction_id = request.form['prediction_id']
            except KeyError:
                logger.warning("KeyError", exc_info=True)
                abort(400, description="Unknown key received from form")

            recaptcha_response = request.form.get('g-recaptcha-response')
            form_api_key = request.form.get('api_key')
            # --------------------------------------------------

            # ---------- check recaptcha or api_key ----------
            if(form_api_key):
                # check api key
                if(api_key != form_api_key):
                    logger.warning("api key is incorrect")
                    abort(400, description="Api key is incorrect")
            elif(recaptcha_response):
                # check recaptcha
                if(not validate_recaptcha(recaptcha_response, recaptcha_secret_key)):
                    logger.warning("recaptcha is not verified")
                    return render_template("upload.html", models=predictors.keys(), recaptcha_sitekey=recaptcha_sitekey), 400
            else:
                logger.warning("recaptcha or api key is not provided")
                abort(400, description="Recaptcha or api key is not provided")
            # --------------------------------------------------

            # ---------- check form elements ----------
            if(model_name == ""):
                model_name = default_predictor_name

            if(filename == "" or prediction_id == ""):
                logger.warning("required form elements are empty")
                return render_template("upload.html", models=predictors.keys(), recaptcha_sitekey=recaptcha_sitekey), 400

            # prediction_id length
            if(len(prediction_id) != prediction_id_length):
                logger.warning("prediction_id length is wrong")
                abort(400, description="Something went wrong please try again")

            # model name
            if(model_name not in predictors):
                logger.warning("model name is not exists")
                abort(400, description="This predictor is not exists")

            # image extension
            if(not image_operations.validate_extension(supported_extensions, filename, is_case_sensitive=False)):
                logger.warning("image extension is not supported")
                abort(400, description="Your image extension is not supported")
            # --------------------------------------------------


            # check for prediction_id collision
            if(db.is_prediction_exists(prediction_id)):
                logger.warning("prediction id exists")
                abort(500, description="Something went wrong please try again")

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
                abort(400, description="Your image is not supported")

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
            return render_template("upload.html", models=predictors.keys(), recaptcha_sitekey=recaptcha_sitekey), 200

    @app.route('/api', methods=['GET'])
    def api():
        logger.debug("function: {0} method: {1}".format("api", request.method))

        # get args
        arguments = request.args
        prediction_id = arguments.get(get_prediction_endpoint)
        test_prediction_id = arguments.get(TEST_get_prediction_endpoint)

        if(prediction_id):
            prediction = db.get_prediction_json(prediction_id)
            return prediction, 200

        elif(get_predictors_endpoint in arguments):
            return {get_predictors_endpoint : list(predictors.keys())}, 200

        else:
            logger.warning("prediction_id is not provided")
            return default_api_response, 400


    # ---------- error routes ---------- 
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        # all to 404
        abort(404)

    @app.errorhandler(404)
    def error_404(e):
        logger.debug("function: {0} method: {1}".format("error_404", request.method))
        return render_template('404.html'), 404

    @app.errorhandler(400)
    def error_400(e):
        logger.debug("function: {0} method: {1}".format("error_400", request.method))
        # e.code
        # e.name
        return render_template('400.html', description=e.description), 400
   
    @app.errorhandler(413)
    def error_413(e):
        logger.debug("function: {0} method: {1}".format("error_413", request.method))
        return render_template('413.html', description=e.description), 413
   
    @app.errorhandler(500)
    def error_500(e):
        logger.debug("function: {0} method: {1}".format("error_500", request.method))
        return render_template('500.html', description=e.description), 500
    # --------------------------------------------------


    # ---------- test routes ----------
    @app.route('/test-upload', methods=['POST', 'GET'])
    def test_upload():
        if(request.method == 'POST'):
            logger.debug("function: {0} method: {1}".format("test_upload", request.method))

            # ---------- check key errors from form ----------
            try:
                uploaded_file = request.files['image']
                filename = secure_filename(uploaded_file.filename)
                model_name = request.form['model_name']
                prediction_id = request.form['prediction_id']
                form_api_key = request.form['api_key']
            except KeyError:
                logger.warning("KeyError", exc_info=True)
                abort(400, description="Unknown key received from form")
            # --------------------------------------------------

            # ---------- check test api key ----------
            if(TEST_key != form_api_key):
                logger.warning("test api key is incorrect")
                abort(400, description="test api key is incorrect")
            # --------------------------------------------------

            # ---------- check form elements ----------
            if(filename == "" or prediction_id == "" or model_name == ""):
                logger.warning("required form elements are empty")
                abort(400, description="Required form elements are empty")

            # prediction_id length
            if(len(prediction_id) != TEST_prediction_id_length):
                logger.warning("prediction_id length is wrong")
                abort(400, description="Something went wrong please try again")

            # model name
            if(model_name not in TEST_predictors):
                logger.warning("model name is not exists")
                abort(400, description="This predictor is not exists")

            # image extension
            if(not image_operations.validate_extension(TEST_supported_extensions, filename, is_case_sensitive=False)):
                logger.warning("image extension is not supported")
                abort(400, description="Your image extension is not supported")
            # --------------------------------------------------

            # check for prediction_id collision
            if(TEST_db.is_prediction_exists(prediction_id)):
                logger.warning("prediction id exists")
                abort(500, description="Something went wrong please try again")

            # generate unique id
            # unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(temp_save_path, filename))
            unique_filename = str(uuid.uuid4())
            _, file_extension = os.path.splitext(filename)
            unique_full_filename = os.path.join(TEST_temp_save_path, unique_filename + file_extension)
            uploaded_file.save(unique_full_filename)

            # check image resizability
            status, unique_full_filename = image_operations.validate_image(unique_full_filename, try_to_convert = True, delete_unresizable = True)
            if(not status):
                logger.warning("image is not supported")
                abort(400, description="Your image is not supported")

            # prepare preediction
            model_info, model_id = TEST_predictors[model_name].get_model_info()
            TEST_db.create_prediction(prediction_id, model_info, model_id)

            # start prediction on thread
            pred_thread = prediction_thread(
                TEST_database_path, 
                unique_full_filename, 
                prediction_id, 
                predictor=TEST_predictors[model_name]
                )
            
            pred_thread.start()

            return "success", 201
        else:
            return redirect(url_for("home")), 308

    @app.route('/test-api', methods=['GET'])
    def test_api():
        logger.debug("function: {0} method: {1}".format("test_api", request.method))

        # get args
        arguments = request.args
        prediction_id = arguments.get(TEST_get_prediction_endpoint)

        if(prediction_id):
            prediction = TEST_db.get_prediction_json(prediction_id)
            return prediction, 200

        elif(TEST_get_predictors_endpoint in arguments):
            return {TEST_get_predictors_endpoint : list(TEST_predictors.keys())}, 200

        else:
            logger.warning("prediction_id is not provided")
            return TEST_default_api_response, 400
    # --------------------------------------------------


    @app.route('/admin', methods=['GET'])
    def roll():
        return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO")


    # return flask app for serving
    return app




if __name__ == '__main__':
    create_app("deep_predictor/cfg/deep_predictor_small.cfg").run()