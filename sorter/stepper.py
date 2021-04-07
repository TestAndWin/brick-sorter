import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
# gpiozero (used in Motor) uses broadcom (BCM) pin numbering

halfstep_seq = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

class Stepper:

    def __init__(self, pin1: int, pin2:int, pin3:int, pin4:int):
        print("Init Stepper")
        self.control_pins = [pin1, pin2, pin3, pin4]
        self.stepper_pos = 0
        for pin in self.control_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)


    def move(self, pos, distance=40):
        print("Move stepper to:", pos)
        self.stepper_pos = self.stepper_pos + pos
        hs = halfstep_seq.copy()
        if pos < 0:
            # reverse for backwards
            hs.reverse()
            pos = pos * -1

        # 4 = je größer, destro größer der Schritt
        for i in range(pos * distance):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(self.control_pins[pin], hs[halfstep][pin])
                time.sleep(0.003)
   
    def cleanup(self):
        GPIO.cleanup()

def main():
    s = Stepper(18, 5, 6, 26)
    #s.move(1)
    #time.sleep(1)
    s.move(-1, 5)
    s.cleanup()


if __name__ == "__main__":
    main()

