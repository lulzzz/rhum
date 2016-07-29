import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys, os
import random

class Gateway:
    """
    Controller Class

    SUPPORT:
    JSON-only communication messages.

    FUNCTIONS:
    checksum()
    parse()
    reset()
    """
    def __init__(self, timeout=5, checksum=True, baud=38400, device="/dev/ttyACM0"):
        """
        rules : The JSON-like .ctrl file for I/O rules
        """
        try:

            # Get settings
            self.checksum = checksum
            self.device = device
            self.baud = baud
            self.timeout = timeout

        except Exception as e:
            raise e

        ## Connect to MCU
        try:
            self.port = serial.Serial(self.device, self.baud, timeout=self.timeout)
        except Exception as e:
            self.port = None
            raise Exception("Failed to attach MCU!")
            

    def byteify(self, input):
        if isinstance(input, dict):
            return {self.byteify(key) : self.byteify(value) for key,value in input.iteritems()}
        elif isinstance(input, list):
            return [self.byteify(element) for element in input]
        elif isinstance(input, unicode):
            return input.encode('utf-8')
        else:
            return input

    def parse(self, interval=1.0, chars=256, force_read=False): 
        try:
            s = self.port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
            print("SERIAL_READ: %s" % s.strip('\n')) #!DEBUG
            d = json.loads(s) # parse as JSON
            if self.checksum(d): # run checksum of parsed dictionary
                return d # return data if checksum ok
            else:
                return None # return None if checksum failed
        except Exception as e:
            return None

    def checksum(self, d, mod=256):
        """
        Calculate checksum
        """
        chksum = 0
        s = str(d)
        s_clean = s.replace(' ', '')
        for i in s_clean:
            chksum += ord(i)
        return chksum % mod

    def reset(self):
        pass
