/*
  OBD.ino
  On-Board Diagnostics
*/

/* --- Libraries --- */
#include <Canbus.h>
#include <ArduinoJson.h>

/* --- Global --- */

// Constants
const unsigned int OUTPUT_LENGTH = 256;
const unsigned int DATA_LENGTH = 128;
const unsigned int JSON_LENGTH = 256;
const unsigned int CANBUS_LENGTH = 8;
const unsigned int BAUD = 9600;

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
}

/* --- Loop --- */
void loop() {
  
  // Check CANBus
  unsigned int UID = Canbus.message_rx(canbus_rx_buffer); // Check to see if we have a message on the Bus
  int ID = canbus_rx_buffer[0];

  // Create empty JSON buffer
  StaticJsonBuffer<JSON_LENGTH> json_buffer;
  JsonObject& root = json_buffer.createObject();
  root.printTo(data_buffer, sizeof(data_buffer));
  int chksum = checksum(data_buffer);
  sprintf(output_buffer, "{\"data\":%s,\"chksum\":%d,\"id\":%d}", data_buffer, chksum, ID);
  Serial.println(output_buffer);
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
