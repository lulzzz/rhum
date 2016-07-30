/* Welcome to the CAN RX project. This sketch uses the Canbus library.
  Originally created by SK Pang Electronics www.skpang.co.uk
  Modified to work with Jaycon Systems CAN Bus Shield
  This is the CAN RX example, ment to work in conjunction with the CAN TX Example.
  
  You will need to have atleast two Arduino/CAN setup and connected over Ethernet cables.
  Make sure you have the termination jumpers soldered on the end nodes, and POE jumpered on both boards
  if you want to power only one side.
*/

#include <Canbus.h>

unsigned int MY_ID = 0x0757; // This is the devices ID. The Lower the Number, the Higher its Priority on the CAN Bus. ID 0x0000 would be the highest Priority. (Cant have two with the same ID)
unsigned char MY_PID = 10;   // This is the ID we will use to check if the message was for this device. If you have more there one UNO with the same PID, they will all accept the message.
unsigned char RX_Buff[8];  // Buffer to store the incoming data

void setup() {
  Serial.begin(9600); // For debug use
  Serial.println("CAN RX");  
  delay(1000);
  
  if(Canbus.init(CANSPEED_500))  /* Initialise MCP2515 CAN controller at the specified speed */
    Serial.println("CAN Init ok");
  else
    Serial.println("Can't init CAN");
    
  delay(1000);
}

void loop() {
   unsigned int ID = Canbus.message_rx(RX_Buff); // Check to see if we have a message on the Bus
   if (RX_Buff[0] == MY_PID) {
    Serial.println("READ"); 
   }
}
