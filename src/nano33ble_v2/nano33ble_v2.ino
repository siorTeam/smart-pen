#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#define BLE_BUFFER_SIZE 256
#define BtnPin D5
bool RX_BUFFER_FIXED_LENGTH = false;

const char* IMUServiceUUID = "7078692c-2793-11ed-a261-0242ac120002";

const char* IMUServiceTxCharacteristicUUID = "70786bca-2793-11ed-a261-0242ac120002";
const char* IMUServiceRxCharacteristicUUID = "70786cec-2793-11ed-a261-0242ac120002";

float acc_x, acc_y, acc_z;
float gyro_x, gyro_y, gyro_z;
float mag_x, mag_y, mag_z;

//char testData[BLE_BUFFER_SIZE] = "4.64, -2.32, 0.98, 0.03, -1.00, -0.07, 27.93, 24.38, 12.78";

char BLEBuffer[BLE_BUFFER_SIZE];
//char *RxDummy;

BLEService IMUService(IMUServiceUUID); 
BLECharacteristic IMU_Tx_Charateristic(IMUServiceTxCharacteristicUUID, BLERead | BLENotify, BLE_BUFFER_SIZE);
BLECharacteristic IMU_Rx_Charateristic(IMUServiceRxCharacteristicUUID, BLEWriteWithoutResponse | BLEWrite, BLE_BUFFER_SIZE, RX_BUFFER_FIXED_LENGTH);

//BLEDouble

void setup() 
{
  Serial.begin(115200);    // initialize serial communication
  //while (!Serial);

  pinMode(LED_BUILTIN, OUTPUT); // initialize the built-in LED pin
  pinMode(BtnPin, INPUT);

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
  IMUService.addCharacteristic(IMU_Tx_Charateristic); // Add characteristic to service
  IMUService.addCharacteristic(IMU_Rx_Charateristic);
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

      if(digitalRead(D5) == HIGH)
      {
        sprintf(BLEBuffer,"%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %1d\n"
      ,acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, 1);
      }
      else
      {
        sprintf(BLEBuffer,"%.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %.3f, %1d\n"
      ,acc_x, acc_y, acc_z, gyro_x, gyro_y, gyro_z, mag_x, mag_y, mag_z, 0);
      }
      

      IMU_Tx_Charateristic.writeValue(BLEBuffer);
      //Serial.print(BLEBuffer);
      if (IMU_Rx_Charateristic.written()) {
         //RxDummy = IMU_Rx_Charateristic.value();
       }

      delay(7);
    }
    
    Serial.println("* Disconnected to central device!");
  }
}
