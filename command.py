import serial
from time import sleep
#from handOfGod import HandOfGod

# quick sample for sending commands as binary to the arduino
port = serial.Serial('/dev/ttyACM0', 115200);
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

def orbytes(abytes, bbytes):
  return bytes([int(a) | int(b) for a, b in zip(abytes[::-1], bbytes[::-1])][::-1])

# example: command(opcodes["ZERO"], 100)
def command(op, data):
  data_bytes = data.to_bytes(2, 'little');
  packet = orbytes(data_bytes, op);
  port.write(packet);

def send_position(x, y):
  # the arduino is little endian which makes byte stuff slightly unintuitive
  # send the x command
  x_data = x.to_bytes(2, 'little');
  x_packet = orbytes(x_data, opcodes["X"])
  port.write(x_packet);
  print(x_packet.hex())
  # print(f"\"{x_packet.decode('utf-8')}\"")
  # then the y command
  y_data = y.to_bytes(2, 'little');
  y_packet = orbytes(y_data, opcodes["Y"])
  port.write(y_packet);
  print(y_packet.hex())
  # print(f"\"{y_packet.decode('utf-8')}\"")

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
    return y

#zero_packet = bytearray(b'\x5a\x5a')
#print(zero_packet.hex())
#print(zero_packet.decode('utf-8'))
#real_x,real_y = HandOfGod()
#print("real_x: ", real_x, "real_y: ", real_y)
# MoveMotors(arduino,(100,100)) # input the final x y 
#print(real_x, convert(real_x, real_y))
#send_position(int(real_x), int(convert(real_x, real_y))) # input the final x y 


#port.write(bytearray(b'\x00'))
#sleep(5)
#send_position(1,1)
#port.write(zero_packet)
#sleep(15)
#send_position(370,370)
#sleep(5)
#send_position(100,100)
#sleep(5)
#send_position(100, 370)
max_x = 370
max_y = 490
#max_x = 200
#max_y = 200

half_x = max_x // 2;
half_y = max_y // 2;
if __name__ == "__main__":
  send_position(0,0)
  sleep(3)
  send_position(half_x, half_y);
  sleep(3)
  send_position(max_x, max_y);
  sleep(3)
  send_position(half_x, half_y);
  sleep(3)
  send_position(0, max_y);
  sleep(3)
  send_position(half_x, half_y);
  sleep(3)
  send_position(max_x, 0);
  sleep(3)
  send_position(half_x, half_y);
  sleep(3)
  send_position(0, 0);
