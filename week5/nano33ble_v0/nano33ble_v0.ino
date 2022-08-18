#include <ArduinoBLE.h>

const char* deviceServiceUuid = "ce34243c-1ef3-11ed-861d-0242ac120002";
const char* deviceServiceCharacteristicUuid = "ce3425fe-1ef3-11ed-861d-0242ac120002";
char testData[] = "4.64, -2.32, 0.98, 0.03, -1.00, -0.07, 27.93, 24.38, 12.78";
byte testBytes[59];
BLEService IMUService(deviceServiceUuid); 
BLEByteCharacteristic IMUCharateristic(deviceServiceCharacteristicUuid, BLERead | BLEWrite);

void setup() {
  Serial.begin(9600);    // initialize serial communication
  while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin

  if (!BLE.begin()) {   // initialize BLE
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("Nano33BLE");  // Set name for connection
  BLE.setAdvertisedService(IMUService); // Advertise service
  IMUService.addCharacteristic(IMUCharateristic); // Add characteristic to service
  BLE.addService(IMUService); // Add service

  BLE.advertise();  // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections...");
}

void loop() {
  BLEDevice central = BLE.central();
  Serial.println("- Discovering central device...");
  delay(500);

  if (central) {
    Serial.println("* Connected to central device!");
    Serial.print("* Device MAC address: ");
    Serial.println(central.address());
    Serial.println(" ");

    while (central.connected()) {
      
        IMUCharateristic.writeValue((byte)0x11);

    }
    
    Serial.println("* Disconnected to central device!");
  }
}

void CharToByte(char* chars, byte* bytes, unsigned int count){
    for(unsigned int i = 0; i < count; i++)
        bytes[i] = (byte)chars[i];
}
