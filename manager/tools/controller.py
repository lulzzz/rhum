import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys, os
import random

class Controller:
    """
    Controller Class

    SUPPORT:
    JSON-only communication messages.

    FUNCTIONS:
    checksum()
    parse()
    reset()
    """
    def __init__(self, rules='v1', timeout=5):
        """
        rules : The JSON-like .ctrl file for I/O rules
        """
        try:
            if type(rules) == dict:
                self.rules = rules
            else:
                cd = os.getcwd()
                configpath = os.path.join(cd, 'controllers', rules, rules + '.ctrl')
                with open(configpath) as jsonfile:
                    self.rules = self.byteify(json.loads(jsonfile.read()))
            
            # Get MCU settings
            self.mcu_checksum = self.rules['mcu_checksum']
            self.mcu_device = self.rules['mcu_device']
            self.mcu_baud = self.rules['mcu_baud']
            self.mcu_rules = self.rules['mcu_rules']

            # Get Lights settings
            self.lights_model = self.rules['lights_model']
            self.lights_device = self.rules['lights_device']
            self.lights_baud = self.rules['lights_baud']
            self.lights_rules = self.rules['lights_rules']
            self.percent = 0 # default lights to 0

        except Exception as e:
            raise e

        ## Connect to MCU
        try:
            self.mcu_port = serial.Serial(self.mcu_device, self.mcu_baud, timeout=timeout)
        except Exception as e:
            self.mcu_port = None
            raise Exception("Failed to attach MCU!")

        ## Connect to Lights
        try:
            self.lights_port = Lamp(self.lights_device, self.lights_baud, timeout=timeout)
        except Exception as e:
            self.lights_port = None
            raise Exception("Failed to attach Lights!")
            

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
            s = self.mcu_port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
            print("SERIAL_READ: %s" % s.strip('\n')) #!DEBUG
            d = json.loads(s) # parse as JSON
            if self.checksum(d): # run checksum of parsed dictionary
                return d # return data if checksum ok
            else:
                return None # return None if checksum failed
        except Exception as e:
            return None

    def set_params(self, params):
        """
        Set the target values of the controller
        This checks the .ctrl rules file for each of the defined rulesets
        The named values in params are those which are passed either by the GUI or the remote host

        Currently supported rules
            * SETPOINT - Simply send the named value to the controller
            * IN_RANGE - Compare two values, if input value is within that range send 1, else send 0
        """
        now = datetime.now()
        hours_since_midnight = (now - now.replace(hour=0, minute=0, second=0, microsecond=0)).total_seconds() / 3600.0
        params['time'] = hours_since_midnight
        params = {k.encode('ascii'): v for (k, v) in params.items()} # ensure dict is in ASCII encoding
        
        # Set output based on MCU rules
        targets = dict()
        for k,r in self.mcu_rules.iteritems():
            try:
                # Check each rules "type", and then set the target value based on the input values
                if r[0] == "SETPOINT": 
                    targets[k] = int(params[r[1]])
                if r[0] == "IN_RANGE": 
                    limit_max = params[r[3]]
                    limit_min = params[r[2]]
                    metric = params[r[1]]
                    if (metric < limit_max) and (metric > limit_min):
                        targets[k] = 1
                    else:
                        targets[k] = 0
                else:
                    raise Exception("Unrecognized rule for MCU! Check .ctrl file")
            except:
                pass

        # Send parameters to MCU
        print("MCU TARGETS: %s" % str(targets))
        s = json.dumps(targets)
        s.replace(' ', '') # remove whitespace for serial transmission
        self.mcu_port.write(s)

        # Set output based on lights rules
        # This rules are ANDs, so if any of them are zero, they default to zero
        try:
            # Check each rules "type", and then set the target value based on the input values
            limit_min = params[self.lights_rules['on']]
            limit_max = params[self.lights_rules['off']]
            metric = params[self.lights_rules['time']]
            threshold = params[self.lights_rules['threshold']]
            reference = params[self.lights_rules['reference']]
            output = params[self.lights_rules['output']]
            if (metric < limit_max) and (metric > limit_min):
                if (reference < threshold):
                    if (self.percent < output):
                        self.percent += 1
                    else:
                        self.percent = output
                else:
                    self.percent -= 1 # if over the threshold level, fade until at level
            else:
                self.percent = 0
            print limit_min, limit_max, reference, threshold, output
        except:
            raise Exception("Unable to determine rule for lights! Check .ctrl file")

        # Send parameters to lights
        print("OVERHEAD LEVEL: %s" % str(self.percent))
        for c in [1,2,3,4]:
            self.lights_port.set_channel(c, self.percent)
        return s

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


class Lamp:
    """
    Special Serial class
    """

    def __init__(self, device, baud, timeout="1"):
        """
        Initialize connection in Manual Mode
        """
        self.port = serial.Serial(device, baud, timeout=timeout)
        self.manual_mode_command = "%d:%d s lamp.manual %d%%\r"

    def set_channel(self, channel, percent, group=1):
        """
        Set a particular channel of the lamp module to a percent level
        Channels
        """
        if percent > 100:
            percent = 100
        elif percent < 0:
            percent = 0
        if channel > 4 or channel < 1:
            raise Exception("Channel not recognized! Device only suppors channels 1-4")
        command = self.manual_mode_command % (group, channel, percent)
        self.port.write(command)
