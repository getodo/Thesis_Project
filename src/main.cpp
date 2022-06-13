#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#include "LSM9DS1.h"
#include "ble.h"
#include "predictor.h"

float *accel_data;
float *gyro_data;
String tx;
String prediction;
String currentPrediction = " ";
String accelData = "";
unsigned long sample_timer = 0;
unsigned long sample_interval = 10;

void setup()
{
    Serial.begin(115200);
    init_LSM9DS1();
    init_ble();
    init_predictor();
}

void slow_samples()
{
    unsigned long current_millis = millis();
    while(current_millis - sample_timer <= sample_interval)
    {
        current_millis = millis();
    }
    sample_timer = current_millis;
}

void loop()
{
    BLEDevice central = BLE.central();
    slow_samples(); // wait 100ms between each sample 
    accel_data = read_accel();
    gyro_data = read_gyro();
    String accel_x = String(accel_data[0], 3);
    String accel_y = String(accel_data[1], 3);
    String accel_z = String(accel_data[2], 3);
    String gyro_x = String(gyro_data[0], 2);
    String gyro_y = String(gyro_data[1], 2);
    String gyro_z = String(gyro_data[2], 2);
    String xyz = "a " + accel_x + " " +  accel_y + " " + accel_z;
    String xyz_gyro = "g" + gyro_x + " " + gyro_y + " " + gyro_z;
    Serial.println(xyz_gyro);
    prediction = predictor(accel_data[0], accel_data[1], accel_data[2]);
    if (currentPrediction == " ")
    {
        currentPrediction = prediction;
        tx_ble_message(prediction);
    }
    if (currentPrediction != prediction)
    {
        tx_ble_message(prediction);

    }
    tx_ble_message(xyz);
    currentPrediction = prediction;
}
