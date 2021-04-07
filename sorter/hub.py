import RPi.GPIO as GPIO
import time

# gpiozero (used in Motor) uses broadcom (BCM) pin numbering
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)


class Hub:
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

    current_hub_pos = 0

    def __init__(self, pin1: int, pin2: int, pin3: int, pin4: int):
        print("Init Hub")
        self.hub_control_pins = [pin1, pin2, pin3, pin4]
        for pin in self.hub_control_pins:
            GPIO.setup(pin, GPIO.OUT)
            GPIO.output(pin, 0)

    def move(self, slot: int):
        if slot > 9:
            print("Slot is out of range")
            return

        print("Move hub to slot: ", slot)

        hs = self.halfstep_seq.copy()

        if slot >= 0:
            hub_move = self.current_hub_pos - slot
            self.current_hub_pos = slot
            if hub_move < 0:
                # reverse for backwards
                hs.reverse()
                hub_move = hub_move * -1
        else:
            # In case the hub must re-positioned
            hub_move = slot * -1

        for i in range(hub_move * 32):
            for halfstep in range(8):
                for pin in range(4):
                    GPIO.output(self.hub_control_pins[pin], hs[halfstep][pin])
                time.sleep(0.003)


def main():
    hub = Hub(27, 22, 23, 24)

    hub.move(0)
    time.sleep(1)
    hub.move(1)
    time.sleep(1)
    hub.move(2)
    time.sleep(1)
    hub.move(3)
    time.sleep(1)
    hub.move(4)
    time.sleep(1)
    hub.move(5)
    time.sleep(1)
    hub.move(6)
    time.sleep(1)
    hub.move(7)
    time.sleep(1)
    hub.move(8)
    time.sleep(1)
    hub.move(0)
    GPIO.cleanup()


if __name__ == "__main__":
    main()
