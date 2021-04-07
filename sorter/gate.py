import RPi.GPIO as GPIO
from time import sleep
from threading import Thread

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Gate(Thread):
    def __init__(self, pin):
        print("Init Gate")
        GPIO.setup(pin, GPIO.OUT)
        self.p = GPIO.PWM(pin, 50)  # PWM with 50Hz
        self.p.start(0)
        self.gate_active = False
        self.thread_running = False
        Thread.__init__(self)

    def start_gate(self):
        print("Start gate")
        self.gate_active = True
        self.thread_running = True
        self.start()

    def stop_gate(self):
        print("Stop gate")
        self.gate_active = False
        self.thread_running = False
        self.p.ChangeDutyCycle(1)
        self.join()
        self.p.ChangeDutyCycle(0)

    def run(self):
        while self.thread_running:
            if self.gate_active:
                self.p.ChangeDutyCycle(3.5)
                sleep(0.3)
                self.p.ChangeDutyCycle(1)
                sleep(1.5)


def main():
    gate = Gate(4)
    gate.start_gate()
    sleep(8)
    gate.stop_gate()
    GPIO.cleanup()


if __name__ == "__main__":
    main()
