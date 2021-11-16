

/*     Simple Stepper Motor Control Exaple Code
 *      
 *  by Dejan Nedelkovski, www.HowToMechatronics.com
 *  Drives a 5rev/sec
 *  
 */
// defines pins numbers
const int stepPin = 3; 
const int dirPin = 2;
int counter ;
long prevmillis = 0;
float time_taken;
//const int enablePin = 56  ; 
 
void setup() {
  Serial.begin(9600); // opens serial port, sets data rate to 9600 bps
  // Sets the two pins as Outputs
  pinMode(stepPin,OUTPUT); 
  pinMode(dirPin,OUTPUT);
  counter = 0;
 // pinMode(enablePin,OUTPUT);
  //digitalWrite(enablePin,LOW);
}
void stepping(int revs)  {
  //digitalWrite(dirPin,HIGH); // Enables the motor to move in a particular direction
  // Makes 200 pulses for making one full cycle rotation
  
  for(float x = 0; x < 200*revs; x++) {
    digitalWrite(stepPin,HIGH); 
    delayMicroseconds(498); 
    digitalWrite(stepPin,LOW); 
    delayMicroseconds(498); 
   // Serial.print("Rev Completion: ");   //comment these out for speed
    //Serial.println(x/200);  //comment these out for speed
  }
}

void loop() {

  
  if (counter < 1 ){
   stepping(100
   );
   counter += 1;
   }
unsigned long currentMillis = millis();
time_taken = currentMillis-prevmillis;
Serial.print("Revs per sec: ");
Serial.println(100/(time_taken/1000));
delay(50000);

 
   
   
}
 
 

 // One second delay
  
//  digitalWrite(dirPin,LOW); //Changes the rotations direction
  // Makes 400 pulses for making two full cycle rotation
//  for(int x = 0; x < 400; x++) {
 //   digitalWrite(stepPin,HIGH);
  //  delayMicroseconds(500);
 //   digitalWrite(stepPin,LOW);
  //  delayMicroseconds(500);
 // }
////  delay(1000);
//}
