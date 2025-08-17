#!/usr/bin/env python

""" X-ray machine Seifert RP149 "driver"

XrayMachine class allows to control X-ray machine installed at CERN.
For more details about iradiation facilty please refer to:
https://espace.cern.ch/project-xrayese/_layouts/15/start.aspx#/
"""
################################################################################
# Author: Szymon Kulis
# Modified by: Giulio Borghello
#
#
#Python script to control the X-Ray Machine at CERN
################################################################################

import os
import math
import serial
import time
import logging

class XrayMachineExceptions(Exception):
    pass

class XrayMachine():
    def __init__(self,port="/dev/ttyUSB2"):
        self.logger = logging.getLogger('XRAY')
        self.logger.info("Opening port '%s'"%port)
        self.port = serial.Serial(
            port=port,
            baudrate=9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout = 0.5
        )

    def __send(self,msg):
        self.logger.debug("Send: '%s'"%(msg))
        self.port.write((msg + "\n").encode())

    def __receive(self,buflen=12):
        msg=self.port.read(buflen)
        msgStr=""
        msg = msg.decode('utf-8')

        for b in msg:
            if ord(b)>32 and ord(b)<128:
                msgStr+=b
            else:
                msgStr+="[0x%02x]"%ord(b)
        self.logger.debug("Recv: '%s'"%(msgStr))
        return msg

    def disconnect(self):
        if self.isContected():
            self.port.close()
            # self.logger.info("Closing port %s"%port)

    def isContected(self):
        if "port" in dir(self):
            return self.port.isOpen()
        return False

    def setHighVoltage(self, hv=30):
        """ Set High Voltage """
        self.logger.info("setHighVoltage : %d [V]"%hv)
        self.__send("SV:%d"%hv)

    def getHighVoltageSetPoint(self):
        """ Read High Voltage set point"""
        self.__send("VN")
        response=self.__receive()
        try:
            hv=int(response[1:11])
            self.logger.info("getHighVoltageSetPoint : %d [V]"%hv)
        except:
            raise XrayMachineExceptions("getHighVoltageSetPoint : unexpected response")
        return hv/1000

    def getHighVoltage(self):
        """ Read actual value of High Voltage """
        self.__send("VA")
        response=self.__receive()
        try:
            hv=int(response[1:11])
            self.logger.info("getHighVoltage : %d [V]"%hv)
        except:
            raise XrayMachineExceptions("getHighVoltage : unexpected response")
        return hv/1000

    def setCurrent(self, cur=10):
        """ Set Tube Current """
        self.logger.info("setCurrent : %d [mA]"%(cur))
        self.__send("SC:%d"%cur)

    def getCurrent(self):
        """ Get Tube Current """
        self.__send("CA")
        response=self.__receive()
        try:
            cur=int(response[1:11])
            self.logger.info("getCurrent : %d [mA]"%cur)
        except:
            raise XrayMachineExceptions("getCurrent : unexpected response")
        return cur/1000

    def getCurrentSetPoint(self):
        """ Get Tube Current Set Point"""
        self.__send("CN")
        response=self.__receive()
        try:
            cur=int(response[1:11])
            self.logger.info("getCurrentSetPoint : %d [mA]"%cur)
        except:
            raise XrayMachineExceptions("getCurrentSetPoint : unexpected response")
        return cur/1000

    def timerOn(self, tn=1):
        """ Exposure timer ON, tn - timer number (integer)"""
        msg="TS:%d"%(tn)
        self.__send(msg)

    def timerOff(self, tn=1):
        """ Exposure timer OFF, tn - timer number (integer)"""
        msg="TE:%d"%(tn)
        self.__send(msg)

    def setTimer(self, time=10, tn=1):
        """ Set timer, time in seconds, tn - timer number (integer)"""
        h=math.floor(time/3600)
        time=time-3600*h
        m=math.floor(time/60)
        time=time-m*60
        s=time
        print("setTimer : %d [s] (h:%d m:%d s:%d)"%(time,h, m, s))
        self.logger.info("setTimer : %d [s] (h:%d m:%d s:%d)"%(time,h, m, s))
        msg="TP:%d,%02d,%02d,%02d"%(tn,h, m, s)
        self.__send(msg)

    def getTimerSetPoint(self, tn=1):
        """ Get timer, tn - timer number (integer)"""
        msg="TN:%d"%(tn)
        self.__send(msg)
        response=self.__receive()
        try:
            timer=int(response[1:11])
        except:
            raise XrayMachineExceptions("getTimer : unexpected response")
        self.logger.info("getTimerSetPoint : %d [s]"%(timer))
        return timer

    def getTimer(self, tn=1):
        """ Get timer, tn - timer number (integer)"""
        msg="TA:%d"%(tn)
        self.__send(msg)
        response=self.__receive()
        try:
            timer=int(response[1:11])
        except:
            raise XrayMachineExceptions("getTimer : unexpected response")
        self.logger.info("getTimer : %d [s]"%(timer))
        return timer

    def openShutter(self, sn=1):
        """ Open Shutter, sn - shutter number (integer 1-4)"""
        msg="OS:%d"%(sn)
        self.__send(msg)

    def closeShutter(self, sn=1):
        """ Close Shutter, sn - shutter number (integer 1-4)"""
        msg="CS:%d"%(sn)
        self.__send(msg)

    def hvEnable(self, s):
        if bool(s):
            self.__send("HV:1")
        else:
            self.__send("HV:0")

    def waitForWarmUp(self, timeStep=1.0):
        """ Wait until tube is ready to work. The state of the tube is polled
            every timeStep expresed in seconds"""
        warmedUp=False
        while not warmedUp:
            time.sleep(timeStep)
            current=self.getCurrent()
            currentSetPoint=self.getCurrentSetPoint()
            highVoltageSetPoint=self.getHighVoltageSetPoint()
            highVoltage=self.getHighVoltage()
            print("Current: ", current, " Current set point: ", currentSetPoint)
            print("Votlage: ", highVoltage, " Voltage set point: ", highVoltageSetPoint)
            if current == currentSetPoint and highVoltage == highVoltageSetPoint:
                warmedUp=True


    def startExposure(self, exposureTime=10):
        self.setTimer(exposureTime)
        self.hvEnable(1)
        self.waitForWarmUp()
        self.openShutter()

    def isExposureFinished(self, tn=1):
        timer = self.getTimer(tn)
        return timer <= 0
