void SerialParser(void) {
  // Read formatted input message (@{direction}%{speed}_{duration}$!) from serial port.
  char readChar[64];
  Serial.readBytesUntil(33,readChar,64); // 33 is the ASCII code for ! which marks the end of the message.
  String read_ = String(readChar);
  // Get the index location of the delimiters (%,_,$) marking the end of direction,speed,duration. 
  int idx1 = read_.indexOf('%');
  int idx2 = read_.indexOf('_');
  int idx3 = read_.indexOf('$');
  // This is for calculating the time of on and off phase based on user specified duty cycle.
  // For example, for a duty cylce of 0.7, the pump will be on for 7*dt seconds and off for 3*dt seconds in one cycle.
  // The duration of one cycle will be 10*dt
  float dt = 0.1;
  // Extract direction, speed and duration from the message.
  String pump_direction = read_.substring(1,idx1);
  float speed_fraction = atof(read_.substring(idx1+1,idx2).c_str()); // speed_fraction is the duty cycle of the pump
  float pump_duration = atof(read_.substring(idx2+1,idx3).c_str());

  //speed_fraction = 0.25;

  // Direction (F,R) // Speed_Fraction(0.1-1) // Duration (float)
  
  // Determine which pin to activate based on the direction
  // Regardless of direction, pin 13 always needs to be activated to turn the pump on
  // change the pin number if your wiring is changed. 
  int pin = 13; 
  bool skip = true;
  if (pump_direction == "F") {
      // pin 5 of arduino is wired to the forward pumping button
      // change the pin number if you the wiring is changed
      pin = 5; 
      skip = false; 
  }
  else if (pump_direction == "R") {
      // pin 4 of arduino is wired to the reverse pumping button
      // change the pin number if you the wiring is changed
      pin = 4;
      skip = false;
  }
  else if (pump_direction == "U") {
      pin = 13; 
      skip = true; // When direction is undefined, set skip to true to skip any pumping
  }

  
  if (skip==false){
    pinMode(pin, OUTPUT);
    pinMode(13, OUTPUT);
    
    if (pump_duration > dt){
      if (speed_fraction == 1){
        // If the duty cycle is 1, it means the pump is on throughout the duration
        digitalWrite(pin, HIGH);
        delay(pump_duration*1000);
        digitalWrite(pin, LOW);
      }
      else {
        // If duty cycle is smaller than 1, the pump will cycle between on and off.
        int total_steps = pump_duration/dt; // Total cycle to be run
        int used_steps = 0; // How many cycles have been run
        int pos_duty = round(10*speed_fraction); // The duration of on within one cycle
        int neg_duty = round(10-pos_duty); // The duration of off within one cycle
  
        while (used_steps<total_steps){
          if ((used_steps+10)<total_steps){
            // For the first N-10 cycles, operate in the standard on/off way as how standard duty cycle should be. 
            digitalWrite(pin, HIGH);
            digitalWrite(13, HIGH);
            delay(1000*dt*pos_duty);
            digitalWrite(pin, LOW);
            digitalWrite(13, LOW);
            delay(1000*dt*neg_duty);
            used_steps = used_steps+10;
          }
          else {
            // For the last 10 cycles, combine all 10 on together and all 10 off together.
            int remaining_steps = total_steps-used_steps;
            int remaining_pos = remaining_steps*speed_fraction;
            int remaining_neg = remaining_steps - remaining_pos;
            digitalWrite(pin, HIGH);
            digitalWrite(13, HIGH);
            delay(1000*dt*remaining_pos);
            digitalWrite(pin, LOW);
            digitalWrite(13, LOW);
            delay(1000*dt*remaining_neg);
            used_steps = total_steps;
          }
        }
      }
      digitalWrite(pin, LOW);
      digitalWrite(13, LOW);
  }
  }
}

void setup()  {
  Serial.begin(9600); 
    while (!Serial) {
    ; // wait for serial port to connect. Needed for Leonardo only
  }
}

void loop() {
   SerialParser();
   }
