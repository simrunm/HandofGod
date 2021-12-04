import serial
import time
from noThreadTest import HandOfGod


def InitializeSerial():
    ''' 
    Initialze serial communication with the Arduino.

    Returns: Arduino serial object
    '''
    print('Connecting to Arduino')
    arduino = serial.Serial("COM8",115200, timeout=.1)
    time.sleep(3)
    print('Connected to Arduino')
    print('To command gantry, first zero axis with [Zero] command, then command location with string [X---Y---]')
    
    return arduino

def WriteArduino(arduino, x):
    '''
    Write serial to Arduino
    '''
    arduino.write(bytes(x, 'utf-8'))

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
    command_location = f'X{location[0]}Y{location[1]}'
    WriteArduino(arduino,command_location)

def main(arduino):
    WriteArduino(arduino,"Zero")
    time.sleep(5) 
    # while True:
    #     command = input("Enter a command: ") # Taking input from user

    #     WriteArduino(arduino,command)

    # real_x,real_y = HandOfGod()
    real_x,real_y = 10,10
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
    



