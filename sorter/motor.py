import time
import gpiozero
# gpiozero uses broadcom (BCM) pin numbering


class Motor:
    def __init__(self, pinForward: int, pinBackward: int):
        print("Init Motor")
        self.motor = gpiozero.Motor(pinForward, pinBackward)
        self.status = "s"

    def stop(self):
        self.motor.stop()
        self.status = "s"

    def forward(self, power: float):
        self.motor.forward(power)
        self.status = "r"

    def backward(self, power: float):
        self.motor.backward(power)
        self.status = "b"

def main():
    m = Motor(5,6)   
    m.forward(0.5)
    time.sleep(2)
    m.stop()
    m.backward(0.3)
    time.sleep(2)


if __name__ == "__main__":
    main()

