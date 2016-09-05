import serial
import json
import ast
import time

class Arduino:
    def __init__(self, dev='/dev/ttyACM0', baud=9600):
        self.port = serial.Serial(dev, baud)

    def listen(self):
        s = self.port.readline()
        return s
    
    def send_command(self, cmd, val):
        out = str(cmd) + str(val) + '\n'
        self.port.write(out)

if __name__ == '__main__':
    d = raw_input('Enter the device name: ')
    app = Arduino(dev=d)
    while True:
        try:
            s = app.listen()
            print s
        except KeyboardInterrupt:
            break
        except Exception as e:
            print str(e)
