import serial
import sys
import json

timeout=5
baud = 9600
device = sys.argv[1]

port = serial.Serial(device, baud, timeout=timeout)
while True:
    try:
         s = port.readline() #!TODO Need to handle very highspeed controllers, i.e. backlog
         d = json.loads(s)  
         print d
    except KeyboardInterrupt: break
    except Exception as e: print str(e)

