// Main Arduino Code for Hand of God PIE Project
// Allows for gantry to move to any spot given a serial input
// Allows for zeroing of axis at begining
// Authors: Elvis Wolcott, Chris Allum



#include <SpeedyStepper.h>

// uncomment to enable debug printing
#define DEBUG

// command definitions
// bitmasks for commands
#define OPCODE_MASK      0xF
#define DATA_MASK     0x0FFF
// opcodes:
//    * 0x0: zero     (no data)
//    * 0x1: tension +x (steps)
//    * 0x2: tension +y (steps)
//    * 0x3: tension -x (steps)
//    * 0x4: tension -y (steps)
//    * 0x5: move to x  (steps)
//    * 0x6: move to y  (steps)
//    * 0x7: ready    (no data)
//    * 0x8-0xF:       (unused)
enum opcode {
  C_ZERO,
  C_TENSION_X_P,
  C_TENSION_X_N,
  C_TENSION_Y_P,
  C_TENSION_Y_N,
  C_MOVE_X,
  C_MOVE_Y,
  C_READY,
};

char opcode;
short data;
short buffer;
short bytes; 
// instead of doing string decoding and stuff we can just use the binary
// all commands are two bytes
// format: 4 bits opcode + 12 bits data


//
// pin assignments
//

// endstops
#define X_STOP_PIN        2
#define Y_STOP_PIN        3

// steppers
#define TOP_MOTOR_STEP    8
#define TOP_MOTOR_DIR     9
#define LEFT_MOTOR_STEP  10
#define LEFT_MOTOR_DIR   11
#define RIGHT_MOTOR_STEP 12
#define RIGHT_MOTOR_DIR  13

// stepper motor directions
#define TOP_MOTOR_OUT    LOW
#define TOP_MOTOR_IN    HIGH
#define LEFT_MOTOR_OUT  HIGH
#define LEFT_MOTOR_IN    LOW
#define RIGHT_MOTOR_OUT  LOW
#define RIGHT_MOTOR_IN  HIGH


//
// create motors
//
SpeedyStepper stepperR;
SpeedyStepper stepperL;
SpeedyStepper stepperT;

//
// Set motor parameters
//
const int steps_per_rotation = 200;
const float max_speed = 3.0; // rotations per second
const float zero_speed = .75; // rotations per second

//
// Initialize global x and y and target x and y
//
int x, x_target; // steps in the x direction
int y, y_target; // steps in the x direction

// 
// Initialize for zero axis
volatile int x_zeroed = 0; // zeroing is complete
volatile int y_zeroed = 0;

// 
// Timing stuff
//
unsigned long t; // timing is the core of *everything*

//
// Mechanical parameters of gantry
// 
const float spool_diameter = 50.8; // 2in to mm
const float max_gantry_x = 370.0; // mm
const float max_gantry_y = 410.0; // mm

//
// Misc 
//
String command;
bool zeroed;


void setup() {
 // Get Serial running
  Serial.begin(115200);

  // Initialize Motors
  pinMode(LEFT_MOTOR_STEP, OUTPUT);
  pinMode(LEFT_MOTOR_DIR, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR, OUTPUT);
  pinMode(TOP_MOTOR_DIR, OUTPUT);
  pinMode(TOP_MOTOR_DIR, OUTPUT);

  // leds
  pinMode(A0, OUTPUT);
  pinMode(A1, OUTPUT);
  pinMode(A2, OUTPUT);
  digitalWrite(A0, HIGH);
  digitalWrite(A1, HIGH);
  digitalWrite(A2, HIGH);

  // Initialize Stepper Motors
  stepperR.connectToPins(RIGHT_MOTOR_STEP, RIGHT_MOTOR_DIR); 
  stepperL.connectToPins(LEFT_MOTOR_STEP, LEFT_MOTOR_DIR);
  stepperT.connectToPins(TOP_MOTOR_STEP, TOP_MOTOR_DIR);

  // Initialize end stop interupts
  attachInterrupt(digitalPinToInterrupt(X_STOP_PIN), stop_x, RISING);
  attachInterrupt(digitalPinToInterrupt(Y_STOP_PIN), stop_y, RISING);

  /*
  // Try moving somewhere
  move(300, 300);
  delay(200);
  move(20,20);
  delay(200);
  move(200,200);
  */

}

//////////////// ZERO FUNCTIONS ////////////////////////

void stop_x() {
  //digitalWrite(DEBUG_LED_1_PIN, HIGH);
  x_zeroed = 1;
}

void stop_y() {
  //digitalWrite(DEBUG_LED_1_PIN, LOW);
  y_zeroed = 1;
}

void zero_x() {
  #ifdef DEBUG
  Serial.println("Zeroing X");
  #endif
  x_zeroed = 0;
  // zeros the x position
  digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_OUT); // same direction
  digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
  while (!x_zeroed) {
    // todo: optimize with register access
    // digitalWrite is slow enough the pulses will be long enough for the controller
    // HIGH pulse
    digitalWrite(LEFT_MOTOR_STEP, HIGH);
    digitalWrite(RIGHT_MOTOR_STEP, HIGH);
    digitalWrite(LEFT_MOTOR_STEP, LOW);
    digitalWrite(RIGHT_MOTOR_STEP, LOW);
    // wait LOW
    delay(1000/(steps_per_rotation * zero_speed));
  }
}

void zero_y() {
  #ifdef DEBUG
  Serial.println("Zeroing Y");
  #endif
  y_zeroed = 0;
  // zeros the y position
  digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_IN); // reverse left motor
  digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
  digitalWrite(TOP_MOTOR_DIR, TOP_MOTOR_OUT);
  while (!y_zeroed) {
    // todo: optimize with register access
    // digitalWrite is slow enough the pulses will be long enough for the controller
    // HIGH pulse
    digitalWrite(LEFT_MOTOR_STEP, HIGH);
    digitalWrite(RIGHT_MOTOR_STEP, HIGH);
    digitalWrite(TOP_MOTOR_STEP, HIGH);
    digitalWrite(LEFT_MOTOR_STEP, LOW);
    digitalWrite(RIGHT_MOTOR_STEP, LOW);
    digitalWrite(TOP_MOTOR_STEP, LOW);
    // wait LOW
    delay(1000/(steps_per_rotation * zero_speed));
  }
}

void clear_motors(){
  digitalWrite(LEFT_MOTOR_STEP, LOW);
  digitalWrite(RIGHT_MOTOR_STEP, LOW);
  digitalWrite(TOP_MOTOR_STEP, LOW);
}

void tention(){
  digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_IN);
  digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
  digitalWrite(TOP_MOTOR_DIR, TOP_MOTOR_IN);
  for (int step = 0; step <= 10; step++){
    digitalWrite(LEFT_MOTOR_STEP, HIGH);
    digitalWrite(RIGHT_MOTOR_STEP, HIGH);
    digitalWrite(TOP_MOTOR_STEP, HIGH);
    digitalWrite(LEFT_MOTOR_STEP, LOW);
    digitalWrite(RIGHT_MOTOR_STEP, LOW);
    digitalWrite(TOP_MOTOR_STEP, LOW);
    // wait LOW
    delay(1000/(steps_per_rotation * 2));
  }
}

void zero_all(){
  //clear_motors();
  delay(1000);
  // Zero the axis
  zero_y();
  y = 0; // set global x to zero
  zero_x();
  x = 0; // set global y to zero
  //Serial.print("Axis at Zero");
  tention();
  delay(1000);
}

///////////////////////////////////////////////////////////////////////


void move(float x_target, float y_target){
  #ifdef DEBUG
  Serial.println("move: ");
  Serial.println(x_target);
  Serial.println(y_target);
  Serial.println(x);
  Serial.println(y);
  #endif
  // swap x direction
  x_target = -x_target;

  // prevent from crashing gantry
  if (x_target < -max_gantry_x)
    x_target = -max_gantry_x;
  if (y_target > max_gantry_y)
    y_target = max_gantry_y;
  
  // calculate distance in mm
  float dx = x_target - x;
  float dy = y_target - y;

  // calculate steps needed to turn by each motor
  long x_steps = dx * (1/(spool_diameter*3.14)) * (steps_per_rotation);
  long y_steps = dy * (1/(spool_diameter*3.14)) * (steps_per_rotation);

  long steps_T = -(y_steps);
  long steps_L = x_steps + y_steps;
  long steps_R = -(x_steps - y_steps);

  #ifdef DEBUG
  Serial.println("steps:");
  Serial.println(steps_T);
  Serial.println(steps_L);
  Serial.println(steps_R);
  #endif

  float speedInStepsPerSecond = 5000;
  float accelerationInStepsPerSecondPerSecond = 4500; // tested up to 5000
  moveXYWithCoordination(steps_R, steps_L, steps_T, speedInStepsPerSecond, accelerationInStepsPerSecondPerSecond);
  tention();
  x = x_target;
  y = y_target;
  
}

short x_command, y_command;


void loop() {
  // number of bytes in the serial buffer
  bytes = Serial.available();
  if (bytes == 2) {
    #ifdef DEBUG
    digitalWrite(A0, LOW);
    #endif
    // read a command into the buffer
    Serial.readBytes((char*)&buffer, 2);
    opcode = (buffer >> 12) & OPCODE_MASK;
    data = buffer & DATA_MASK;
    // for now also ZZ in the serial monitor as a zero
    if (buffer == 0x5a5a) {
      data = 0;
      opcode = C_ZERO;
    }
    switch (opcode) {
      case (C_ZERO):
        #ifdef DEBUG
        Serial.println("ZEROING");
        #endif
        zero_all();
        zeroed = true;
        break;
      case (C_TENSION_X_P):
        break;
      case (C_TENSION_X_N):
        break;
      case (C_TENSION_Y_P):
        break;
      case (C_TENSION_Y_N):
        break;
      case (C_MOVE_X):
        x_command = data;
        break;
      case (C_MOVE_Y):
        y_command = data;
        break;
      case (C_READY):
        break;
      default:
        // unused opcode
        break;
    }
    #ifdef DEBUG
    Serial.println("New command:");
    Serial.println(String((int)opcode, HEX));
    Serial.println(String((int)data));
    Serial.println(String(buffer, HEX));
    #endif
  } else if (bytes > 2) {
    // check if this error mode ever occurs, might be unnecessary!
    Serial.read();
    #ifdef DEBUG
    Serial.println("ERROR: READ > 2 BYTES");
    #endif
  }

  // hack to accommodate seprate packets for x and y
  // this can be done cleaner but it works
  if (x_command && y_command) {
    x_target = x_command;
    y_target = y_command;
    #ifdef DEBUG
    Serial.println(x_target);
    Serial.println(y_target);
    #endif
    move(x_target,y_target);
    x_command = 0;
    y_command = 0;
  }
  
}

////////////////// SPEEDY STEPPER CODE BELOW ///////////////////////////////////////

void moveXYWithCoordination(long stepsR, long stepsL, long stepsT, float speedInStepsPerSecond, float accelerationInStepsPerSecondPerSecond)
{
  float speedInStepsPerSecond_R;
  float accelerationInStepsPerSecondPerSecond_R;
  float speedInStepsPerSecond_L;
  float accelerationInStepsPerSecondPerSecond_L;
  float speedInStepsPerSecond_T;
  float accelerationInStepsPerSecondPerSecond_T;
  long absStepsR;
  long absStepsL;
  long absStepsT;

  //
  // setup initial speed and acceleration values
  //
  speedInStepsPerSecond_R = speedInStepsPerSecond;
  accelerationInStepsPerSecondPerSecond_R = accelerationInStepsPerSecondPerSecond;
  
  speedInStepsPerSecond_L = speedInStepsPerSecond;
  accelerationInStepsPerSecondPerSecond_L = accelerationInStepsPerSecondPerSecond;

  speedInStepsPerSecond_T = speedInStepsPerSecond;
  accelerationInStepsPerSecondPerSecond_T = accelerationInStepsPerSecondPerSecond;


  //
  // determine how many steps each motor is moving
  //
  if (stepsR >= 0)
    absStepsR = stepsR;
  else
    absStepsR = -stepsR;
 
  if (stepsL >= 0)
    absStepsL = stepsL;
  else
    absStepsL = -stepsL;

  if (stepsT >= 0)
    absStepsT = stepsT;
  else
    absStepsT = -stepsT;


  //
  // determine which motor is traveling the farthest, then slow down the
  // speed rates for the motor moving the shortest distance
  //
  if ((absStepsR > absStepsL) && (absStepsR > absStepsT) && (stepsR != 0))
  {
    //
    // slow down the motor traveling less far
    //
    float scalerL = (float) absStepsL / (float) absStepsR;
    speedInStepsPerSecond_L = speedInStepsPerSecond_L * scalerL;
    accelerationInStepsPerSecondPerSecond_L = accelerationInStepsPerSecondPerSecond_L * scalerL;

    float scalerT = (float) absStepsT / (float) absStepsR;
    speedInStepsPerSecond_T = speedInStepsPerSecond_T * scalerT;
    accelerationInStepsPerSecondPerSecond_T = accelerationInStepsPerSecondPerSecond_T * scalerT;
  }
  
  if ((absStepsL > absStepsR) && (absStepsL > absStepsT) && (stepsL != 0))
  {
    //
    // slow down the motor traveling less far
    //
    float scalerR = (float) absStepsR / (float) absStepsL;
    speedInStepsPerSecond_R = speedInStepsPerSecond_R * scalerR;
    accelerationInStepsPerSecondPerSecond_R = accelerationInStepsPerSecondPerSecond_R * scalerR;
    
    float scalerT = (float) absStepsT / (float) absStepsL;
    speedInStepsPerSecond_T = speedInStepsPerSecond_T * scalerT;
    accelerationInStepsPerSecondPerSecond_T = accelerationInStepsPerSecondPerSecond_T * scalerT;
  }

  if ((absStepsT > absStepsR) && (absStepsT > absStepsL) && (stepsT != 0))
  {
    //
    // slow down the motor traveling less far
    //
    float scalerR = (float) absStepsR / (float) absStepsT;
    speedInStepsPerSecond_R = speedInStepsPerSecond_R * scalerR;
    accelerationInStepsPerSecondPerSecond_R = accelerationInStepsPerSecondPerSecond_R * scalerR;
    
    float scalerL = (float) absStepsL / (float) absStepsT;
    speedInStepsPerSecond_L = speedInStepsPerSecond_L * scalerL;
    accelerationInStepsPerSecondPerSecond_L = accelerationInStepsPerSecondPerSecond_L * scalerL;
  }

  
  //
  // setup the motion for the R motor
  //
  stepperR.setSpeedInStepsPerSecond(speedInStepsPerSecond_R);
  stepperR.setAccelerationInStepsPerSecondPerSecond(accelerationInStepsPerSecondPerSecond_R);
  stepperR.setupRelativeMoveInSteps(stepsR);


  //
  // setup the motion for the L motor
  //
  stepperL.setSpeedInStepsPerSecond(speedInStepsPerSecond_L);
  stepperL.setAccelerationInStepsPerSecondPerSecond(accelerationInStepsPerSecondPerSecond_L);
  stepperL.setupRelativeMoveInSteps(stepsL);

  //
  // setup the motion for the T motor
  //
  stepperT.setSpeedInStepsPerSecond(speedInStepsPerSecond_T);
  stepperT.setAccelerationInStepsPerSecondPerSecond(accelerationInStepsPerSecondPerSecond_T);
  stepperT.setupRelativeMoveInSteps(stepsT);


  //
  // now execute the moves, looping until both motors have finished
  //
  while((!stepperR.motionComplete()) || (!stepperL.motionComplete()) || (!stepperT.motionComplete()))
  {
    stepperR.processMovement();
    stepperL.processMovement();
    stepperT.processMovement();
  }
}
