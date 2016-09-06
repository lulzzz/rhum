/*
  gateway.ino
*/

/* --- Libraries --- */
#include <Canbus.h>
#include <ArduinoJson.h>
#include "stdio.h"

/* --- Prototypes --- */
int checksum(char *buf);

/* --- Global --- */
// Constants
const unsigned int OUTPUT_LENGTH = 256;
const unsigned int DATA_LENGTH = 128;
const unsigned int JSON_LENGTH = 256;
const unsigned int CANBUS_LENGTH = 8;
const unsigned int BAUD = 38400;
const unsigned int DIGITS = 2;
const unsigned int PRECISION = 1;
// Message Types
const int GET_REQUEST = 1;
const int GET_RESPONSE = 2;
const int SET_REQUEST = 3;
const int SET_RESPONSE = 4;
const int CALIBRATE_REQUEST = 5;
const int CALIBRATE_RESPONSE = 6;

// Node Types
const int GATEWAY = 0;
const int MOISTURE_CONTROL_V1 = 1;

// Variables
int chksum;
int canbus_status = 0;

// Buffers
char output_buffer[OUTPUT_LENGTH];
char data_buffer[DATA_LENGTH];
unsigned char canbus_rx_buffer[CANBUS_LENGTH];  // Buffer to store the incoming data
unsigned char canbus_tx_buffer[CANBUS_LENGTH];  // Buffer to store the incoming data

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
}

/* --- Loop --- */
void loop() {
  
  // Check CANBus
  if (canbus_status) {

    // Check CANBUS
    unsigned int UID = Canbus.message_rx(canbus_rx_buffer); // Check to see if we have a message on the Bus
    int msg = canbus_rx_buffer[0];
    int nt = canbus_rx_buffer[1];
    int sn = canbus_rx_buffer[2];
    int id = canbus_rx_buffer[3];
    
    // Control network via gateway (i.e. write calibration or setpoint values)
    /*
     * TODO
     */
    if (UID != 0) {
      // Read from network
      StaticJsonBuffer<JSON_LENGTH> json_buffer;
      JsonObject& root = json_buffer.createObject();
      if (msg == GET_RESPONSE) {
        if (nt == MOISTURE_CONTROL_V1) {
          char moisture_buf[16];
          char temperature_buf[16];
          sprintf(moisture_buf, "%d.%d", canbus_rx_buffer[4], canbus_rx_buffer[5]);
          sprintf(temperature_buf, "%d.%d", canbus_rx_buffer[6], canbus_rx_buffer[7]);
          root["moisture"] = atof(moisture_buf);
          root["temperature"] = atof(temperature_buf);
        }
      }
      root.printTo(data_buffer, sizeof(data_buffer));
      int chksum = checksum(data_buffer);
      sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d,\"msg\":%d,\"nt\":%d,\"sn\":%d,\"id\":%d}", data_buffer, chksum, msg, nt, sn, id);
      Serial.println(output_buffer);
    }
  }
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
