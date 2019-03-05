#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# lock().acquire()
# ____________developed by paco andres____________________
import time
from node.libs import control
import Pyro4


class basemotion(control.Control):
    """Movement of wheels through Arduino."""

    __REQUIRED = ["usbserial", "BASE"]

    def __init__(self):
        self.start_subscription("usbserial", "BASE")
        self.set__vel(mi=0, md=0)
        self.start_worker(self.worker)

    def worker(self):
        while self.worker_run:
            # print self.usbserial.get__all()
            time.sleep(self.frec)

    @Pyro4.expose
    @Pyro4.oneway
    @control.flask("actuator")
    def set_vel(self, mi=1, md=1):
        # print "base " + str(mi) + "," + str(md)
        self.usbserial.command(com="base " + str(mi) + "," + str(md))

    @Pyro4.expose
    @control.flask("sensor", 2)
    def get_base(self):
        return self.BASE

    @Pyro4.expose
    def left(self, DC=100):
        self.set_vel(0, DC)

    @Pyro4.expose
    def right(self, DC=100):
        self.set_vel(DC, 0)

    @Pyro4.expose
    def stop(self):
        self.set_vel(0, 0)

    @Pyro4.expose
    def forward(self, DCA=100, DCB=100):
        self.set_vel(DCA, DCB)

    @Pyro4.expose
    def backward(self, DCA=-100, DCB=-100):
        self.set_vel(DCA, DCB)
