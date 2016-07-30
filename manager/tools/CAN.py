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
    def __init__(self, use_checksum=False, timeout=1, baud=38400, device="/dev/ttyACM0"):
        """
        rules : The JSON-like .ctrl file for I/O rules
        """
        try:

            # Get settings
            self.use_checksum = use_checksum
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

    def poll(self, chars=256, force_read=False): 
        try:
            s = self.port.readline()
            msg = self.byteify(json.loads(s)) # parse as JSON
            if self.use_checksum:
                chksum = self.checksum(msg['data'])
                if self.checksum(msg['data']) == msg['chksum']: # run checksum of parsed dictionary
                    return msg # return data if checksum ok
                else:
                    return None # return None if checksum failed
            else:
                return msg
        except Exception as e:
            raise e

    def checksum(self, data, mod=256, force_precision=2):
        """
        Calculate checksum
        """
        chksum = 0
        s = str(data)
        s_clean = s.replace(' ', '')
        for i in s_clean:
            chksum += ord(i)
        return chksum % mod

    def reset(self):
        pass
