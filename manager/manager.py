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
from cherrypy.process.plugins import Monitor
from cherrypy import tools
from itertools import cycle
import tools.CAN as CAN

"""
Manager Class
This class is responsible for acting as the HTTP interface between the remote server and node(s)
"""
class Manager:

    def __init__(self, config=None, log='log.txt'):
        self.workspace = os.path.dirname(os.path.abspath(__file__))
        self.config = config
        self.log = log
        self.threads_active = True
        self.gateway = CAN.Gateway(baud=self.config['gateway_baud'], device=self.config['gateway_device'], use_checksum=self.config['gateway_use_checksum'])
        
        # Initialize Webapp
        self.log_msg('HTTP', 'NOTE: Initializing Run-Time Tasks ...')
        try:
            self.poll_task = Monitor(cherrypy.engine, self.poll, frequency=1/float(self.config['poll_freq'])).subscribe()
        except Exception as error:
            self.log_msg('ENGINE', 'Error: %s' % str(error))

    def log_msg(self, header, msg):
        """
        Saves messages to logfile
        """
        try:
            if self.log is None: raise Exception("Missing error logfile!")
            date = datetime.strftime(datetime.now(), self.config['datetime_format'])
            formatted_msg = "%s\t%s\t%s" % (date, header, msg)
            print formatted_msg
            #with open(os.path.join(self.workspace, self.log), 'w') as error_log:
            #    error_log.write(formatted_msg + '\n')
        except Exception as error:
            print "%s\tLOG\tERROR: Failed to log message!\n" % date

    def poll(self):
        """
        Poll Function
        Threaded function to listen for data from controller and parse it into Python readable info
        Associates each controller event with a datetime stamp
        Dies if threads_active becomes False
        """
        try:
            d = self.gateway.poll() # Grab the latest response from the controller
            if d is not None:
                now = datetime.now()
                datetimestamp = datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S") # grab the current time-stamp for the sample
                d['time'] = datetimestamp
        except Exception as e:
            self.log_msg("", "WARNING: %s" % str(e))

    def close(self):
        pass

    ## Render Index
    @cherrypy.expose
    def index(self, indexfile="index.html", ):
        """
        This function is basically the API
        """
        try:
            indexpath = os.path.join(self.workspace, self.config['cherrypy_path'], indexfile)
            with open(indexpath) as html:
                return html.read()
        except Exception as err:
            self.log_msg("HTTP", "WARNING: %s" % str(err))

    ## Handle Posts
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """
        This function is basically the API
        """
        try:
            url = args[0]
        except Exception as err:
            self.log_msg("HTTP", "WARNING: %s" % str(err))
        return None

    ## CherryPy Reboot
    @cherrypy.expose
    def shutdown(self):
        """
        This function is basically the API
        """
        cherrypy.engine.exit()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        configfile = 'settings.json'
    with open(configfile) as jsonfile:
        config = json.loads(jsonfile.read())
    manager = Manager(config=config)
    cherrypy.server.socket_host = manager.config['cherrypy_address']
    cherrypy.server.socket_port = manager.config['cherrypy_port']
    conf = {
        '/': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, manager.config['cherrypy_path'])},
        '/js': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, manager.config['cherrypy_path'], 'js')},
        '/logs': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, 'logs')},
    }
    cherrypy.quickstart(manager, '/', config=conf)
    manager.close()
    
