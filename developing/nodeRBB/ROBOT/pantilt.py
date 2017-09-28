#!/usr/bin/env python
# -*- coding: utf-8 -*-
#lock().acquire()
#____________developed by paco andres____________________
import time
from nodeRBB.LIBS import control,utils
import Pyro4

@Pyro4.expose
class pantilt(control.control):
    @control.loadconfig
    def __init__(self,data,**kwargs):
        self.send_subscripcion(self.arduino,"PT")
        self.bar=False
        self.ptblock=False
        super(pantilt,self).__init__(self.worker)

    def worker(self):
        while self.worker_run:
            #write here code for your sensor

            time.sleep(self.frec)
    @Pyro4.oneway
    def move(self,pan=90,tilt=90):
      if self.ptblock==False:
        self.arduino.command("setpt "+str(pan)+","+str(tilt))
        while self.PT[0]!=pan and self.PT[1]!=tilt:
            print "wait servo"
            self.ptblock=True
        self.ptblock=False
    @Pyro4.oneway
    def barrido(self,i,f):
        if not self.bar:
          self.bar=True
          for l in range(i,f,1):
              self.move(l,120)
              time.sleep(0.05)
          self.bar=False
    def get_pantilt(self):

        return self.PT

if __name__ == "__main__":
    pass
