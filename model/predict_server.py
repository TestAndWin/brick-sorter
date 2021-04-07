from flask import Flask, request, make_response, jsonify
import numpy as np
import cv2
from time import time
from predictor import Predictor

app = Flask(__name__)


@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    image = np.array(data['image'])
    p = predictor.predict(image)
    #file_name = '../data/' + p['name'] + '/image_' + str(round(time() * 1000)) + '.jpg'
    file_name = '../images/image_' + str(round(time() * 1000)) + "_" + p['name'] + '.jpg'
    cv2.imwrite(file_name, image)
    return p, 200

@app.route('/save-image', methods=['POST'])
def save_image():
    data = request.json
    image = np.array(data['image'])
    file_name = '../images/image_' + str(round(time() * 1000)) + '.jpg'
    cv2.imwrite(file_name, image)
    return "OK", 200


predictor = Predictor()
app.run(debug=False, host='0.0.0.0')
