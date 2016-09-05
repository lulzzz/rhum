import serial
import json
import ast
import time

class Arduino:
    def __init__(self, dev='/dev/ttyACM0', baud=38400):
        self.port = serial.Serial(dev, baud)

    def listen(self):
        s = self.port.readline()
        return s

if __name__ == '__main__':
    app = Arduino(dev=d)
    while True:
        try:
            s = app.listen()
            print s
        except KeyboardInterrupt:
            break
        except Exception as e:
            print str(e)
