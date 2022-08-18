

#include <Arduino_LSM9DS1.h>

void setup() {
  Serial.begin(115200);
  
  if (!IMU.begin()) {
    Serial.println("Failed to initialize IMU!");
    while (1);
  }
}

void loop() {
  // put your main code here, to run re
  peatedly:
  float acc_x, acc_y, acc_z;

  if (IMU.accelerationAvailable()) {
    IMU.readAcceleration(acc_x, acc_y, acc_z);
  }

  float gyro_x, gyro_y, gyro_z;

  if (IMU.gyroscopeAvailable()) {
    IMU.readGyroscope(gyro_x, gyro_y, gyro_z);
  }

  float mag_x, mag_y, mag_z;

  IMU.readMagneticField(mag_x, mag_y, mag_z);

  delay(7);
  
  Serial.print(gyro_x);
  Serial.print(", ");
  Serial.print(gyro_y);
  Serial.print(", ");
  Serial.print(gyro_z);
  Serial.print(", ");

  Serial.print(acc_x);
  Serial.print(", ");
  Serial.print(acc_y);
  Serial.print(", ");
  Serial.print(acc_z);
  Serial.print(", ");

  Serial.print(mag_x);
  Serial.print(", ");
  Serial.print(mag_y);
  Serial.print(", ");
  Serial.println(mag_z);
}
