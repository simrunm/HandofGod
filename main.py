import serial
import time
from noThreadTest import HandOfGod


def InitializeSerial():
    ''' 
    Initialize serial communication with the Arduino.

    Returns: Arduino serial object
    '''
    print('Connecting to Arduino')
    arduino = serial.Serial("COM8",115200, timeout=.1)
    time.sleep(3)
    print('Connected to Arduino')
    print('To command gantry, first zero axis with [Zero] command, then command location with string [X---Y---]')
    
    return arduino

def ORbytes(abytes, bbytes):
    '''
    Bitwise OR for two bytearrays.

    Args:
        abytes: a bytearray
        bbytes: another bytearray
    Returns:
        a byte array with the result
    '''
    return bytes([int(a) | int(b) for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])


# this has to be manually synced with the firmware if the opcodes are changed
opcodes = {
  "ZERO":  b'\x00\x00',
  "T+X":   b'\x00\x10',
  "T+Y":   b'\x00\x20',
  "T-X":   b'\x00\x30',
  "T-Y":   b'\x00\x40',
  "X":     b'\x00\x50',
  "Y":     b'\x00\x50',
  "READY": b'\x00\x70',
}

def ReadArduino(arduino):
    data = arduino.readline()
    return data


def MoveMotors(arduino, location: tuple):
    ''' 
    Send a command to the arduino to move the motors to a location

    Args:
        Tuple (X,Y) for where to move gantry

    Returns:
        NONE
    '''
    # the arduino is little endian which makes byte stuff slightly unintuitive
    # send the x command
    x_data = location[0].to_bytes(2, 'little');
    x_packet = ORbytes(x_data, opcodes["X"])
    arduino.write(x_packet);
    # then the y command
    y_data = location[1].to_bytes(2, 'little');
    y_packet = ORbytes(y_data, opcodes["Y"])
    arduino.write(y_packet);

def main(arduino):
    # the zero command is just two bytes of 0s
    arduino.write(bytearray(b'\x00x00'))
    time.sleep(5) 
    # while True:
    #     command = input("Enter a command: ") # Taking input from user

    #     WriteArduino(arduino,command)

    real_x,real_y = HandOfGod()
    # print(real_x, real_y)
    MoveMotors(arduino,convert(real_x,real_y)) # input the final x y 
        #break

def convert(x,y):
    """
    Convert from real life x and y distance to x, y coordinate on the gantry.

    gantry dimensions:
    370, 410 origin in bottom right corner
    460mm, 500mm

    distance from sideframe edge to gantry 550mm
    """
    y = y - 550
    y = y * (410/500)
    print(x,y)
    return 100,100

if __name__ == "__main__":
    arduino = InitializeSerial()
    #MoveMotors(arduino,(300,300))
    main(arduino)
    



