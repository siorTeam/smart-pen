#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#define BLE_BUFFER_SIZE 200

const char* IMUServiceUUID = "ce34243c-1ef3-11ed-861d-0242ac120002";
const char* IMUServiceCharacteristicUUID = "ce3425fe-1ef3-11ed-861d-0242ac120002";

float acc_x, acc_y, acc_z;
float gyro_x, gyro_y, gyro_z;
float mag_x, mag_y, mag_z;

//char testData[BLE_BUFFER_SIZE] = "4.64, -2.32, 0.98, 0.03, -1.00, -0.07, 27.93, 24.38, 12.78";

char BLEBuffer[BLE_BUFFER_SIZE];
BLEService IMUService(IMUServiceUUID); 
BLECharacteristic IMUCharateristic(IMUServiceCharacteristicUUID, BLERead | BLEWrite, BLE_BUFFER_SIZE);

//BLEDouble

void setup() 
{
  Serial.begin(115200);    // initialize serial communication
  //while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin

  // initialize IMU
  if (!IMU.begin()) 
  {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }

  // initialize BLE
  if (!BLE.begin()) 
  {   
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("SmartPen");  // Set name for connection
  BLE.setAdvertisedService(IMUService); // Advertise service
  IMUService.addCharacteristic(IMUCharateristic); // Add characteristic to service
  BLE.addService(IMUService); // Add service

  BLE.advertise();  // Start advertising
  Serial.print("Peripheral device MAC: ");
  Serial.println(BLE.address());
  Serial.println("Waiting for connections...");
}

void loop() 
{
  BLEDevice central = BLE.central();
  Serial.println("- Discovering central device...");
  delay(500);

  if (central) 
  {
    Serial.println("* Connected to central device!");
    Serial.print("* Device MAC address: ");
    Serial.println(central.address());
    Serial.println(" ");

    while (central.connected()) 
    {
      if (IMU.accelerationAvailable()) 
      {
        IMU.readAcceleration(acc_x, acc_y, acc_z);
      }

      if (IMU.gyroscopeAvailable()) 
      {
        IMU.readGyroscope(gyro_x, gyro_y, gyro_z);
      }
      if(IMU.magneticFieldAvailable())
      {
        IMU.readMagneticField(mag_x, mag_y, mag_z);
      }
      
      sprintf(BLEBuffer,"%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f"
      ,acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z);

      IMUCharateristic.writeValue(BLEBuffer);
      Serial.print(BLEBuffer);

      delay(7);
    }
    
    Serial.println("* Disconnected to central device!");
  }
}
