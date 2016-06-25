// Contants
const int BAUD = 9600;
const int INTERVAL = 1000;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;

// Variables
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];

void setup() {
  Serial.begin(BAUD);
}

void loop() {
  delay(INTERVAL);
  int lights = 1;
  int watering_time = 60;
  int cycle_time = 240;
  sprintf(data_buffer, "{\"lights\":%d,\"watering_time\":%d,\"cycle_time\":%d}", lights, watering_time, cycle_time);
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d}", data_buffer,chksum);
  Serial.println(output_buffer);
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}
