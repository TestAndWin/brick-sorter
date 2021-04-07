import os
import numpy as np
import shutil
import requests
import time
import cv2
from eventhandler import EventHandler
from flask import Flask, request, send_file, render_template
from PIL import Image

from camera import Camera
from hub import Hub
from motor import Motor
from gate import Gate
from stepper import Stepper

gate_pin = 4

predict_server = "http://192.168.178.70:5000/"


class Sorter:
    def __init__(self):
        self.last_predict = ''
        # When true the ML detection is used, otherwise the images are only saved on the server
        self.do_detection = True
        self.camera = self.init_cam()

        # Using BCM
        self.belt = Motor(16, 20)
        self.plate = Motor(13, 19)
        self.hub = Hub(27, 22, 23, 24)
        self.gate = Gate(gate_pin)
        self.stepper = Stepper(18, 5, 6, 26)

    def init_cam(self):
        camera = Camera()
        camera.event_handler.link(self.brick_detected, 'brick_detected')
        camera.event_handler.link(self.brick_moving_in, 'brick_moving_in')
        return camera

    def save_image(self, image):
        start_time = time.time()
        data = {'image': image.tolist()}
        requests.post(predict_server + "save-image", json=data)
        # Use a slot something in the middle
        return 4

    def predict(self, image):
        start_time = time.time()
        image = cv2.resize(image, dsize=(224, 224), interpolation=cv2.INTER_CUBIC)
        cv2.imwrite("latest.jpg", image)
        data = {'image': image.tolist()}
        try:
            response = requests.post(predict_server + "predict", json=data)

            print("--- %s seconds ---" % (time.time() - start_time))
            print("Status:", response.status_code)
            if not response.status_code == 200:
                return 0
            else:
                j = response.json()
                print("Response:", j)
                self.last_predict = j["name"] + "<br>" + j["distribution"]
                return int(j["index"])
        except requests.exceptions.RequestException as e:
            print("Error sending request", e)
        return -1

    def start_gate(self):
        # Thread can only be started once
        if not self.gate.is_alive():
            del self.gate
            self.gate = Gate(gate_pin)
            self.gate.start_gate()

    def stop_gate(self):
        if self.gate.is_alive():
            self.gate.stop_gate()

    def brick_moving_in(self):
        print("Handle event - Brick moving in")
        self.plate.stop()
        self.stop_gate()
        self.belt.stop()

    def brick_detected(self, image):
        print("Handle event - Brick detected")
        # detection can be disabled when only images should be made
        brick_idx = self.predict(image) if self.do_detection else self.save_image(image)
        # The sorter has 10 slots
        self.hub.move(brick_idx % 10)
        self.stepper.move(1)
        self.stepper.move(-1)
        self.camera.release_for_next()
        self.start_gate()
        self.plate.forward(0.9)
        self.belt.forward(0.2)


app = Flask(__name__)


@app.route('/', methods=['GET'])
def home():
    return get_overview_page()


@app.route('/start-transport', methods=['POST', 'GET'])
def start_transport():
    start_belt()
    start_plate()
    sorter.start_gate()
    return get_overview_page()


@app.route('/stop-transport', methods=['POST', 'GET'])
def stop_transport():
    stop_belt()
    stop_plate()
    sorter.stop_gate()
    return get_overview_page()


@app.route('/start-belt', methods=['POST', 'GET'])
def start_belt():
    sorter.belt.forward(0.2)
    return get_overview_page()


@app.route('/stop-belt', methods=['POST', 'GET'])
def stop_belt():
    sorter.belt.stop()
    return get_overview_page()


@app.route('/start-plate', methods=['POST', 'GET'])
def start_plate():
    sorter.plate.forward(0.9)
    return get_overview_page()


@app.route('/stop-plate', methods=['POST', 'GET'])
def stop_plate():
    sorter.plate.stop()
    return get_overview_page()


@app.route('/move-stepper', methods=['POST', 'GET'])
def move_stepper():
    pos = int(request.args.get('pos'))
    sorter.stepper.move(pos)
    return get_overview_page()


@app.route('/start-gate', methods=['POST', 'GET'])
def do_start_gate():
    sorter.start_gate()
    return get_overview_page()


@app.route('/stop-gate', methods=['POST', 'GET'])
def do_stop_gate():
    sorter.stop_gate()
    return get_overview_page()


@app.route('/move-hub', methods=['POST', 'GET'])
def move_hub():
    slot = int(request.args.get('slot'))
    sorter.hub.move(slot)
    return get_overview_page()


@app.route('/take-picture', methods=['POST', 'GET'])
def take_picture():
    filename = sorter.camera.take_picture()
    return send_file(filename, mimetype='image/jpg')


@app.route('/start-detection', methods=['POST', 'GET'])
def start_detection():
    # Thread can only be started once
    if not sorter.camera.is_alive():
        del sorter.camera
        sorter.camera = sorter.init_cam()
        sorter.camera.start_detection()
    return get_overview_page()


@app.route('/stop-detection', methods=['POST', 'GET'])
def stop_detection():
    if sorter.camera.is_alive():
        sorter.camera.stop_detection()
    return get_overview_page()


@app.route('/last-predict', methods=['GET'])
def get_last_predict():
    return sorter.last_predict


@app.route('/latest.jpg', methods=['GET'])
def latest_image():
    return send_file("latest.jpg", mimetype='image/jpg')


def get_overview_page():
    return render_template("overview.html", belt=sorter.belt.status, plate=sorter.plate.status, stepper=sorter.stepper.stepper_pos, gate=sorter.gate.gate_active, detection=sorter.camera.do_detection, hub=sorter.hub.current_hub_pos)


try:
    sorter = Sorter()
    app.run(debug=False, host='0.0.0.0')

finally:
    sorter.hub.move(0)
