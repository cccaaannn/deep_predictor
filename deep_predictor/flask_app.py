from flask import Flask, request, render_template, redirect, abort
from werkzeug.utils import secure_filename
import sys
import os

# import tensorflow as tf

# cfg paths
flask_cfg_path = "deep_predictor/cfg/flask.cfg"
database_handler_cfg_path = "deep_predictor/cfg/database.cfg"
deep_predctor_cfg_path = "deep_predictor/cfg/other/mnist_options.cfg"


from helpers.file_folder_operations import file_folder_operations

from helpers.image_operations import image_operations


cfg = file_folder_operations.read_json_file(flask_cfg_path)


from logger_creator import logger_creator
logger = logger_creator().flask_logger()



from database_handler import database_handler
db = database_handler(database_handler_cfg_path)



# from deep_predictor import deep_predictor
# predictor = deep_predictor(deep_predctor_cfg_path)
# predictor.init_predictor(darknet = False, keras = True)
# tf_graph = tf.get_default_graph()


# dummy predictor for testing without keras or tf
from predictor_dummy import predictor
predictor = predictor()
predictor.init()
tf_graph = None



from prediction_thread import prediction_thread





# create app
app = Flask(__name__)
app.config["DEBUG"] = True
app.config['MAX_CONTENT_LENGTH'] = cfg["flask_options"]["MAX_CONTENT_LENGTH"]
app.config['UPLOAD_EXTENSIONS'] = cfg["flask_options"]["UPLOAD_EXTENSIONS"]
app.config['UPLOAD_PATH'] = cfg["flask_options"]["UPLOAD_PATH"]


@app.route('/', methods=['GET'])
def home():
    logger.info("function: {0} method: {1}".format("home", request.method))
    return render_template("index.html")


@app.route('/result', methods=['GET'])
def result_page():
    return redirect("upload.html")




@app.route('/upload', methods=['POST', 'GET'])
def upload_files():
    logger.info("function: {0} method: {1}".format("upload_files", request.method))
    if(request.method == 'POST'):
        uploaded_file = request.files['file']
        filename = secure_filename(uploaded_file.filename)

        model_id = request.form['model_id']
        prediction_id = request.form['prediction_id']


        if(filename == "" or model_id == "" or prediction_id == ""):
            return render_template("upload.html")
        

        # prevet collision
        if(db.is_prediction_exists(prediction_id)):
            # db.update_prediction_status(prediction_id, 400)
            abort(400)

        # prepare preediction
        db.create_prediction(prediction_id)


        if(not image_operations.validate_extension(app.config['UPLOAD_EXTENSIONS'], filename)):
            logger.warning("image extension is not supported")
            db.update_prediction_status(prediction_id, 310)
            # db.delete_prediction(prediction_id)
            abort(400)


        unique_full_filename = file_folder_operations.create_unique_file_name(os.path.join(app.config['UPLOAD_PATH'], filename))
        uploaded_file.save(unique_full_filename)


        if(not image_operations.validate_image(unique_full_filename, delete = True)):
            logger.warning("image is not supported")
            db.update_prediction_status(prediction_id, 350)
            # db.delete_prediction(prediction_id)
            abort(400)

        # start prediction on thread
        pred_thread = prediction_thread(database_handler_cfg_path, unique_full_filename, prediction_id, int(model_id), predictor, tf_graph, is_dummy=True)
        pred_thread.start()

        return render_template("result.html", prediction_id=prediction_id)
    else:
        return render_template("upload.html")



@app.route('/api', methods=['GET'])
def api():
    logger.info("function: {0} method: {1}".format("api", request.method))

    query_parameters = request.args

    prediction_id = query_parameters.get('prediction_id')

    prediction = cfg["flask_options"]["dafault_api_response"]

    if(prediction_id):
        prediction = db.get_prediction(prediction_id)

        return prediction
    else:
        return prediction
    # try:




app.run()