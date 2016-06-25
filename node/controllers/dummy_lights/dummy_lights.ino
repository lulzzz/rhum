int BAUD_RATE = 115200;

void setup() {
  Serial.begin(BAUD_RATE);
}

void loop() {
  char c;
  while (Serial.available()) {
    c = Serial.read();
  }
}

