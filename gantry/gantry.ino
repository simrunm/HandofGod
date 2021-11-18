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
// max number of steps in a direction
#define MAX_STEPS_Y     500
#define MAX_STEPS_X     500
// debug LEDs
// compiler macro to generate NOP instructions for more precise delays
// 16MHz = 0.0625us/cycle => 16 instructions
#define DELAY_CYCLES(n) __builtin_avr_delay_cycles(n)
// digitalWrite has some safety checks but takes 50-60 cycles (3us)!
// given that our servo driver has a minimum pulse duration of 1us this allow us to churn out slightly faster pulses
// im mostly doing this to serve my learning goal of learning more complex firmware development!


// note: there's some pseudocode for the library I'm working on commented out here

// for the x-axis demo we can be tricky and use an inverter (NOT gate) on the direction pin of one motor to get perfect synchronization
// the step pins are connected to each other to achieve this effect

unsigned long t; // timing is the core of *everything*
const int steps_per_rotation = 200;
const float max_speed = 3.0; // rotations per second
const float zero_speed = 1; // rotations per second
unsigned int x, x_target; // steps in the x direction
unsigned int y, y_target; // steps in the x direction
volatile int x_zeroed = 0; // zeroing is complete
volatile int y_zeroed = 0;

void setup() {
  // debug LED
  //pinMode(DEBUG_LED_1_PIN, OUTPUT);
  // this can be left as slow calls, we don't need to micro-optimize the boot sequence
  pinMode(LEFT_MOTOR_STEP, OUTPUT);
  pinMode(LEFT_MOTOR_DIR, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR, OUTPUT);
  // serial for recieving commands
  Serial.begin(9600);
  // setup the motion system with contraints
  
  
  // setup the interrupts
  // used for safety and zeroing
  attachInterrupt(digitalPinToInterrupt(X_STOP_PIN), stop_x, RISING);
  attachInterrupt(digitalPinToInterrupt(Y_STOP_PIN), stop_y, RISING);

  // zero the position
  zero_y();
  zero_x();

  // ensure initial tension

}

void stop_x() {
  //digitalWrite(DEBUG_LED_1_PIN, HIGH);
  x_zeroed = 1;
}

void stop_y() {
  //digitalWrite(DEBUG_LED_1_PIN, LOW);
  y_zeroed = 1;
}


// ZEROING WILL NOT WORK IF INTERRUPTS ARE NOT RUNNING
// zeroing runs with out accerlation because you shouldn't be trying to drive your motors to the limits into the endstop!
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
  while (!y_zeroed) {
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

byte in;
void loop() {
  // gcode is a thing that exists but WAY overkill for our needs
  // take in serial commands for (x,y) pairs
  //motion.update_target(x, y);
  // perform steps
  //motion.run();
  if (Serial.available()) {
    in = Serial.read();
    if (in == "\n") {
      // line end
    }
  }
  
  // for the x only case things are easy because we only have one interval to track
  // not using delay is ideal because it keeps the main loop non blocking so that everything runs smoothly with other tasks (though occasionaly a step may come a bit late)


  // TODO: verify timing with a scope
  // while there is some delay between starting a write and the gpio updating, this should keep things very tight
  // that delay could be measured with a scope and the delays updated accordingly
  
  DELAY_CYCLES(16);
  
}
