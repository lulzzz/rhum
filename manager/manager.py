#!/usr/bin/env python
import json
import requests
import threading
import time
from datetime import datetime
import serial
import sys, os
import random
import cherrypy
from itertools import cycle
import tools.CAN as CAN

"""
Manager Class
This class is responsible for acting as the HTTP interface between the remote manager (and/or local GUI) and controller(s)
"""
class Manager:

    def __init__(self, config=None, log='log.txt'):
        self.config = config
        self.log = open(log, 'w')
        self.threads_active = True
        self.gateway = CAN.Gateway()
        threading.Thread(target=self.watchdog, args=(), kwargs={}).start()
    
    def log_msg(self, msg):
        print msg
        self.log.write(msg + '\n')

    def watchdog(self):
        """
        WatchDog Function
        Threaded function to listen for data from controller and parse it into Python readable info
        Associates each controller event with a datetime stamp
        Dies if threads_active becomes False
        """
        while self.threads_active == True:
            try:
                d = self.gateway.poll() # Grab the latest response from the controller
                if d is None:
                    self.log_msg("CHECKSUM: FAILED")
                else:
                    self.log_msg("CHECKSUM: OK")
                    now = datetime.now()
                    datetimestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") # grab the current time-stamp for the sample
                    d['time'] = datetimestamp
            except Exception as e:
                self.log_msg(str(e))
                raise e

    def push_to_remote(self, d):
        """
        Push current local settings to the remote manager
        Arguments:
            dict
        Returns:
            tuple of (code, msg)
        """
        try:
            r = None
            d['uid'] = self.config['UID']
            d['node_type'] = self.config['CTRL_CONF']
            addr = self.config['SERVER_ADDR']
            r = requests.post(addr, json=d)
            return (r.status_code, r.json())
        except Exception as e:
            if r is not None:
                return (r.status_code, r.reason)
            else:
                return (400, 'Lost server')

    def run(self, queue_limit=16, error_limit=None, gui=False, freq=1):
        """
        Run node as HTTP daemon

        Notes:
            * Node-App configuration is Push-Pull
            * For each iteration, the latest data gathered from the Controller is pushed from the Queue
            * Data is pushed to the App via HTTP Post to SERVER_ADDR
            * If the App has a task waiting, the task is returned as the response to the POST
        """
        if self.config['GUI']:
            # Select GUI by controller type
            if self.config['CTRL_CONF'] == 'v1':
                self.gui = rhumGUI.GUI_v1()
            if self.config['CTRL_CONF'] == 'bronfman':
                self.gui = rhumGUI.GUI_bronfman()
            else:
                self.log_msg("GUI not found for \"%s\" configuration." % (self.config['CTRL_CONF']))
                self.threads_active = False
                exit(0)
            # If GUI started successfully, run as thread
            if self.gui:
                self.gui.start()   

        # Wait for values to get set
        time.sleep(5)
        
        try:
            while ((len(self.remote_queue) < error_limit) or (error_limit is None)) and self.threads_active:
                
                # Wait for next event
                time.sleep(1 / float(freq)) # slow down everyone, we're moving too fast

                # Handle GUI
                # Retrieve local changes to targets (overrides remote)
                if (self.gui is not None):
                    gui_targets = self.gui.get_values() #!TODO Resolve multiple sources for setting targets, GUI should override
                    current_params = self.controller.set_params(gui_targets)
                
                # Handle controller queue
                while len(self.controller_queue) > queue_limit:
                    self.controller_queue.pop(0) # grab from out-queue
                num_samples = len(self.controller_queue)
                if num_samples > 0:
                    self.log_msg("MCU QUEUE LENGTH: %d" %  num_samples)
                    try:
                        sample = self.controller_queue.pop()
                        self.log_msg("SAMPLE: %s" % str(sample))
                        response = self.push_to_remote(sample) # SEND TO REMOTE
                        if (self.gui is not None):
                            try:
                                sample['data']
                                self.gui.update_values(sample['data'])
                            except:
                                pass
                        if response is not None:
                            self.remote_queue.append(response)
                    except Exception as e:
                        self.log_msg(str(e))
                        raise e

                # Handled accrued responses/errors
                num_responses = len(self.remote_queue)
                if num_responses > 0:
                    for resp in self.remote_queue:
                        self.log_msg("REMOTE QUEUE LENGTH: %d" % num_responses)
                        self.log_msg("RESPONSE: %s" % str(resp))
                        response_code = resp[0]
                        if response_code == 200:
                            self.remote_queue.pop()
                            target_values = resp[1]['targets']
                            if target_values is not None:
                                try:
                                    self.controller.set_params(target_values) # send target values within response to controller
                                    self.gui.settings.update(target_values) #!TODO Dangerous way to update GUI from remote
                                except Exception as e:
                                    self.log_msg(str(e))
                                self.controller_queue = []
                        if response_code == 400: 
                            self.remote_queue.pop() #!TODO bad connection!
                        if response_code == 500:
                            self.remote_queue.pop() #!TODO server there, but uncooperative!
                        if response_code is None:
                            self.remote_queue.pop()
                        else:
                            pass #!TODO Unknown errors!

        except KeyboardInterrupt:
            self.log_msg("\nexiting...")
            self.threads_active = False
            exit(0)
        except Exception as e:
            self.log_msg(str(e))
            self.threads_active = False
            exit(0)

    ## Render Index
    @cherrypy.expose
    def index(self, indexfile="index.html", ):
        indexpath = os.path.join(self.CURRENT_DIR, self.config['CHERRYPY_PATH'], indexfile)
        with open(indexpath) as html:
            return html.read()

    ## Handle Posts
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """
        This function is basically the API
        """
        try:
            url = args[0]
        except Exception as err:
            self.log_msg('ERROR', str(err), important=True)
        return None

    ## CherryPy Reboot
    @cherrypy.expose
    def shutdown(self):
        cherrypy.engine.exit()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        configfile = 'default.cfg'
    with open(configfile) as jsonfile:
        config = json.loads(jsonfile.read())
    node = Manager(config=config)
    node.run() # quickstart as daemon
    
