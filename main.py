import serial
import time


def InitializeSerial():
    ''' 
    Initialze serial communication with the Arduino.

    Returns: Arduino serial object
    '''
    print('Connecting to Arduino')
    arduino = serial.Serial("/dev/ttyACM0",115200, timeout=.1)
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
    while True:
        command = input("Enter a command: ") # Taking input from user
        WriteArduino(arduino,command)

        #MoveMotors(arduino,(100,200))
        #break



if __name__ == "__main__":
    arduino = InitializeSerial()
    #MoveMotors(arduino,(300,300))
    main(arduino)
    



