/*
  OBD.ino
  On-Board Diagnostics
*/

/* --- Libraries --- */
#include <Canbus.h>
#include <ArduinoJson.h>
#include <RunningMedian.h>
#include <DallasTemperature.h>
#include <OneWire.h>

/* --- Global --- */
// Constants
const unsigned int DEVICE_ID = 0x01; // CHANGE DEVICE ID HERE!
const unsigned int DEVICE_TYPE = 1;
const unsigned int PUMP_RELAY_PIN = 3;
const unsigned int SOLENOID_RELAY_PIN = 4;
const unsigned int TEMP_SENSOR_PIN = 5;
const unsigned int MOISTURE_AO_PIN = 0;
const unsigned int MOISTURE_DO_PIN = 5;
const unsigned int SAMPLES = 2;
const unsigned int OUTPUT_LENGTH = 256;
const unsigned int CANBUS_LENGTH = 8;
const unsigned int DATA_LENGTH = 128;
const unsigned int BAUD = 9600;
const unsigned int JSON_LENGTH = 256;
const unsigned int LOOP_INTERVAL = 1000;

// Variables
int chksum;
int canbus_status = 0;
float mean_temperature = 0;
int moisture_setpoint = 50;

// Buffers
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];
unsigned char canbus_rx_buffer[CANBUS_LENGTH];  // Buffer to store the incoming data
unsigned char canbus_tx_buffer[CANBUS_LENGTH];  // Buffer to store the incoming data

// Objects
OneWire oneWire(TEMP_SENSOR_PIN);
DallasTemperature ds18b20(&oneWire);
RunningMedian temperature_history = RunningMedian(SAMPLES);
RunningMedian moisture_history = RunningMedian(SAMPLES);

/* --- Setup --- */
void setup() {

  // Initialize USB
  Serial.begin(BAUD);
  delay(10);
  
  // Initialise MCP2515 CAN controller at the specified speed
  int canbus_attempts = 0;
  while (!canbus_status) {
    canbus_status = Canbus.init(CANSPEED_500);
    delay(10);
  }

  // Sensors
  ds18b20.begin();

  // Relays
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(SOLENOID_RELAY_PIN, OUTPUT);
}

/* --- Loop --- */
void loop() {
  
  // Check Sensors
  int moisture_value = analogRead(MOISTURE_AO_PIN);
  moisture_history.add(moisture_value);
  int mean_moisture = moisture_history.getAverage();
  ds18b20.requestTemperatures();
  float temperature_value = ds18b20.getTempCByIndex(0);
  temperature_history.add(temperature_value);
  mean_temperature = temperature_history.getAverage();

  // Set Relays
  if (mean_moisture < moisture_setpoint) {
    digitalWrite(PUMP_RELAY_PIN, HIGH);
  }
  else {
    digitalWrite(PUMP_RELAY_PIN, LOW);
  }

  // Push to CAN
  canbus_tx_buffer[0] = DEVICE_TYPE;
  canbus_tx_buffer[1] = DEVICE_ID;
  canbus_tx_buffer[2] = int(mean_temperature);
  canbus_tx_buffer[3] = int(mean_moisture);
  Canbus.message_tx(DEVICE_ID, canbus_tx_buffer);
  
  // Pull from CAN
  unsigned int UID = Canbus.message_rx(canbus_rx_buffer); // Check to see if we have a message on the Bus
  int ID = canbus_rx_buffer[0];
  
  // Print Data to JSON Buffer
  StaticJsonBuffer<JSON_LENGTH> json_buffer;
  JsonObject& root = json_buffer.createObject();
  root["temperature"] = mean_temperature;
  root["moisture"] = mean_moisture;
  root.printTo(data_buffer, sizeof(data_buffer));
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d,\"id\":%d,\"type\":%d}", data_buffer, chksum, DEVICE_ID, DEVICE_TYPE);
  Serial.println(output_buffer);

  // Wait
  delay(LOOP_INTERVAL);
}

/* --- Functions --- */
// Checksum
int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < DATA_LENGTH; i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}
