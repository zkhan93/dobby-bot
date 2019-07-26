import RPi.GPIO as GPIO
from functools import partial
import threading
from time import sleep


class V_POS(object):
    up = 'up'
    down = 'down'
    vcenter = 'vcenter'


class H_POS(object):
    right = 'right'
    hcenter = 'hcenter'
    left = 'left'


class Camservo(object):

    def __init__(self, pan, tilt):
        self.pan = int(pan)
        self.tilt = int(tilt)
        # create 9 directions
        # ie., combination of 3 position in each x and y direction
        for vp in (V_POS.up, V_POS.down, V_POS.vcenter):
            for hp in (H_POS.right, H_POS.hcenter, H_POS.left):
                setattr(self, vp + hp, partial(self._move, vp, hp))

    def __enter__(self):
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pan, GPIO.OUT)
        GPIO.setup(self.tilt, GPIO.OUT)

        # sleeptime required for harware to move
        self.sleeptime = 0.5  # secs
        freq = 50
        self.panpwm = GPIO.PWM(self.pan, freq)
        self.tiltpwm = GPIO.PWM(self.tilt, freq)

        self.panpwm.start(0)
        self.tiltpwm.start(0)

        return self

    def __exit__(self, exc_type, exc_value, traceback):
        try:
            self.panpwm.stop()
            self.tiltpwm.stop()
            GPIO.cleanup()
        except Exception as ex:
            print('error cleaning up camservo', str(ex))

    def up(self):
        self._setdutycycle(self.tilt, self.tiltpwm, 4.5)

    def down(self):
        self._setdutycycle(self.tilt, self.tiltpwm, 7.5)

    def vcenter(self):
        self._setdutycycle(self.tilt, self.tiltpwm, 9)

    def right(self):
        self._setdutycycle(self.pan, self.panpwm, 3) # 6

    def hcenter(self):
        self._setdutycycle(self.pan, self.panpwm, 7) # 8

    def left(self):
        self._setdutycycle(self.pan, self.panpwm, 12) # 10

    def _move(self, vertical, horizontal):
        if vertical not in ('up', 'down', 'vcenter'):
            return
        if horizontal not in ('right', 'left', 'hcenter'):
            return
        threadname = vertical + horizontal
        t = threading.Thread(target=getattr(self, vertical), name=threadname)
        t.start()
        getattr(self, horizontal)()
        t.join()

    def _setdutycycle(self, pin, pwm, duty):
        GPIO.output(pin, True)
        pwm.ChangeDutyCycle(duty)
        sleep(self.sleeptime)
        GPIO.output(pin, False)
        pwm.ChangeDutyCycle(0)


if __name__== '__main__':
    with Camservo(31, 32) as cs:
        cs.up()
        sleep(1)
        cs.down()
        sleep(1)
        cs.vcenter()
        