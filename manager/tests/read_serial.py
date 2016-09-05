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

    def parse(self, s):
        try:
            msg = ast.literal_eval(s)
            pid = msg['pid']
            chksum1 = msg['chksum']
            data = msg['data']
            chksum2 = self.checksum(data)
            if chksum1 == chksum2 :
                return data
            else:
                return None
        except Exception as e:
            raise e
    
    def checksum(self, data):
        chksum = 0
        try:
            s = str(data)
            s_clean = s.replace(' ', '')
            for i in s_clean:
                chksum += ord(i)
            return chksum % 256
        except Exception as e:
            raise e
    
    def send_command(self, cmd, val):
        out = str(cmd) + str(val) + '\n'
        self.port.write(out)

if __name__ == '__main__':
    d = raw_input('Enter the device name: ')
    app = Arduino(dev=d)
    while True:
        try:
            a = app.listen()
            print a
            res = app.parse(a)
            print res
        except KeyboardInterrupt:
            break
        except Exception as e:
            print str(e)
