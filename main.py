import serial
import time
from tqdm import tqdm


def InitializeSerial():
    ''' 
    Initialize serial communication with the Arduino.

    Returns: Arduino serial object
    '''
    #arduino = serial.Serial("/dev/ttyACM0",115200, timeout=.1)
    arduino = serial.Serial("COM8",115200, timeout=.1)
    for i in tqdm(range(100), ascii= "---------#", desc = 'Connecting to Arduino'):
        time.sleep(.025)
   
    
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
  "Y":     b'\x00\x60',
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

def convert(x,y):
    """
    Convert from real life x and y distance to x, y coordinate on the gantry.

    gantry dimensions:
    370, 410 origin in bottom right corner
    460mm, 500mm

    distance from sideframe edge to gantry 620*2=1240
    """
    y = y - 1240
    y = y * (410/500)
    print("converted x: ", x, "converted y: ", y)
    return 100,100

def main():
    arduino = InitializeSerial()
    # the zero command is just two bytes of 0s
    arduino.write(bytearray(b'\x00\x00'))
    time.sleep(6) 
    
    
    #moves it to the center
    MoveMotors(arduino,(185,205))
    time.sleep(1)
    print('Axis zeroed and gantry centered')

    # real_x = int(input("X: "))
    # real_y = int(input("Y: "))
    # MoveMotors(arduino,(real_x,real_y))

    real_x,real_y = HandOfGod()
    print("real_x: ", real_x, "real_y: ", real_y)
    print("time before movemotors: ", time.time())
    MoveMotors(arduino,convert(real_x, real_y)) # input the final x y 
        #break
    print("time after movemotors: ", time.time())
    

# if __name__ == "__main__":
#     main()
