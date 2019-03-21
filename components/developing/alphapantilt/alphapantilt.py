#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ____________developed by paco andres____________________
# _________collaboration with cristian vazquez____________
# All data defined in json configuration are attributes in your code object
import time
from node.libs import control
import Pyro4
from node.libs.gpio.GPIO import *

@Pyro4.expose
class alphapantilt(control.Control):
    __REQUIRED = ["PAN", "TILT", "gpioservice"]

    def __init__(self):
        # TODO: With service
        # self.GPIO = GPIOCLS(self.gpioservice, self.pyro4id)
        # self.GPIO.setup(self.TILT, OUT)
        # self.GPIO.setup(self.PAN, OUT)
        # self.cpan = self.GPIO.PWM(self.PAN, 50)
        # self.ctilt = self.GPIO.PWM(self.TILT, 50)
        # self.cpan.start(50)
        # self.ctilt.start(50)
        # self.set_pantilt(50,120)

        # self.set_angle(self.PAN, self.cpan, 180)
        # self.set_angle(self.TILT, self.ctilt, 180)

        self.ptblock = False
        self.bar = False

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.PAN, GPIO.OUT)
        GPIO.setup(self.TILT, GPIO.OUT)

        self.cpan = GPIO.PWM(self.PAN, 50)
        self.ctilt = GPIO.PWM(self.TILT, 50)

        self.pan_a = 105
        self.tilt_a = 120

        self.set_pantilt(self.pan_a, self.tilt_a)

    @control.flask("actuator")
    @Pyro4.oneway
    def set_pantilt(self, pan=105, tilt=120):
        # print("pan", pan, "tilt", tilt)
        self.pan_a = pan
        self.tilt_a = tilt
        self.ctilt.start(50)
        self.cpan.start(50)
        self.cpan.ChangeDutyCycle(12.5 - 10.0 * float(self.pan_a) / 180)
        self.ctilt.ChangeDutyCycle(12.5 - 10.0 * float(self.tilt_a) / 180)
        time.sleep(0.5)
        self.ctilt.start(0)
        self.cpan.start(0)
        # self.cpan.stop()
        # self.ctilt.stop()

    @control.flask("sensor", 2)
    def get_pantilt(self):
        return self.pan_a, self.tilt_a

    @Pyro4.oneway
    @control.flask("actuator")
    def move(self, pan=40, tilt=90):
        if pan < 10:
            pan = 10
        elif pan > 120:
            pan = 120
        if tilt < 15:
            tilt = 15
        elif tilt > 140:
            tilt = 140
        if self.ptblock is False:
            self.set_pantilt(pan, tilt)
            while self.pan_a != pan and self.tilt_a != tilt:
                # print("Waiting for servo...")
                self.ptblock = True
            self.ptblock = False

    @Pyro4.oneway
    @control.flask("actuator")
    def sweep(self, i, f):
        if not self.bar:
            self.bar = True
            for l in range(i, f, 1):
                self.move(l, 120)
                time.sleep(0.005)
            self.bar = False
