from picamera import PiCamera
from time import sleep, time
import numpy as np
import io
import cv2
from eventhandler import EventHandler
from threading import Thread
from datetime import datetime

cam = PiCamera()
cam.resolution = (600, 600)
cam.sensor_mode = 0

sigma = 0.33
time_to_rest = 600

class Camera(Thread):
    def __init__(self):
        self.event_handler = EventHandler('brick_detected', 'brick_moving_in')
        self.do_detection = False
        self.current_time = 0
        self.event_triggered = False
        Thread.__init__(self)

    def start_detection(self):
        print('Start detection')
        self.do_detection = True
        self.start()

    def stop_detection(self):
        print('Stop detection')
        self.do_detection = False
        self.join()

    def run(self):
        while self.do_detection:
            if not self.event_triggered:
                self.find_contours_and_trigger(self.take_picture_as_np())

    def take_picture(self):
        print('Take Picture')
        filename = './pictures/im_' + str(round(time() * 1000)) + '.jpg'
        cam.capture(filename, resize=(224, 224))
        return filename

    def take_picture_as_np(self):
        # w multiply of 32, h of 16
        output = np.empty((608, 608, 3), dtype=np.uint8)
        cam.capture(output, format='bgr', use_video_port=True)
        output = output.reshape((608, 608, 3))
        output = output[:600, :600, :]
        output = cv2.GaussianBlur(output, (5, 5), 0)
        return output

    def release_for_next(self):
        self.current_time = 0
        self.event_triggered = False

    def find_contours_and_trigger(self, image):
        v = np.median(image)
        lower = int(max(0, (1.0 - sigma) * v))
        upper = int(min(255, (1.0 + sigma) * v))

        edged = cv2.Canny(image, lower, upper)
        contours = cv2.findContours(edged.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) < 1 or len(contours[0]) < 1:
            return
        # Check only the biggest contour
        contour = sorted(contours[0], key=cv2.contourArea, reverse=True)[:1][0]

        x, y, w, h = cv2.boundingRect(contour)
        trigger = False
        # expect certain size
        if w > 15 and h > 15:
            if self.current_time == 0:
                self.current_time = round(time() * 1000)
                self.event_handler.fire('brick_moving_in')            

            print('Width, Height, Size, X, Y: ', w, h, (w*h), x, y)
            # brick should be completely visible to the camera
            if x == 0:
                print('<<< left border')
            elif x > 0 and (x+w) < 600:
                print('=== center')
                trigger = True
            elif (x+w) >= 600:
                print('>>> right border')
            else:
                print('No clue')

        # throw event with image, but we give the brick time to settle 
        if trigger and round(time() * 1000) > (self.current_time + time_to_rest):
            self.event_triggered = True
            #file_name = './pictures/image_' + str(round(time() * 1000))
            #cv2.imwrite(file_name + '.jpg', image)
            self.event_handler.fire('brick_detected', image)

        # TODO: Error handling in case the brick is at the border

def main():
    cam = Camera()
    cam.start_detection()
    sleep(3)
    cam.stop_detection()


if __name__ == '__main__':
    main()
