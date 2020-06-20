from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests
import shutil
import logging
import os



# from deep_predictor import deep_predictor
from my_bot_key import botkey




def __set_logger(logger_name = "telegram_logger", log_file = log_file):
    logger = logging.getLogger(logger_name)  
    if(not logger.handlers):
        logger.setLevel(20)
        
        # log formatter
        formatter = logging.Formatter("[%(levelname)s] \n%(asctime)s \n%(message)s", datefmt="%Y-%m-%d %H:%M:%S")

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

def log_user_info(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info("Function name: {0}\nUser info: {1}".format(func.__name__, args[0].message.from_user))
            return func(*args, **kwargs)
        return wrapper
    return decorator

def log_internal_info(logger):
    def decorator(func):
        def wrapper(*args, **kwargs):
            logger.info("Function name: {0} args: {1}, and kwargs: {2}".format(func.__name__, args, kwargs))
            return func(*args, **kwargs)
        return wrapper
    return decorator

logger = __set_logger()

# instantiate and init predictor backend
# dp = deep_predictor()
# dp.init_predictor()




@log_internal_info(logger)
def __create_unique_file_name(file_path, before_number="(", after_number=")"):
    temp_file_path = file_path
    file_name_counter = 1
    if(os.path.isfile(temp_file_path)):
        while(True):
            save_path, temp_file_name = os.path.split(temp_file_path)
            temp_file_name, temp_file_extension = os.path.splitext(temp_file_name)
            temp_file_name = "{0}{1}{2}{3}{4}".format(temp_file_name, before_number, file_name_counter, after_number, temp_file_extension)
            temp_file_path = os.path.join(save_path, temp_file_name)
            file_name_counter += 1
            if(os.path.isfile(temp_file_path)):
                temp_file_path = file_path
            else:
                file_path = temp_file_path
                break

    return file_path

@log_internal_info(logger)
def __download_file_requests(url, local_full_path):
    with requests.get(url, stream=True) as req:
        with open(local_full_path, 'wb') as file:
            shutil.copyfileobj(req.raw, file)


@log_internal_info(logger)
def __get_image(file_id, bot_key = botkey, download_path = "images/temp"):
    """uses telegrams ap to retrive image"""

    # get file path on server
    file_path_api_str = "https://api.telegram.org/bot{0}/getFile?file_id={1}".format(bot_key, file_id)
    response = requests.get(file_path_api_str).json()
    file_path_on_server = response["result"]["file_path"]
    _ , file_name_on_server = os.path.split(file_path_on_server)
    
    file_download_api_str = "https://api.telegram.org/file/bot{0}/{1}".format(bot_key, file_path_on_server)

    # create unique file name on that path to prevent override
    unique_full_local_path = __create_unique_file_name(os.path.join(download_path, file_name_on_server))
    __download_file_requests(file_download_api_str, unique_full_local_path)

    return unique_full_local_path









def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, context.error)

@log_user_info(logger)
def test(update, context):
    """test function"""
    update.message.reply_text("testing")

@log_user_info(logger)
def help(update, context):
    """help function"""
    update.message.reply_text("help")






@log_user_info(logger)
def image_handler(update, context):
    try:    
        # get image from api
        file_id = update.message.photo[-1].file_id
        image_path = __get_image(botkey, file_id)
        update.message.reply_text("I am predicting wait a sec")

        # make prediction using backend
        image_class, labeled_image = dp.predict_image(image_path)

        # inform the user
        update.message.reply_text("result: {0}".format(image_class))
        if(image_class != "not-classified"):
            context.bot.send_photo(chat_id=update.message.chat.id, photo=labeled_image)

    except Exception:
        logger.exception("image_handler caused problem")
        update.message.reply_text("oops something went wrong")


"""
def image_handler(update, context):
    try:    
        # get image
        file_id = update.message.photo[-1].file_id
        image_path = get_image(botkey, file_id)
        update.message.reply_text("I am predicting wait a sec")

        # make prediction
        prediction_result = predict_image(image_path)
        update.message.reply_text("result: {0}".format(prediction_result))


    except Exception as e:
        update.message.reply_text("oops something went wrong")
"""

"""
predictions_main_folder = "images/predictions"

def image_handler2(update, context):
    try:    
        # get image
        file_id = update.message.photo[-1].file_id
        temp_image_path = get_image(botkey, file_id)
        update.message.reply_text("I am predicting wait a sec")

        # make prediction
        prediction_result = predict_image(temp_image_path)
        
        # labeled_image = prediction_result[][]

        if(prediction_result):
            image_class = prediction_result[0][0]
        else:
            image_class = "not-classified"


        # prepare new image name for predictions directory
        _ , temp_image_name = os.path.split(temp_image_path)
        predicted_image_class_path = os.path.join(predictions_main_folder, image_class)
        predicted_image_path = __create_unique_file_name(os.path.join(predicted_image_class_path, temp_image_name))

        # create class file if not exists
        __create_dir_if_not_exists(predicted_image_class_path)

        # move image from temp to predictions
        os.rename(temp_image_path, predicted_image_path)



        # inform the user
        update.message.reply_text("result: {0}".format(image_class))
        if(image_class != "not-classified"):
            context.bot.send_photo(chat_id=update.message.chat.id, photo=labeled_image)
        

    except Exception as e:
        update.message.reply_text("oops something went wrong")
"""







def main():
    logger.info("bot started")
    
    updater = Updater(botkey, use_context=True)

    updater.dispatcher.add_error_handler(error)
    updater.dispatcher.add_handler(CommandHandler("help", help))
    updater.dispatcher.add_handler(CommandHandler("test", test, pass_user_data=True))
    updater.dispatcher.add_handler(MessageHandler(Filters.photo, image_handler))

    
    updater.start_polling()
    updater.idle()




if __name__ == '__main__':
    main()


