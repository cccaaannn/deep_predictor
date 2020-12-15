
"""
https://github.com/hunglc007/tensorflow-yolov4-tflite
this is a modified version of the detect.py on this repo
"""

import tensorflow as tf

# USE ONLY CPU
# physical_devices = tf.config.experimental.list_physical_devices('GPU')
# if len(physical_devices) > 0:
#     tf.config.experimental.set_memory_growth(physical_devices[0], True)


from tensorflow.python.saved_model import tag_constants
import numpy as np
import cv2

def read_class_names_tf_yolo(class_file_name):
    names = {}
    with open(class_file_name, 'r') as data:
        for ID, name in enumerate(data):
            names[ID] = name.strip('\n')
    return names

def load_tf_yolo_model(model_path):
    saved_model_loaded = tf.saved_model.load(model_path, tags=[tag_constants.SERVING])
    return saved_model_loaded

def perform_detect(saved_model_loaded, names, original_image, image_data, iou_threshold, score_threshold, max_output_size_per_class, max_total_size):

    images_data = []
    for i in range(1):
        images_data.append(image_data)
    images_data = np.asarray(images_data).astype(np.float32)


    infer = saved_model_loaded.signatures['serving_default']
    batch_data = tf.constant(images_data)
    pred_bbox = infer(batch_data)
    for key, value in pred_bbox.items():
        boxes = value[:, :, 0:4]
        pred_conf = value[:, :, 4:]
    
    boxes, scores, classes, valid_detections = tf.image.combined_non_max_suppression(
        boxes=tf.reshape(boxes, (tf.shape(boxes)[0], -1, 1, 4)),
        scores=tf.reshape(
            pred_conf, (tf.shape(pred_conf)[0], -1, tf.shape(pred_conf)[-1])),
        max_output_size_per_class=max_output_size_per_class,
        max_total_size=max_total_size,
        iou_threshold=iou_threshold,
        score_threshold=score_threshold
    )
    pred_bbox = [boxes.numpy(), scores.numpy(), classes.numpy(), valid_detections.numpy()]


    predictions = []
    classes = names
    num_classes = len(classes)
    image_height, image_width, _ = original_image.shape
    out_boxes, out_scores, out_classes, num_boxes = pred_bbox
    for i in range(num_boxes[0]):
        if int(out_classes[0][i]) < 0 or int(out_classes[0][i]) > num_classes: continue

        coor = out_boxes[0][i]
        x1 = coor[1]
        y1 = coor[0]
        x2 = coor[3]
        y2 = coor[2]

        # if not scaled
        # cx = (x2 - (x2-x1) / 2) / image_width
        # cy = (y2 - (y2-y1) / 2) / image_height

        # w = (x2-x1) / image_width
        # h = (y2-y1) / image_height

        cx = (x2 - (x2-x1) / 2) 
        cy = (y2 - (y2-y1) / 2) 

        w = (x2-x1)
        h = (y2-y1)

        predictions.append(
            (
                classes[out_classes[0][i]],
                out_scores[0][i], 
                (cx,cy,w,h)
            )
        )

        # print()
        # print(
        #     classes[out_classes[0][i]],
        #     float("{0:.5f}".format(float(out_scores[0][i]))), 
        #     float("{0:.5f}".format(cx)), 
        #     float("{0:.5f}".format(cy)), 
        #     float("{0:.5f}".format(w)), 
        #     float("{0:.5f}".format(h)), 
        #     end="\n")
    
    return predictions

