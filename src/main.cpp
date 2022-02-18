#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
// Import TensorFlow
#include "LSM9DS1.h"
#include "ble.h"
#include "predictor.h"

float *p;
String tx;
String prediction;

void setup()
{
    Serial.begin(115200);
    init_LSM9DS1();
    init_ble();
    init_predictor();
}

void loop()
{
    // Variable to checsk if cetral device is connected
    BLEDevice central = BLE.central();
    if (central)
    {
        Serial.print("Connected to central: ");
        Serial.println(central.address());
        while (central.connected())
        {
            prediction = predictor(p[0], p[1], p[2]);
            tx_ble_message(prediction);
        }
    }
}
