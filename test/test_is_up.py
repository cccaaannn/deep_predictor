import smtplib 
import ssl
import requests

import schedule
import datetime
import time

import logging 
import json

from prediction_generator import prediction_generator





def create_logger(logger_name, log_file, log_level):
    logger = logging.getLogger(logger_name)  
    if(not logger.handlers):
        logger.setLevel(log_level)
        
        # log formatter
        formatter = logging.Formatter("[{0}][%(levelname)s] %(asctime)s %(message)s".format(logger_name), datefmt="%Y-%m-%d %H:%M:%S")

        # file handler
        if(log_file):
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        # stream handler
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        logger.addHandler(stream_handler)

    return logger

def send_mail(sender_mail, sender_password, receiver_mail, mail_subject, mail_body, smtp_server_incoming="smtp.gmail.com"):

    message = "Subject: {0}\n\n{1}".format(mail_subject, mail_body).encode("utf-8")

    context = ssl.create_default_context()
    with smtplib.SMTP_SSL(smtp_server_incoming, 465, context=context) as server:
        server.login(sender_mail, sender_password)
        server.sendmail(sender_mail, receiver_mail, message)

    logger.info("The mail has been sent")

def test_prediction(prediction_gen, mail_info, api_url="http://127.0.0.1:5000/test-api?prediction_id=", result_wait_time=7):
    """tests prediction by generating posting prediction, waiting and geting prediction result
        if result is an error send mail
    """
    try:
        # make prediction
        prediction_id = prediction_gen.post_prediction()

        # wait and get the prediction result
        time.sleep(result_wait_time)
        prediction = json.loads(requests.get("{0}{1}".format(api_url, prediction_id)).text)
        prediction_status = prediction["prediction_status"]
        logger.info(prediction_status)

        if(prediction_status != 200):
            # send the error
            logger.warning("prediction failed with status {0}".format(prediction_status))
            send_mail(mail_info["sender_mail"], mail_info["sender_password"], mail_info["receiver_mail"], "deep_predictor:prediction error {0}".format(prediction_status), mail_body="", smtp_server_incoming="smtp.gmail.com")
    except:
        logger.error("test died", exc_info=True)
        send_mail(mail_info["sender_mail"], mail_info["sender_password"], mail_info["receiver_mail"], "deep_predictor:is up test died", mail_body="", smtp_server_incoming="smtp.gmail.com")







logger_name = "is_up_logger"
log_file = "logs/is_up_logger.log"
log_level = 20

logger = create_logger(logger_name, log_file, log_level)

id_prefix = "TEST" 
id_size = 28 # after adding the prefix size becomes 32
test_image_folder = "test_images/food"
api_key = "4c98a83efe384b53b1db01516907cabb"
api_url = "http://127.0.0.1:5000/test-api?prediction_id="

prediction_gen = prediction_generator(id_prefix, id_size, test_image_folder, api_key)


# mail info
from mail_info import sender_mail, sender_password, receiver_mail
mail_info = {"sender_mail":sender_mail, "sender_password":sender_password, "receiver_mail":receiver_mail}


schedule.every(1).minutes.do(test_prediction, prediction_gen, mail_info, api_url=api_url)
# schedule.every(1).hour.do(test_prediction, prediction_gen, mail_info, api_url=api_url)

while True:
    schedule.run_pending()
    time.sleep(1)

