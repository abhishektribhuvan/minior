#include <Arduino.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Wire.h>

Adafruit_MPU6050 mpu;
unsigned long lastSendTime = 0;

void setup() {
  Serial.begin(115200);

  if (!mpu.begin()) {
    Serial.println("{\"error\": \"MPU6050 not found\"}");
    while (1);
  }
  
  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setFilterBandwidth(MPU6050_BAND_21_HZ);
}

void loop() {
  // Fire data every 20ms (50 readings per second)
  // 1000 readings will take exactly 20 seconds to calibrate.
  if (millis() - lastSendTime >= 20) {
    lastSendTime = millis(); 

    sensors_event_t a, g, temp;
    mpu.getEvent(&a, &g, &temp);

    char strX[16], strY[16], strZ[16];
    sprintf(strX, "%.4f", a.acceleration.x);
    sprintf(strY, "%.4f", a.acceleration.y);
    sprintf(strZ, "%.4f", a.acceleration.z);

    char jsonPayload[128];
    sprintf(jsonPayload, "{\"x\": %s, \"y\": %s, \"z\": %s}", strX, strY, strZ);
    Serial.println(jsonPayload);
  }
}