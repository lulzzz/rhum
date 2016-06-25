/*
  Hydroponics controller - Version 1
*/

// Libraries
#include <ArduinoJson.h>

// Prototypes
int getAverage(int, int);
int checksum(char *);

// Contants
const int BAUD = 9600;
const int INTERVAL = 1000;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;
const int JSON_LENGTH = 256;
const int INPUT_LENGTH = 256;

// IO PINS
const int SOILMOISTURE1_PIN = A0;
const int SOILMOISTURE2_PIN = A1;
const int SOILMOISTURE3_PIN = A2;
const int SOILMOISTURE4_PIN = A3;
const int PHOTOSENSOR1_PIN = A4;
const int PHOTOSENSOR2_PIN = A5;
const int SOLENOID1_PIN = 6;
const int SOLENOID2_PIN = 7;
const int SOLENOID3_PIN = 8;
const int SOLENOID4_PIN = 9;

// Conversion Constants
const int PHOTOSENSOR_SAMPLES = 5;
const int PHOTOSENSOR_MIN = 0;
const int PHOTOSENSOR_MAX = 1024;
const int SOILMOISTURE_SAMPLES = 5;
const int SOILMOISTURE_MIN = 0;
const int SOILMOISTURE_MAX = 1024;

// Communication Buffers
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];
char targets_buffer[DATA_LENGTH];
char input_buffer[INPUT_LENGTH];
StaticJsonBuffer<JSON_LENGTH> json_input;
StaticJsonBuffer<JSON_LENGTH> json_sensors;
StaticJsonBuffer<JSON_LENGTH> json_targets;
JsonObject& input = json_input.createObject();
JsonObject& sensors = json_sensors.createObject();
JsonObject& targets = json_targets.createObject();

// Variables
int cycle_time = 0;
int watering_time = 0;
int smc1 = 0;
int smc2 = 0;
int smc3 = 0;
int smc4 = 0;

// Setup
void setup(void) {
  Serial.begin(BAUD);
  pinMode(SOLENOID1_PIN, OUTPUT);
  pinMode(SOLENOID2_PIN, OUTPUT);
  pinMode(SOLENOID3_PIN, OUTPUT);
  pinMode(SOLENOID4_PIN, OUTPUT);
}

void loop(void) {
  delay(INTERVAL);
  
  // Update Targets
  if (Serial.available() > 0) {
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      input_buffer[i] = c;
      i++;
    }
    JsonObject& input = json_input.parseObject(input_buffer);
    smc1 = input["smc1"];
    smc2 = input["smc2"];
    smc3 = input["smc3"];
    smc4 = input["smc4"];
    watering_time = input["watering"];
    cycle_time = input["cycle"];
    while (Serial.available() > 0) {
      Serial.read();
    }
  }
  
  // Update Targets
  targets["smc1"] = smc1;
  targets["smc2"] = smc2;
  targets["smc3"] = smc3;
  targets["smc4"] = smc4;
  targets["watering"] = watering_time;
  targets["cycle"] = cycle_time;
  targets.printTo(targets_buffer, sizeof(targets_buffer));
  
  // Update Sensors
  sensors["photo1"] = map(getAverage(PHOTOSENSOR1_PIN, PHOTOSENSOR_SAMPLES), PHOTOSENSOR_MIN, PHOTOSENSOR_MAX, 0, 100);
  sensors["photo2"] = map(getAverage(PHOTOSENSOR2_PIN, PHOTOSENSOR_SAMPLES), PHOTOSENSOR_MIN, PHOTOSENSOR_MAX, 0, 100);
  sensors["smc1"] = map(getAverage(SOILMOISTURE1_PIN, SOILMOISTURE_SAMPLES), SOILMOISTURE_MIN, SOILMOISTURE_MAX, 0, 100);
  sensors["smc2"] = map(getAverage(SOILMOISTURE2_PIN, SOILMOISTURE_SAMPLES), SOILMOISTURE_MIN, SOILMOISTURE_MAX, 0, 100);
  sensors["smc3"] = map(getAverage(SOILMOISTURE3_PIN, SOILMOISTURE_SAMPLES), SOILMOISTURE_MIN, SOILMOISTURE_MAX, 0, 100);
  sensors["smc4"] = map(getAverage(SOILMOISTURE4_PIN, SOILMOISTURE_SAMPLES), SOILMOISTURE_MIN, SOILMOISTURE_MAX, 0, 100);
  sensors.printTo(data_buffer, sizeof(data_buffer));
  
  // Push values to node
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"targets\":%s,\"chksum\":%d}", data_buffer, targets_buffer, chksum);
  Serial.println(output_buffer);
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}

int getAverage(int analog_pin, int n) {
  long sum = 0;
  for (int i = 0; i < n; i++ ) {
    sum = sum + analogRead(analog_pin);
  }
  return sum / n;
}
