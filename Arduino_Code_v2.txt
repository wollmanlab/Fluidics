void SerialParser(void) {
  char readChar[64];
  Serial.readBytesUntil(33,readChar,64);
  String read_ = String(readChar);
  // Format is @{direction}%{speed}_{duration}$!
  int idx1 = read_.indexOf('%');
  int idx2 = read_.indexOf('_');
  int idx3 = read_.indexOf('$');
  float dt = 0.1;
  // separate command from associated data
  String pump_direction = read_.substring(1,idx1);
  float speed_fraction = atof(read_.substring(idx1+1,idx2).c_str());
  float pump_duration = atof(read_.substring(idx2+1,idx3).c_str());

  //speed_fraction = 0.25;

  // Direction (F,R) // Speed_Fraction(0.1-1) // Duration (float)
  
  // determine command sent
  int pin = 13;
  bool skip = true;
  if (pump_direction == "F") {
      pin = 5; 
      skip = false; 
  }
  else if (pump_direction == "R") {
      pin = 4;
      skip = false;
  }
  else if (pump_direction == "U") {
      pin = 13; 
      skip = true; 
  }

  
  if (skip==false){
    pinMode(pin, OUTPUT);
    pinMode(13, OUTPUT);
    
    if (pump_duration > dt){
      if (speed_fraction == 1){
        digitalWrite(pin, HIGH);
        delay(pump_duration*1000);
        digitalWrite(pin, LOW);
      }
      else {
        int total_steps = pump_duration/dt;
        int used_steps = 0;
        int pos_duty = round(10*speed_fraction);
        int neg_duty = round(10-pos_duty);
  
        while (used_steps<total_steps){
          if ((used_steps+10)<total_steps){
            // Standard
            digitalWrite(pin, HIGH);
            digitalWrite(13, HIGH);
            delay(1000*dt*pos_duty);
            digitalWrite(pin, LOW);
            digitalWrite(13, LOW);
            delay(1000*dt*neg_duty);
            used_steps = used_steps+10;
          }
          else {
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
