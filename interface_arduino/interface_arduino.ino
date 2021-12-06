







void setup()
{
  Serial.begin(9600);// starts the serial monitor
 
  




}


void Interface_Connect()
{



//see if there's incoming serial data
  if (Serial.available() > 0) {
    incomingData = Serial.read();
  

   
   // prints the value of the sensor to the serial monitor
   if (incomingData == 'S'){ //stop
 //  Serial.print("Stopping");
  
   }

   if (incomingData == 'F') {//start
// Serial.print("Starting");
  
     
   }

     if (incomingData == 'Z') {//start
// Serial.print("Zeroing");
  
     
   }
  }
  
   
   

 
   } ;
