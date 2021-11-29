// Main Arduino Code for Hand of God PIE Project
// Allows for gantry to move to any spot given a serial input
// Allows for zeroing of axis at begining
// Authors: Elvis Wolcott, Chris Allum



#include <SpeedyStepper.h>

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


void setup() {
 // Get Serial running
  Serial.begin(9600);

  // Initialize Motors
  pinMode(LEFT_MOTOR_STEP, OUTPUT);
  pinMode(LEFT_MOTOR_DIR, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR, OUTPUT);
  pinMode(TOP_MOTOR_DIR, OUTPUT);
  pinMode(TOP_MOTOR_DIR, OUTPUT);

  // Initialize Stepper Motors
  stepperR.connectToPins(RIGHT_MOTOR_STEP, RIGHT_MOTOR_DIR); 
  stepperL.connectToPins(LEFT_MOTOR_STEP, LEFT_MOTOR_DIR);
  stepperT.connectToPins(TOP_MOTOR_STEP, TOP_MOTOR_DIR);

  // Initialize end stop interupts
  attachInterrupt(digitalPinToInterrupt(X_STOP_PIN), stop_x, RISING);
  attachInterrupt(digitalPinToInterrupt(Y_STOP_PIN), stop_y, RISING);

  //clear_motors();
  delay(1000);
  // Zero the axis
  zero_y();
  y = 0; // set global x to zero
  zero_x();
  x = 0; // set global y to zero
  Serial.print("Axis at Zero");
  tention();
  delay(1000);

  // Try moving somewhere
  move(300, 300);
  delay(200);
  move(20,20);
  delay(200);
  move(100,100);
  

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
  x_zeroed = 0;
  // zeros the x position
  digitalWrite(LEFT_MOTOR_DIR, LOW); // same direction
  digitalWrite(RIGHT_MOTOR_DIR, LOW);
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
  y_zeroed = 0;
  // zeros the y position
  digitalWrite(LEFT_MOTOR_DIR, HIGH); // reverse left motor
  digitalWrite(RIGHT_MOTOR_DIR, LOW);
  digitalWrite(TOP_MOTOR_DIR, HIGH);
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
  digitalWrite(LEFT_MOTOR_DIR, HIGH);
  digitalWrite(RIGHT_MOTOR_DIR, LOW);
  digitalWrite(TOP_MOTOR_DIR, LOW);
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

///////////////////////////////////////////////////////////////////////


void move(float x_target, float y_target){
  // swap x directin
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

  long steps_T = y_steps;
  long steps_L = x_steps + y_steps;
  long steps_R = x_steps - y_steps;

  float speedInStepsPerSecond = 5000;
  float accelerationInStepsPerSecondPerSecond = 4500; // tested up to 5000
  moveXYWithCoordination(steps_R, steps_L, steps_T, speedInStepsPerSecond, accelerationInStepsPerSecondPerSecond);
  tention();
  x = x_target;
  y = y_target;
  
}


void loop() {
  while (!Serial.available());
  command = Serial.readString();
  Serial.print(command);


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
