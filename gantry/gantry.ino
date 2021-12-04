// uncomment to enable debug printing
#define DEBUG
// uncomment when debugging without hardware attached
#define HEADLESS

// endstops
#define X_STOP_PIN         2
#define Y_STOP_PIN         3
// steppers
#define TOP_MOTOR_STEP     8
#define TOP_MOTOR_DIR      9
#define LEFT_MOTOR_STEP   10
#define LEFT_MOTOR_DIR    11
#define RIGHT_MOTOR_STEP  12
#define RIGHT_MOTOR_DIR   13
// max number of steps in a direction
#define MAX_STEPS_Y      500
#define MAX_STEPS_X      500
// debug LEDs
#define LED_G             A2
#define LED_Y             A1
#define LED_R             A0
// hardware buttons
#define BUTTON_ZERO        4
#define BUTTON_PLUS        5
#define BUTTON_MINUS       6
#define BUTTON_MODE        7

// stepper motor directions
#define TOP_MOTOR_OUT    LOW
#define TOP_MOTOR_IN    HIGH
#define LEFT_MOTOR_OUT  HIGH
#define LEFT_MOTOR_IN    LOW
#define RIGHT_MOTOR_OUT  LOW
#define RIGHT_MOTOR_IN  HIGH

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

// compiler macro to generate NOP instructions for more precise delays
// 16MHz = 0.0625us/cycle => 16 instructions
#define DELAY_CYCLES(n) __builtin_avr_delay_cycles(n)
// digitalWrite has some safety checks but takes 50-60 cycles (3us)!
// given that our servo driver has a minimum pulse duration of 1us this allow us to churn out slightly faster pulses
// im mostly doing this to serve my learning goal of learning more complex firmware development!


// note: there's some pseudocode for the library I'm working on commented out here
enum setup_state {
  S_UNKNOWN,
  S_TENSION_X,
  S_TENSION_Y,
  S_READY
};

setup_state state = S_UNKNOWN;


// for the x-axis demo we can be tricky and use an inverter (NOT gate) on the direction pin of one motor to get perfect synchronization
// the step pins are connected to each other to achieve this effect

unsigned long t; // timing is the core of *everything*
const int steps_per_rotation = 200;
const float max_speed = 3.0; // rotations per second
const float zero_speed = .75    ; // rotations per second
unsigned int x, x_target; // steps in the x direction
unsigned int y, y_target; // steps in the x direction
volatile int x_zeroed = 0; // zeroing is complete
volatile int y_zeroed = 0;

void setup() {
  // this can be left as slow calls, we don't need to micro-optimize the boot sequence
  pinMode(LEFT_MOTOR_STEP, OUTPUT);
  pinMode(LEFT_MOTOR_DIR, OUTPUT);
  pinMode(RIGHT_MOTOR_STEP, OUTPUT);
  pinMode(RIGHT_MOTOR_DIR, OUTPUT);
  pinMode(TOP_MOTOR_STEP, OUTPUT);
  pinMode(TOP_MOTOR_DIR, OUTPUT);
  pinMode(BUTTON_ZERO, INPUT_PULLUP);
  pinMode(BUTTON_PLUS, INPUT_PULLUP);
  pinMode(BUTTON_MINUS, INPUT_PULLUP);
  pinMode(BUTTON_MODE, INPUT_PULLUP);
  pinMode(LED_G, OUTPUT);
  pinMode(LED_Y, OUTPUT);
  pinMode(LED_R, OUTPUT);
  // LEDs are active LOW
  digitalWrite(LED_G, HIGH);
  digitalWrite(LED_Y, HIGH);
  digitalWrite(LED_R, HIGH);
  // serial for receiving commands
  Serial.begin(9600);
  // setup the motion system with contraints
  
  
  // setup the interrupts
  // used for safety and zeroing
  attachInterrupt(digitalPinToInterrupt(X_STOP_PIN), stop_x, RISING);
  attachInterrupt(digitalPinToInterrupt(Y_STOP_PIN), stop_y, RISING);
  Serial.read(); // flush read buffer
  delay(5000); // wait a bit before accepting any commands
  // show boot sequence complete on LEDs
  digitalWrite(LED_R, LOW);
  delay(1000);
  digitalWrite(LED_Y, LOW);
  delay(1000);
  digitalWrite(LED_G, LOW);
  delay(1000);
  digitalWrite(LED_G, HIGH);
  digitalWrite(LED_Y, HIGH);
  digitalWrite(LED_R, HIGH);
  delay(1000);
  digitalWrite(LED_G, LOW);
  digitalWrite(LED_Y, LOW);
  digitalWrite(LED_R, LOW);
  delay(1000);
  digitalWrite(LED_G, HIGH);
  digitalWrite(LED_Y, HIGH);
  digitalWrite(LED_R, HIGH);
  #ifdef DEBUG
  Serial.println("Boot complete");
  #endif
}

void stop_x() {
  x_zeroed = 1;
}

void stop_y() {
  y_zeroed = 1;
}


// ZEROING WILL NOT WORK IF INTERRUPTS ARE NOT RUNNING
// zeroing runs with out acceleration because you shouldn't be trying to drive your motors to the limits into the endstop!
void zero_x() {
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
  y_zeroed = 0;
  // zeros the y position
  digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_IN); // pull both in
  digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
  digitalWrite(TOP_MOTOR_DIR, TOP_MOTOR_OUT); // increase length of top y
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

void zero() {
  #ifndef HEADLESS
  zero_y();
  zero_x();
  #endif
  // todo: check state ordering and what order zeroing and tensioning needs to happen in
  // if it hasn't been zeroed yet, now ready for tensioning
  if (state == S_UNKNOWN) {
    state = S_TENSION_X;
    digitalWrite(LED_G, HIGH);
    digitalWrite(LED_Y, HIGH);
    digitalWrite(LED_R, LOW);
  }
}

// ensures LEDs always reflect state
void set_state(setup_state new_state) {
  state = new_state;
  // update LEDs based on state
  switch (new_state) {
    case S_READY:
      digitalWrite(LED_G, LOW);
      digitalWrite(LED_R, HIGH);
      digitalWrite(LED_Y, HIGH);
      break;
    case S_TENSION_X:
      digitalWrite(LED_G, LOW);
      digitalWrite(LED_R, HIGH);
      digitalWrite(LED_Y, HIGH);
      break;
    case S_TENSION_Y:
      digitalWrite(LED_G, LOW);
      digitalWrite(LED_R, HIGH);
      digitalWrite(LED_Y, HIGH);
      break;
    default:
      digitalWrite(LED_G, HIGH);
      digitalWrite(LED_R, HIGH);
      digitalWrite(LED_Y, HIGH);
      break;
  }
}


void loop() {
  // gcode is a thing that exists but WAY overkill for our needs
  // take in serial commands for (x,y) pairs
  //motion.update_target(x, y);
  // perform steps
  //motion.run();
  // number of bytes in the serial buffer
  bytes = Serial.available();
  if (bytes == 2) {
    // read a command into the buffer
    Serial.readBytes((char*)&buffer, 2);
    opcode = (buffer >> 12) & OPCODE_MASK;
    data = buffer & DATA_MASK;
    switch (opcode) {
      case (C_ZERO):
        zero();
        break;
      case (C_TENSION_X_P):
        zero();
        break;
      case (C_TENSION_X_N):
        zero();
        break;
      case (C_TENSION_Y_P):
        zero();
        break;
      case (C_TENSION_Y_N):
        zero();
        break;
      case (C_MOVE_X):
        zero();
        break;
      case (C_MOVE_Y):
        zero();
        break;
      case (C_READY):
        set_state(S_READY);
        break;
      default:
        // unused opcode
        break;
    }
    #ifdef DEBUG
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

  // this can be optimized eventually by just reading the whole register at once
  // hardware control interface
  // reads take a while so this might be worth optimizing eventually
  if (digitalRead(BUTTON_ZERO) == LOW) {
    // zero the position
    #ifdef DEBUG
    Serial.println("Zero pressed");
    #endif
    zero();
  }

  // adjust initial tension
  // mode state machine
  if (digitalRead(BUTTON_MODE) == LOW) {
    #ifdef DEBUG
    Serial.println("Mode pressed");
    #endif
    switch (state) {
      case S_TENSION_X:
        state = S_TENSION_Y;
        digitalWrite(LED_G, HIGH);
        digitalWrite(LED_Y, LOW);
        digitalWrite(LED_R, LOW);
        break;
      case S_TENSION_Y:
        state = S_READY;
        digitalWrite(LED_G, LOW);
        digitalWrite(LED_Y, HIGH);
        digitalWrite(LED_R, HIGH);
        break;
      case S_READY:
        state = S_TENSION_X;
        digitalWrite(LED_G, HIGH);
        digitalWrite(LED_Y, HIGH);
        digitalWrite(LED_R, LOW);
        break;
    }
    delay(500);
  }

  // increase tension
  if (digitalRead(BUTTON_PLUS) == LOW) {
    #ifdef DEBUG
    Serial.println("+ Pressed");
    #endif
    switch (state) {
      case S_TENSION_X:
        // step motor once
        digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_IN);
        digitalWrite(LEFT_MOTOR_STEP, HIGH);
        digitalWrite(LEFT_MOTOR_STEP, LOW);
        break;
      case S_TENSION_Y:
        // step motor once
        digitalWrite(TOP_MOTOR_DIR, TOP_MOTOR_IN);
        digitalWrite(TOP_MOTOR_STEP, HIGH);
        digitalWrite(TOP_MOTOR_STEP, LOW);
        break;
    }
    delay(500);
  }

  // increase tension
  if (digitalRead(BUTTON_MINUS) == LOW) {
    #ifdef DEBUG
    Serial.println("- Pressed");
    #endif
    switch (state) {
      case S_TENSION_X:
        // step motor once
        digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
        digitalWrite(RIGHT_MOTOR_STEP, HIGH);
        digitalWrite(RIGHT_MOTOR_STEP, LOW);
        break;
      case S_TENSION_Y:
        // step motors once
        digitalWrite(RIGHT_MOTOR_DIR, RIGHT_MOTOR_IN);
        digitalWrite(LEFT_MOTOR_DIR, LEFT_MOTOR_IN);
        digitalWrite(RIGHT_MOTOR_STEP, HIGH);
        digitalWrite(LEFT_MOTOR_STEP, HIGH);
        digitalWrite(RIGHT_MOTOR_STEP, LOW);
        digitalWrite(LEFT_MOTOR_STEP, LOW);
        break;
    }
    delay(500);
  }

  
  // for the x only case things are easy because we only have one interval to track
  // not using delay is ideal because it keeps the main loop non blocking so that everything runs smoothly with other tasks (though occasionaly a step may come a bit late)


  // TODO: verify timing with a scope
  // while there is some delay between starting a write and the gpio updating, this should keep things very tight
  // that delay could be measured with a scope and the delays updated accordingly
  
  DELAY_CYCLES(16);
  
}
