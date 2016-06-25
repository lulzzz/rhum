/*
  Hydroponics Controller - Bronfman 
*/
  
/* --- Libraries --- */
#include <ArduinoJson.h>

/* --- Prototypes --- */
int readAverage(const int, const int, const int);
float toVoltage(const int, const int, const int);
int getLuminosity(const int, const int);
int getMoistureContent (const int, const int);
void setRelay(const int, const boolean);
boolean controlMoisture(int, int, boolean);
int checksum(char*);

/* --- Constants --- */
// JSON / Serial
const int INPUT_LENGTH = 256;
const int OUTPUT_LENGTH = 256;
const int DATA_LENGTH = 128;
const int BAUD_RATE = 9600;
const int INTERVAL = 20;

// Soil Moisture Sensors (VH400)
const int PIN_D_SENSOR_SMC_1 = 2;
const int PIN_D_SENSOR_SMC_2 = 3;
const int PIN_D_SENSOR_SMC_3 = 5;
const int PIN_D_SENSOR_SMC_4 = 4;
const int SMC_DEADBAND = 10; // %
const int SMC_NUM_SAMPLES = 5;

// Photosensors (950 Ohm)
const int PIN_D_SENSOR_PHOTO_1 = 6;
const int PIN_D_SENSOR_PHOTO_2 = 7;
const int PHOTO_MIN = 50; // bits
const int PHOTO_MAX = 1024; // bits
const int PHOTO_NUM_SAMPLES = 5;

// Soil Moisture Content Relays
const int PIN_D_RELAY_SMC_1 = 8;
const int PIN_D_RELAY_SMC_2 = 9;
const int PIN_D_RELAY_SMC_3 = 11;
const int PIN_D_RELAY_SMC_4 = 10;

// Intercanopy LED Relay
const int PIN_D_RELAY_LED = 12; // set to D13 if independent

// Analog Pins
const int PIN_A_SENSOR_SMC_1 = 0;
const int PIN_A_SENSOR_SMC_2 = 1;
const int PIN_A_SENSOR_SMC_3 = 3;
const int PIN_A_SENSOR_SMC_4 = 2;
const int PIN_A_SENSOR_PHOTO_1 = 4;
const int PIN_A_SENSOR_PHOTO_2 = 5;

/* --- Variables --- */
// JSON
char data_buffer[DATA_LENGTH];
char targets_buffer[DATA_LENGTH];
char ser_buffer[OUTPUT_LENGTH];

// Relay States
boolean relay_smc_1 = false; // Drip irrigation solenoid Bed #1, south
boolean relay_smc_2 = false; // Drip irrigation solenoid Bed #2, north
boolean relay_smc_3 = false; // Drip irrigation solenoid Bed #1, south
boolean relay_smc_4 = false; // Drip irrigation solenoid Bed #2, north
boolean relay_led = false; // Intercanopy LEDS Bed #1 & #2

// Variables contenant les valeurs des capteurs
int current_smc_1 = 0;
int current_smc_2 = 0;
int current_smc_3 = 0;
int current_smc_4 = 0;
int current_photo_1 = 0;
int current_photo_2 = 0;
int target_smc_1 = 70;
int target_smc_2 = 70;
int target_smc_3 = 70;
int target_smc_4 = 70;

void setup() {

  // Initialise I/O Pins
  pinMode(PIN_D_SENSOR_SMC_1, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_1, LOW);
  pinMode(PIN_D_SENSOR_SMC_2, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_2, LOW);
  pinMode(PIN_D_SENSOR_SMC_3, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_3, LOW);
  pinMode(PIN_D_SENSOR_SMC_4, OUTPUT);
  digitalWrite(PIN_D_SENSOR_SMC_4, LOW);
  pinMode(PIN_D_SENSOR_PHOTO_1, OUTPUT);
  digitalWrite(PIN_D_SENSOR_PHOTO_1, LOW);
  pinMode(PIN_D_SENSOR_PHOTO_2, OUTPUT);
  digitalWrite(PIN_D_SENSOR_PHOTO_2, LOW);
  pinMode(PIN_D_RELAY_SMC_1, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_1, HIGH);
  pinMode(PIN_D_RELAY_SMC_2, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_2, HIGH);
  pinMode(PIN_D_RELAY_SMC_3, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_3, HIGH);
  pinMode(PIN_D_RELAY_SMC_4, OUTPUT);
  digitalWrite(PIN_D_RELAY_SMC_4, HIGH);
  pinMode(PIN_D_RELAY_LED, OUTPUT);
  digitalWrite(PIN_D_RELAY_LED, HIGH);

  // Initialize Serial
  Serial.begin(BAUD_RATE);

  // Initialize RX Buffer
  StaticJsonBuffer<INPUT_LENGTH> json_rx;
  JsonObject& dict = json_rx.createObject();
  dict["s1"] = target_smc_1;
  dict["s2"] = target_smc_2;
  dict["s3"] = target_smc_3;
  dict["s4"] = target_smc_4;
  dict["l"] = (int)relay_led;
  dict.printTo(targets_buffer, sizeof(targets_buffer));
}

void loop() {
  delay(INTERVAL);
  StaticJsonBuffer<INPUT_LENGTH> json_rx;
  StaticJsonBuffer<OUTPUT_LENGTH> json_tx;

  // Receive
  if (Serial.available() > 0) {
    memset(&ser_buffer[0], 0, sizeof(ser_buffer));
    int i = 0;
    char c = ' ';
    while (c != '}') {
      c = Serial.read();
      if (c == '\r') {
        break;
      }
      else {
        ser_buffer[i] = c;
        i++;
      }
    }
    while (Serial.available() > 0) {
      Serial.read();  // Flush remaining characters
    }
    JsonObject& dict = json_rx.parseObject(ser_buffer);
    if (dict.success()) {
      target_smc_1 = dict["s1"];
      target_smc_2 = dict["s2"];
      target_smc_3 = dict["s3"];
      target_smc_4 = dict["s4"];
      relay_led = (boolean)dict["l"];
      dict.printTo(targets_buffer, sizeof(targets_buffer));
    }
    else {
      Serial.println("Failed!");
    }
  }

  // Read Sensors
  current_smc_1 = getMoistureContent(PIN_D_SENSOR_SMC_1, PIN_A_SENSOR_SMC_1);
  current_smc_2 = getMoistureContent(PIN_D_SENSOR_SMC_2, PIN_A_SENSOR_SMC_2);
  current_smc_3 = getMoistureContent(PIN_D_SENSOR_SMC_3, PIN_A_SENSOR_SMC_3);
  current_smc_4 = getMoistureContent(PIN_D_SENSOR_SMC_4, PIN_A_SENSOR_SMC_4);
  current_photo_1 = getLuminosity(PIN_D_SENSOR_PHOTO_1, PIN_A_SENSOR_PHOTO_1);
  current_photo_2 = getLuminosity(PIN_D_SENSOR_PHOTO_2, PIN_A_SENSOR_PHOTO_2);

  // Control Irritation
  relay_smc_1 = controlMoisture(target_smc_1, current_smc_1, relay_smc_1);
  relay_smc_2 = controlMoisture(target_smc_2, current_smc_2, relay_smc_1);
  relay_smc_3 = controlMoisture(target_smc_3, current_smc_3, relay_smc_1);
  relay_smc_4 = controlMoisture(target_smc_4, current_smc_4, relay_smc_1);
  setRelay(PIN_D_RELAY_SMC_1, relay_smc_1); // Solenoid A
  setRelay(PIN_D_RELAY_SMC_2, relay_smc_2); // Solenoid B
  setRelay(PIN_D_RELAY_SMC_3, relay_smc_3); // Solenoid C
  setRelay(PIN_D_RELAY_SMC_4, relay_smc_4); // Solenoid D

  // Control Inter-canopy Lighting
  setRelay(PIN_D_RELAY_LED, relay_led);

  // Transmit
  JsonObject& dict = json_tx.createObject();
  dict["s1"] = current_smc_1;
  dict["s2"] = current_smc_2;
  dict["s3"] = current_smc_3;
  dict["s4"] = current_smc_4;
  dict["p"] = (current_photo_1 + current_photo_2) / 2; // average the two values
  dict.printTo(data_buffer, sizeof(data_buffer));
  sprintf(ser_buffer, "{\"data\":%s,\"targets\":%s,\"chksum\":%d}", data_buffer, targets_buffer, checksum(data_buffer));
  Serial.println(ser_buffer);
}

/* --- Functions --- */
// Read Pin Value
int readAverage(const int pin_write, const int pin_read, const int num_samples) {
  const int delay_millis = 100;
  int sum = 0;
  for (int i = 0; i < num_samples; i++) {
    digitalWrite(pin_write, HIGH);
    delay(delay_millis);
    sum += analogRead(pin_read);
    digitalWrite(pin_write, LOW);
  }
  return sum / num_samples;
}

// Convert to Voltage
float toVoltage(const int pin_write, const int pin_read, const int num_samples) {
  return readAverage(pin_write, pin_read, num_samples) * (5.0 / 1023.0);
}

// Return Luminosity (%)
// Assume linear relationship
int getLuminosity(const int pin_write, const int pin_read) {
  const int luminosity = map(readAverage(pin_write, pin_read, PHOTO_NUM_SAMPLES), PHOTO_MIN, PHOTO_MAX, 100, 0);
  if (luminosity < 0) {
    return 0;
  }
  else if (luminosity > 100) {
    return 100;
  }
  else {
    return luminosity;
  }
}

// Calculate Volumetric Moisture Content (%) for VH400 Sensor
// http://vegetronix.com/Products/VH400/VH400-Piecewise-Curve.phtml
int getMoistureContent (const int pin_write, const int pin_read) {
  float moisture = 0.0;
  float voltage = toVoltage(pin_write, pin_read, SMC_NUM_SAMPLES);
  if (voltage < 1.1) {
    moisture = 10.0 * voltage - 1.0;
  }
  if (voltage < 1.3) {
    moisture = 25.0 * voltage - 17.5;
  }
  if (voltage < 1.82) {
    moisture = 48.08 * voltage - 47.5;
  }
  if (voltage < 2.2) {
    moisture = 26.32 * voltage - 7.89;
  }
  if (voltage >= 2.2) {
    moisture = 26.32 * voltage - 7.89; 
  }
  if (voltage >= 2.85) {
    moisture = 219.2 * voltage - 557.6;
  }
  
  // Limit to percentage range
  if (moisture > 100) {
    moisture = 100;
  }
  else if (moisture < 0) {
    moisture = 0;
  }
  return moisture;
}

// Set Relay
void setRelay(const int pin, const boolean state) {
  delay(25);
  if (state) {
    digitalWrite(pin, LOW);
  }
  else {
    digitalWrite(pin, HIGH);
  }
}

// Function to determine if irrigation solenoid should be engaged/disengaged
// greater than SMC_TARGET --> deactivate
// less than SMC_TARGET - SMC_DEADBAND --> activate
// within SMC_TARGET +/- SMC_DEADBAND --> deactivate
boolean controlMoisture(int target, int current, boolean state) {
  // GREATER THAN
  if (current < target - SMC_DEADBAND) {
    return true; // engage if under limit - deadband
  }
  // IN RANGE
  else if ((current < target) && (current > target - SMC_DEADBAND)) {
    if (state) {
      return true; // if rising, keep rising
    }
    else {
      return false; // if falling, keep falling
    }
  }
  // LESS THAN
  else if (current > target) {
    return false; // disengage if over limit
  }
  else {
    return false; // disengage if everything is awful, THIS SHOULD NEVER HAPPEN
  }
}

int checksum(char* buf) {
  int sum = 0;
  for (int i = 0; i < sizeof(buf); i++) {
    sum = sum + buf[i];
  }
  return sum % 256;
}

