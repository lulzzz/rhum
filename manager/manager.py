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
import tools.DB as DB
import fnmatch
import re

"""
Manager Class
This class is responsible for acting as the HTTP interface between the remote server and node(s)
"""
class Manager:

    def __init__(self, config=None, log='errors.txt'):
        try:
            self.config = config
            self.workspace = os.path.dirname(os.path.abspath(__file__))
            self.logs_directory = os.path.join(self.workspace, self.config['cherrypy_path'], 'logs')
            self.logfile = os.path.join(self.logs_directory, log)
            with open(self.logfile, 'w') as log:
                pass
            self.log_msg('CANBUS', 'NOTE: Initializing Log-file ...')
            self.poll_bad_counter = 0
            self.poll_ok_counter = 0
            self.poll_nodata_counter = 0
            self.active_nodes = []
        except Exception as error:
            self.log_msg('ENGINE', 'ERROR: %s' % str(error))

        try:
            self.log_msg('CANBUS', 'NOTE: Initializing CANBUS ...')
            self.gateway = CAN.Gateway(baud=self.config['gateway_baud'], device=self.config['gateway_device'], use_checksum=self.config['gateway_use_checksum'])
        except Exception as error:
            self.gateway = None
            self.log_msg('CANBUS', 'ERROR: %s' % str(error))
        if self.gateway is None: self.log_msg('CANBUS', 'ERROR: No CAN Gateway found! Check the connection in the Manager!')

        try:
            self.log_msg('DB    ', 'NOTE: Initializing Database ...')
            self.database = DB.NodeDB(port=self.config['db_port'], address=self.config['db_address'], name=self.config['db_name'])
        except Exception as error:
            self.database = None
            self.log_msg('DB    ', 'ERROR: %s' % str(error))
        if self.database is None: self.log_msg('DB    ', 'Error: Database failed to attached!')

        # Initialize Webapp
        self.log_msg('HTTP  ', 'NOTE: Initializing Run-Time Tasks ...')
        try:
            self.log_msg('CANBUS', 'NOTE: Polling frequency set to: %d Hz' % float(self.config['poll_freq_hz']))
            self.poll_task = Monitor(cherrypy.engine, self.poll, frequency=1/float(self.config['poll_freq_hz'])).subscribe()
            self.log_msg('CANBUS', 'NOTE: Auto-clean interval set to: %2.1f hours' % float(self.config['clean_freq_hours']))
            self.clean_task = Monitor(cherrypy.engine, self.clean, frequency=float(3600 * self.config['clean_freq_hours'])).subscribe()
            self.log_msg('CANBUS', 'NOTE: Auto-clean cut-off period set to: %d days' % self.config['db_cutoff_days'])
            """
            TODO: Additional scheduled tasks for network maintenance?
            """
        except Exception as error:
            self.log_msg('HTTP  ', 'ERROR: %s' % str(error))

    def log_msg(self, header, msg):
        """
        Saves messages to logfile
        """
        try:
            if self.logfile is None: raise Exception("Missing error logfile!")
            date = datetime.strftime(datetime.now(), self.config['datetime_format'])
            formatted_msg = "%s %s %s" % (date, header, msg)
            print formatted_msg
            with open(self.logfile, 'a') as log:
                log.write(formatted_msg + '\n')
        except Exception as error:
            print "FATAL ERROR: Failed to log message!\n"

    def poll(self):
        """
        Poll Function
        Threaded function to listen for data from controller and parse it into Python readable info
        Associates each controller event with a datetime stamp
        """
        if self.gateway is not None:
            try:
                d = self.gateway.poll() # Grab the latest response from the controller
                if d is not None:
                    self.poll_nodata_counter = 0
                    self.poll_ok_counter += 1
                    self.database.store(d)
                    uid = format(d['nt'], '02x') + '-' + format(d['sn'], '02x') + '-' + format(d['id'], '02x')
                    self.active_nodes.append(uid)
                else:
                    self.poll_bad_counter += 1
            except ValueError as e:
                self.poll_nodata_counter += 1 # This error occurs when there was no data available from the CAN Gateway, and can be ignored (to a limit)
                if self.poll_nodata_counter == self.config['poll_nodata_limit']:
                    self.log_msg("CANBUS", "WARNING: %d iterations without new data! Check Manager's connection to Nodes!" % self.poll_nodata_counter)
                    self.poll_nodata_counter = 0
            except Exception as e:
                self.poll_bad_counter += 1
                self.log_msg("CANBUS", "ERROR: %s" % str(e))
        else:
            self.poll_bad_counter += 1
        if self.poll_bad_counter + self.poll_ok_counter == self.config['poll_samples']:
            self.log_msg("CANBUS", "NOTE: Gateway read-failure rate: %d out of %d" % (self.poll_bad_counter, self.poll_ok_counter + self.poll_bad_counter))
            if self.poll_bad_counter == self.poll_ok_counter:
                self.log_msg("CANBUS", "WARNING: No messages on BUS! Check connection to the Gateway!")
            self.log_msg("CANBUS", "NOTE: Active nodes: %s" % str(list(set(self.active_nodes))))
            self.poll_bad_counter = 0
            self.poll_ok_counter = 0
            self.active_nodes = []

    def clean(self):
        try:
            self.log_msg("DB    ", "WARNING: Executing scheduled DB clean-up ...") 
            docs_deleted = self.database.clean(cutoff_days=self.config['db_cutoff_days'])
            self.log_msg("DB    ", "NOTE: Deleted: %d docs" % docs_deleted)
        except Exception as e:
            self.log_msg("DB    ", "ERROR: %s" % str(e))

    def close(self):
        pass

    ## Render Index
    @cherrypy.expose
    def index(self, indexfile="index.html"):
        """
        This function is basically the API
        """
        try:
            indexpath = os.path.join(self.workspace, self.config['cherrypy_path'], indexfile)
            with open(indexpath, 'r') as html:
                return html.read()
        except Exception as err:
            self.log_msg("HTTP  ", "WARNING: %s" % str(err))

    ## Handle Posts
    @cherrypy.expose
    def default(self, *args, **kwargs):
        """
        This function is basically the API
        """
        try:
            if args[0] == 'regen':
                try:
                    self.log_msg("HTTP  ", "NOTE: Request to regenerate CSV for: %s days" % args[1])
                    a = time.time()
                    self.database.dump_csv(os.path.join(self.logs_directory, 'data-' + str(args[1]) + '.csv'), days=int(args[1]))
                    b = time.time()
                    self.log_msg("HTTP  ", "NOTE: CSV generation complete! Took %d ms" % int((b - a) * 1000)) 
                except Exception as e:
                    self.log_msg("DB    ", "ERROR: %s" % str(e))
            elif args[0] == 'clean':
                try:
                    self.log_msg("HTTP  ", "NOTE: Request to clean DB data older than: %s days" % args[1])
                    docs_deleted = self.database.clean(cutoff_days=int(args[1]))
                    self.log_msg("DB    ", "NOTE: Deleted: %d docs" % docs_deleted)
                except Exception as e:
                    self.log_msg("DB    ", "ERROR: %s" % str(e))
            elif args[0] == 'cordova.js':
                self.log_msg("HTTP  ", "NOTE: Rendering App with Cordova.js ... ")
            elif args[0] == 'config':
                self.log_msg("HTTP  ", "NOTE: Loading App config ... ")
            else:
                self.log_msg("HTTP  ", "WARNING: No API handler for: %s" % str(args[0]))
        except Exception as err:
            self.log_msg("HTTP  ", "ERROR: %s" % str(err))
        return None

    ## CherryPy Reboot
    @cherrypy.expose
    def shutdown(self):
        """
        This function is basically the API
        """
        self.log_msg("HTTP  ", "WARNING: Executing shutdown of CherryPy3 Server!")
        cherrypy.engine.exit()
    
if __name__ == '__main__':
    if len(sys.argv) > 1:
        configfile = sys.argv[1]
    else:
        configfile =  os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')
    with open(configfile) as jsonfile:
        config = json.loads(jsonfile.read())
    manager = Manager(config=config)
    cherrypy.server.socket_host = manager.config['cherrypy_address']
    cherrypy.server.socket_port = manager.config['cherrypy_port']
    conf = {
        '/': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, manager.config['cherrypy_path'])},
        '/js': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, manager.config['cherrypy_path'], 'js')},
        '/logs': {'tools.staticdir.on':True, 'tools.staticdir.dir':os.path.join(manager.workspace, manager.config['cherrypy_path'], 'logs')},
    }
    cherrypy.quickstart(manager, '/', config=conf)
    manager.close()
    
