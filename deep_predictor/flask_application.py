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



# create app
class flask_app():
    def __init__(self, deep_predictor_cfg_path):
        self.__logger = logger_creator().flask_logger()

        self.__deep_predictor_cfg_path = deep_predictor_cfg_path
        self.__set_options()
        self.__connect_db()
        self.__init_predictors()


    def __set_options(self):
        """reads cfg file and assigns cfg values to local variables"""
        self.__logger.info("flask_app using cfg file on path:{0}".format(self.__deep_predictor_cfg_path))

        # set config options
        cfg = file_folder_operations.read_json_file(self.__deep_predictor_cfg_path)

        # flask options
        self.__secret_key = cfg["deep_predictor_options"]["flask_options"]["secret_key"]
        self.__max_content_length = eval(cfg["deep_predictor_options"]["flask_options"]["max_content_length"])
        self.__debug = cfg["deep_predictor_options"]["flask_options"]["debug"]


        # ---------- production options ----------

        # recaptcha_options 
        self.__recaptcha_sitekey = cfg["deep_predictor_options"]["production"]["recaptcha_options"]["recaptcha_sitekey"]
        self.recaptcha_secret_key = cfg["deep_predictor_options"]["production"]["recaptcha_options"]["recaptcha_secret_key"]

        # upload options
        self.__supported_extensions = cfg["deep_predictor_options"]["production"]["upload_options"]["supported_extensions"]

        # api options
        self.__api_key = cfg["deep_predictor_options"]["production"]["api_options"]["api_key"]
        self.__prediction_id_length = cfg["deep_predictor_options"]["production"]["api_options"]["prediction_id_length"]
        self.__default_api_response = cfg["deep_predictor_options"]["production"]["api_options"]["default_api_response"]
        self.__get_prediction_endpoint = cfg["deep_predictor_options"]["production"]["api_options"]["get_prediction_endpoint"]
        self.__get_predictors_endpoint = cfg["deep_predictor_options"]["production"]["api_options"]["get_predictors_endpoint"]

        # path options
        self.__temp_save_path = cfg["deep_predictor_options"]["production"]["path_options"]["temp_save_path"]
        self.__database_path = cfg["deep_predictor_options"]["production"]["path_options"]["database_path"]

        # prediction options
        self.__default_predictor_name = cfg["deep_predictor_options"]["production"]["prediction_options"]["default_predictor_name"]

        # predictor cfg paths
        self.__predictor_cfgs = cfg["deep_predictor_options"]["test"]["prediction_options"]["predictors"]

        # --------------------------------------------------

        # ---------- test options ----------

        # upload options
        self.__TEST_supported_extensions = cfg["deep_predictor_options"]["test"]["upload_options"]["supported_extensions"]

        # api options
        self.__TEST_key = cfg["deep_predictor_options"]["test"]["api_options"]["api_key"]
        self.__TEST_prediction_id_length = cfg["deep_predictor_options"]["test"]["api_options"]["prediction_id_length"]
        self.__TEST_default_api_response = cfg["deep_predictor_options"]["test"]["api_options"]["default_api_response"]
        self.__TEST_get_prediction_endpoint = cfg["deep_predictor_options"]["test"]["api_options"]["get_prediction_endpoint"]
        self.__TEST_get_predictors_endpoint = cfg["deep_predictor_options"]["test"]["api_options"]["get_predictors_endpoint"]

        # path options
        self.__TEST_temp_save_path = cfg["deep_predictor_options"]["test"]["path_options"]["temp_save_path"]
        self.__TEST_database_path = cfg["deep_predictor_options"]["test"]["path_options"]["database_path"]

        # predictor cfg paths
        self.__TEST_predictor_cfgs = cfg["deep_predictor_options"]["production"]["prediction_options"]["predictors"]

        # --------------------------------------------------


    def __init_predictors(self):
        """creates predictors"""

        self.__predictors = {}
        for predictor in self.__TEST_predictor_cfgs:
            self.__predictors.update({
                predictor : deep_predictor(self.__TEST_predictor_cfgs[predictor])
            })

        self.__TEST_predictors = {}
        for predictor in self.__predictor_cfgs:
            self.__TEST_predictors.update({
                predictor : deep_predictor(self.__predictor_cfgs[predictor])
            })
 
    def __connect_db(self):
        """creates instace of db class"""
        self.__db = database_handler(database_path = self.__database_path, check_connection = True, create_table = True)
        self.__TEST_db = database_handler(database_path = self.__TEST_database_path, check_connection = True, create_table = True)

    def __validate_recaptcha(self, recaptcha_response, recaptcha_secret_key):
        """validates recaptcha"""
        payload = {"response":recaptcha_response, "secret":recaptcha_secret_key}
        response = requests.post("https://www.google.com/recaptcha/api/siteverify", payload)
        response_dict = json.loads(response.text)
        return response_dict["success"]


    def create_app(self):
        """creates flask app"""
        self.__logger.info("creating flask app")

        # flask app
        app = Flask(__name__)
        app.config["DEBUG"] = self.__debug
        app.config['MAX_CONTENT_LENGTH'] = self.__max_content_length
        app.secret_key = self.__secret_key


        # ---------- regular routes ----------
        @app.route('/', methods=['GET'])
        def home():
            self.__logger.debug("function: {0} method: {1}".format("home", request.method))
            return render_template("index.html"), 200

        @app.route('/result', methods=['GET'])
        def result():
            self.__logger.debug("function: {0} method: {1}".format("result", request.method))
            return redirect(url_for("home")), 308

        @app.route('/upload', methods=['POST', 'GET'])
        def upload():
            self.__logger.debug("function: {0} method: {1}".format("upload", request.method))
            if(request.method == 'POST'):
    
                # ---------- check key errors from form ----------
                try:
                    uploaded_file = request.files['image']
                    filename = secure_filename(uploaded_file.filename)
                    model_name = request.form['model_name']
                    prediction_id = request.form['prediction_id']
                except KeyError:
                    self.__logger.warning("KeyError", exc_info=True)
                    abort(400, description="Unknown key received from form")

                recaptcha_response = request.form.get('g-recaptcha-response')
                form_api_key = request.form.get('api_key')
                # --------------------------------------------------

                # ---------- check recaptcha or api_key ----------
                if(form_api_key):
                    # check api key
                    if(self.__api_key != form_api_key):
                        self.__logger.warning("api key is incorrect")
                        abort(400, description="Api key is incorrect")
                elif(recaptcha_response):
                    # check recaptcha
                    if(not self.__validate_recaptcha(recaptcha_response, self.recaptcha_secret_key)):
                        self.__logger.warning("recaptcha is not verified")
                        return render_template("upload.html", models=self.__predictors.keys(), recaptcha_sitekey=self.__recaptcha_sitekey), 400
                else:
                    self.__logger.warning("recaptcha or api key is not provided")
                    abort(400, description="Recaptcha or api key is not provided")
                # --------------------------------------------------

                # ---------- check form elements ----------
                if(model_name == ""):
                    model_name = self.__default_predictor_name

                if(filename == "" or prediction_id == ""):
                    self.__logger.warning("required form elements are empty")
                    return render_template("upload.html", models=self.__predictors.keys(), recaptcha_sitekey=self.__recaptcha_sitekey), 400

                # prediction_id length
                if(len(prediction_id) != self.__prediction_id_length):
                    self.__logger.warning("prediction_id length is wrong")
                    abort(400, description="Something went wrong please try again")

                # model name
                if(model_name not in self.__predictors):
                    self.__logger.warning("model name is not exists")
                    abort(400, description="This predictor is not exists")

                # image extension
                if(not image_operations.validate_extension(self.__supported_extensions, filename, is_case_sensitive=False)):
                    self.__logger.warning("image extension is not supported")
                    abort(400, description="Your image extension is not supported")
                # --------------------------------------------------


                # check for prediction_id collision
                if(self.__db.is_prediction_exists(prediction_id)):
                    self.__logger.warning("prediction id exists")
                    abort(500, description="Something went wrong please try again")

                # generate unique id
                # unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(temp_save_path, filename))
                unique_filename = str(uuid.uuid4())
                _, file_extension = os.path.splitext(filename)
                unique_full_filename = os.path.join(self.__temp_save_path, unique_filename + file_extension)
                uploaded_file.save(unique_full_filename)


                # check image resizability
                status, unique_full_filename = image_operations.validate_image(unique_full_filename, try_to_convert = True, delete_unresizable = True)
                if(not status):
                    self.__logger.warning("image is not supported")
                    abort(400, description="Your image is not supported")

                # prepare preediction
                model_info, model_id = self.__predictors[model_name].get_model_info()
                self.__db.create_prediction(prediction_id, model_info, model_id)

                # start prediction on thread
                pred_thread = prediction_thread(
                    self.__database_path, 
                    unique_full_filename, 
                    prediction_id, 
                    predictor=self.__predictors[model_name]
                    )

                pred_thread.start()

                return render_template("result.html", prediction_id=prediction_id), 201
            else:
                return render_template("upload.html", models=self.__predictors.keys(), recaptcha_sitekey=self.__recaptcha_sitekey), 200

        @app.route('/api', methods=['GET'])
        def api():
            self.__logger.debug("function: {0} method: {1}".format("api", request.method))

            # get args
            arguments = request.args
            prediction_id = arguments.get(self.__get_prediction_endpoint)

            if(prediction_id):
                prediction = self.__db.get_prediction_json(prediction_id)
                return prediction, 200

            elif(self.__get_predictors_endpoint in arguments):
                return {self.__get_predictors_endpoint : list(self.__predictors.keys())}, 200

            else:
                self.__logger.warning("prediction_id is not provided")
                return self.__default_api_response, 400
        # --------------------------------------------------


        # ---------- test routes ----------
        @app.route('/test-upload', methods=['POST', 'GET'])
        def test_upload():
            if(request.method == 'POST'):
                self.__logger.debug("function: {0} method: {1}".format("test_upload", request.method))

                # ---------- check key errors from form ----------
                try:
                    uploaded_file = request.files['image']
                    filename = secure_filename(uploaded_file.filename)
                    model_name = request.form['model_name']
                    prediction_id = request.form['prediction_id']
                    form_api_key = request.form['api_key']
                except KeyError:
                    self.__logger.warning("KeyError", exc_info=True)
                    abort(400, description="Unknown key received from form")
                # --------------------------------------------------

                # ---------- check test api key ----------
                if(self.__TEST_key != form_api_key):
                    self.__logger.warning("test api key is incorrect")
                    abort(400, description="test api key is incorrect")
                # --------------------------------------------------

                # ---------- check form elements ----------
                if(filename == "" or prediction_id == "" or model_name == ""):
                    self.__logger.warning("required form elements are empty")
                    abort(400, description="Required form elements are empty")

                # prediction_id length
                if(len(prediction_id) != self.__TEST_prediction_id_length):
                    self.__logger.warning("prediction_id length is wrong")
                    abort(400, description="Something went wrong please try again")

                # model name
                if(model_name not in self.__TEST_predictors):
                    self.__logger.warning("model name is not exists")
                    abort(400, description="This predictor is not exists")

                # image extension
                if(not image_operations.validate_extension(self.__TEST_supported_extensions, filename, is_case_sensitive=False)):
                    self.__logger.warning("image extension is not supported")
                    abort(400, description="Your image extension is not supported")
                # --------------------------------------------------

                # check for prediction_id collision
                if(self.__TEST_db.is_prediction_exists(prediction_id)):
                    self.__logger.warning("prediction id exists")
                    abort(500, description="Something went wrong please try again")

                # generate unique id
                # unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(temp_save_path, filename))
                unique_filename = str(uuid.uuid4())
                _, file_extension = os.path.splitext(filename)
                unique_full_filename = os.path.join(self.__TEST_temp_save_path, unique_filename + file_extension)
                uploaded_file.save(unique_full_filename)

                # check image resizability
                status, unique_full_filename = image_operations.validate_image(unique_full_filename, try_to_convert = True, delete_unresizable = True)
                if(not status):
                    self.__logger.warning("image is not supported")
                    abort(400, description="Your image is not supported")

                # prepare preediction
                model_info, model_id = self.__TEST_predictors[model_name].get_model_info()
                self.__TEST_db.create_prediction(prediction_id, model_info, model_id)

                # start prediction on thread
                pred_thread = prediction_thread(
                    self.__TEST_database_path, 
                    unique_full_filename, 
                    prediction_id, 
                    predictor=self.__TEST_predictors[model_name]
                    )
                
                pred_thread.start()

                return "success", 201
            else:
                return redirect(url_for("home")), 308

        @app.route('/test-api', methods=['GET'])
        def test_api():
            self.__logger.debug("function: {0} method: {1}".format("test_api", request.method))

            # get args
            arguments = request.args
            prediction_id = arguments.get(self.__TEST_get_prediction_endpoint)

            if(prediction_id):
                prediction = self.__TEST_db.get_prediction_json(prediction_id)
                return prediction, 200

            elif(self.__TEST_get_predictors_endpoint in arguments):
                return {self.__TEST_get_predictors_endpoint : list(self.__TEST_predictors.keys())}, 200

            else:
                self.__logger.warning("prediction_id is not provided")
                return self.__TEST_default_api_response, 400
        # --------------------------------------------------


        # ---------- error routes ---------- 
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        def catch_all(path):
            abort(404)

        @app.errorhandler(404)   
        @app.errorhandler(400)
        @app.errorhandler(413)
        @app.errorhandler(500)
        def generic_error(e):
            self.__logger.debug("function: {0} method: {1}".format("error", request.method))

            if(e.code == 404):
                return render_template('error.html', description="The page you are looking for is not found", code=e.code), e.code
            elif(e.code == 413):
                return render_template('error.html', description="Your image is too large", code=e.code), e.code
            else:
                return render_template('error.html', description=e.description, code=e.code), e.code

        # --------------------------------------------------


        # ---------- other routes ---------- 
        @app.route('/admin', methods=['GET'])
        def roll():
            # rickroll time
            return redirect("https://www.youtube.com/watch?v=dQw4w9WgXcQ&ab_channel=RickAstleyVEVO")
        # --------------------------------------------------


        # return flask app for serving
        return app




if __name__ == '__main__':
    f = flask_app("deep_predictor/cfg/deep_predictor_small.cfg")
    f.create_app().run()