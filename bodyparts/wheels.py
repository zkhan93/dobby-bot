
import RPi.GPIO as GPIO
import time
from collections import namedtuple


class Wheels(object):
    def __init__(self, right_forward, right_back, left_forward, left_back):
        self.WheelSet = namedtuple('WheelSet', 'forward back')
        self.wheels_right = self.WheelSet(right_forward, right_back)
        self.wheels_left = self.WheelSet(left_forward, left_back)
        self.pins = self.wheels_right + self.wheels_left

    def __enter__(self):
        GPIO.setmode(GPIO.BOARD)
        for pin in self.pins:
                GPIO.setup(pin, GPIO.OUT)
        return self

    def move_forward(self, sec=1):
        ''' signal both set of wheels to move forward for time seconds '''
        GPIO.output(self.wheels_right.forward, True)
        GPIO.output(self.wheels_left.forward, True)
        time.sleep(sec)
        GPIO.output(self.wheels_right.forward, False)
        GPIO.output(self.wheels_left.forward, False)

    def move_back(self, sec=1):
        ''' signal both set of wheels to move back for time seconds '''
        GPIO.output(self.wheels_right.back, True)
        GPIO.output(self.wheels_left.back, True)
        time.sleep(sec)
        GPIO.output(self.wheels_right.back, False)
        GPIO.output(self.wheels_left.back, False)

    def turn_right(self, sec=1.5):
        ''' signal both set of wheels to move back for time seconds '''
        GPIO.output(self.wheels_right.forward, True)
        time.sleep(sec)
        GPIO.output(self.wheels_right.forward, False)

    def turn_left(self, sec=1.5):
        ''' signal both set of wheels to move back for time seconds '''
        GPIO.output(self.wheels_left.forward, True)
        time.sleep(sec)
        GPIO.output(self.wheels_left.forward, False)

    def turn_half_left(self):
        self.turn_left(0.5)

    def turn_34_left(self):
        self.turn_left(0.75)

    def turn_half_right(self):
        self.turn_right(0.5)

    def turn_34_right(self):
        self.turn_right(0.75)

    def __exit__(self, exc_type, exc_value, traceback):
            GPIO.cleanup()


if __name__ == '__main__':
    # TODO: Make PINS configurable from web
    with Wheels(35, 36, 37, 38) as wheels:
        moves = (' move_forward turn_right ' * 4).split()
        for move in moves:
            print(move)
            getattr(wheels, move)()
            print('done', move)
