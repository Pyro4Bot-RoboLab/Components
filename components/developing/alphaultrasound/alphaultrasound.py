#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import time
from node.libs import control
import Pyro4
from node.libs.gpio.GPIO import *


class ultrasound(control.Control):
    """ RCW-0002 """
    __REQUIRED = ["TRIG", "ECHO", "gpioservice"]

    def __init__(self):
        self.GPIO = GPIOCLS(self.gpioservice, self.pyro4id)
        self.GPIO.setup(self.TRIG, OUT)
        self.GPIO.setup(self.ECHO, IN)

        self.middleDistance = 0
        self.start_worker(self.worker,)

    def worker(self):
        while self.worker_run:
            time.sleep(self.frec)
            self.middleDistance = self.distance()
            # print("MiddleDistance = %0.2f cm" % self.middleDistance)

    def distance(self):
        self.GPIO.output(self.TRIG, HIGH)
        time.sleep(0.000015)
        self.GPIO.output(self.TRIG, LOW)
        while not self.GPIO.input(self.ECHO):
            pass
        t1 = time.time()
        while self.GPIO.input(self.ECHO):
            pass
        t2 = time.time()
        return (t2 - t1) * 34000 / 2

    @Pyro4.expose
    def getDistance(self):
        # print("%0.2f cm" % self.middleDistance)
        return self.middleDistance
