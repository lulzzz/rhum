/*
  moisture_regulator_v1
*/

/* --- Libraries --- */
#include <Canbus.h>
#include <ArduinoJson.h>
#include <RunningMedian.h>
#include <DallasTemperature.h>
#include <OneWire.h>
#include "stdio.h"

/* --- Global --- */
const unsigned int DEVICE_NT = 0x0001; // Node Type
const unsigned int DEVICE_SN = 1; // Device Series Number 
const unsigned int DEVICE_PN = 1; // Device Part Number
const unsigned int DEVICE_ID = 1; // Device Identification Number

// Message Types
const int GET_REQUEST = 1;
const int GET_RESPONSE = 2;
const int SET_REQUEST = 3;
const int SET_RESPONSE = 4;
const int CALIBRATE_REQUEST = 5;
const int CALIBRATE_RESPONSE = 6;

// IO Pins
const unsigned int PUMP_RELAY_PIN = 3;
const unsigned int SOLENOID_RELAY_PIN = 4;
const unsigned int TEMP_SENSOR_PIN = 5;
const unsigned int MOISTURE_DO_PIN = 6;
const unsigned int SENSOR_POWER_PIN = 7; 
const unsigned int MOISTURE_AO_PIN = 0;

// Etc
const unsigned int SAMPLES = 2;
const unsigned int OUTPUT_LENGTH = 256;
const unsigned int CANBUS_LENGTH = 8;
const unsigned int DATA_LENGTH = 128;
const unsigned int BAUD = 38400;
const unsigned int JSON_LENGTH = 256;
const unsigned int LOOP_INTERVAL = 1000;
const unsigned int DIGITS = 2;
const unsigned int PRECISION = 2;

/* --- Variables --- */
int chksum;
bool canbus_status = 0;
int moisture_sp_low = 20;
int moisture_sp_high = 70;
int temperature_sp_low = 0;
int temperature_sp_high = 100;
int volts_a = 1024;
int volts_b = 0;
int moisture_a = 0;
int moisture_b = 100;

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
  Serial.println(canbus_status);

  // Sensors
  ds18b20.begin();

  // Relays
  pinMode(PUMP_RELAY_PIN, OUTPUT);
  pinMode(SOLENOID_RELAY_PIN, OUTPUT);
  pinMode(SENSOR_POWER_PIN, OUTPUT);
  digitalWrite(SENSOR_POWER_PIN, HIGH);
}

/* --- Loop --- */
void loop() {
  
  // Check Sensors
  float moisture_value = getMoistureContent(MOISTURE_AO_PIN);
  moisture_history.add(moisture_value);
  int moisture_pv = moisture_history.getAverage();
  ds18b20.requestTemperatures();
  float temperature_value = ds18b20.getTempCByIndex(0);
  temperature_history.add(temperature_value);
  float temperature_pv = temperature_history.getAverage();

  // Set Relays (LOW THRESHOLD ONLY)
  if (moisture_pv < moisture_sp_low) {
    digitalWrite(PUMP_RELAY_PIN, HIGH);
  }
  else {
    digitalWrite(PUMP_RELAY_PIN, LOW);
  }

  // CANBUS
  int moisture_sp_low_int = getIntegerPart(moisture_sp_low);
  int moisture_sp_low_frac = getFractionalPart(moisture_sp_low);
  int moisture_sp_high_int = getIntegerPart(moisture_sp_high);
  int moisture_sp_high_frac = getFractionalPart(moisture_sp_high);
  int moisture_pv_int = getIntegerPart(moisture_pv);
  int moisture_pv_frac = getFractionalPart(moisture_pv); 
  int temperature_pv_int = getIntegerPart(temperature_pv);
  int temperature_pv_frac = getFractionalPart(temperature_pv);
  unsigned int UID = Canbus.message_rx(canbus_rx_buffer); // Check to see if we have a message on the Bus
  int message_type = canbus_rx_buffer[0];
  int nt = canbus_rx_buffer[1];
  int sn = canbus_rx_buffer[2];
  int id = canbus_rx_buffer[3];
  if ((nt == DEVICE_NT) && (sn == DEVICE_SN) && (id == DEVICE_ID)) {
    switch (message_type) {
      case SET_REQUEST:
        // Move setpoint variables to new thresholds
        moisture_sp_low = canbus_tx_buffer[4];
        moisture_sp_high = canbus_tx_buffer[5];
        // Create response
        canbus_tx_buffer[0] = SET_RESPONSE;
        canbus_tx_buffer[1] = DEVICE_NT;
        canbus_tx_buffer[2] = DEVICE_SN;
        canbus_tx_buffer[3] = DEVICE_ID;
        canbus_tx_buffer[4] = moisture_sp_low;
        canbus_tx_buffer[5] = moisture_sp_high;
        canbus_tx_buffer[6] = temperature_sp_low;
        canbus_tx_buffer[7] = temperature_sp_high;
        break;
      case CALIBRATE_REQUEST:
        // Set calibration variables to new thresholds
        moisture_a = canbus_tx_buffer[4];
        moisture_b = canbus_tx_buffer[5];
        volts_a = canbus_tx_buffer[6];
        volts_b = canbus_tx_buffer[7];
        // Create response
        canbus_tx_buffer[0] = SET_RESPONSE;
        canbus_tx_buffer[1] = DEVICE_NT;
        canbus_tx_buffer[2] = DEVICE_SN;
        canbus_tx_buffer[3] = DEVICE_ID;
        canbus_tx_buffer[4] = moisture_a;
        canbus_tx_buffer[5] = moisture_b;
        canbus_tx_buffer[6] = volts_a;
        canbus_tx_buffer[7] = volts_b;
        break;
      case GET_REQUEST:
        canbus_tx_buffer[0] = GET_RESPONSE;
        canbus_tx_buffer[1] = DEVICE_NT;
        canbus_tx_buffer[2] = DEVICE_SN;
        canbus_tx_buffer[3] = DEVICE_ID;
        canbus_tx_buffer[4] = moisture_pv_int;
        canbus_tx_buffer[5] = moisture_pv_frac; 
        canbus_tx_buffer[6] = temperature_pv_int;
        canbus_tx_buffer[7] = temperature_pv_frac;
      default:
        break;  
    }
  }
  else {
    canbus_tx_buffer[0] = GET_RESPONSE;
    canbus_tx_buffer[1] = DEVICE_NT;
    canbus_tx_buffer[2] = DEVICE_SN;
    canbus_tx_buffer[3] = DEVICE_ID;
    canbus_tx_buffer[4] = moisture_pv_int;
    canbus_tx_buffer[5] = moisture_pv_frac; 
    canbus_tx_buffer[6] = temperature_pv_int;
    canbus_tx_buffer[7] = temperature_pv_frac;
  }
  Canbus.message_tx(DEVICE_ID, canbus_tx_buffer); // Push to CAN

  // Print Data to JSON Buffer
  StaticJsonBuffer<JSON_LENGTH> json_buffer;
  JsonObject& root = json_buffer.createObject();
  char temperature_buffer[50];
  char moisture_buffer[50];
  sprintf(temperature_buffer, "%d.%d", temperature_pv_int, temperature_pv_frac);
  sprintf(moisture_buffer, "%d.%d", moisture_pv_int, moisture_pv_frac);
  root["temperature"] = temperature_buffer;
  root["moisture"] = moisture_buffer;
  root["moisture_low"] = moisture_sp_low;
  root["moisture_high"] = moisture_sp_high;
  root["temperature_low"] = temperature_sp_low;
  root["temperature_high"] = temperature_sp_high;

  root.printTo(data_buffer, sizeof(data_buffer));
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d,\"sn\":%d,\"id\":%d,\"nt\":%d}", data_buffer, chksum, DEVICE_SN, DEVICE_ID, DEVICE_NT);
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

int getFractionalPart(float value) {
  int int_part, frac_part;
  char buf[16];
  dtostrf(value, DIGITS, PRECISION, buf); 
  sscanf(buf, "%d.%d", &int_part, &frac_part);
  return frac_part;
}

int getIntegerPart(float value) {
  int int_part, frac_part;
  char buf[16];
  dtostrf(value, DIGITS, PRECISION, buf); 
  sscanf(buf, "%d.%d", &int_part, &frac_part);
  return int_part;
}

float getMoistureContent(int pin) {
  int v = analogRead(pin);
  float mc = (float)(v - volts_a) * (moisture_b - moisture_a) / (float)(volts_b - volts_a) + moisture_a;
  return mc;
}

