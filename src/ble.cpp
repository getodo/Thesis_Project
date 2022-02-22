#include <ArduinoBLE.h>
#include "LSM9DS1.h"

#define BLE_BUFFER_SIZES 16
#define BLE_DEVICE_NAME "Arduino Nano 33 BLE Sense"
#define BLE_LOCAL_NAME "Accelerometer BLE"
/*
BLEService BLEAccelerometer("30f3e81c-10b5-11ec-82a8-0242ac130003");
BLEStringCharacteristic accelerometerXYZBLE("30f3ea56-10b5-11ec-82a8-0242ac130003",
                                            BLERead | BLENotify, BLE_BUFFER_SIZES);
*/

BLEService BLEAccelerometer("30F3EA56-10B5-11EC-82A8-0242AC130003");
BLEStringCharacteristic accelerometerXYZBLE("30F3EA56-10B5-11EC-82A8-0242AC130003",
                                            BLERead | BLENotify, BLE_BUFFER_SIZES);

String ble_tx;

char bleBuffer[BLE_BUFFER_SIZES];

void init_ble()
{
    if (!BLE.begin())
    {
        Serial.println("BLE failed to Initiate");
    }

    else
    {
        BLE.setDeviceName(BLE_DEVICE_NAME);
        BLE.setLocalName(BLE_LOCAL_NAME);
        BLE.setAdvertisedService(BLEAccelerometer);
        BLEAccelerometer.addCharacteristic(accelerometerXYZBLE);
        BLE.addService(BLEAccelerometer);
        BLE.advertise();
    }
}

void tx_ble_message(String txBLE)
{
    accelerometerXYZBLE.writeValue(txBLE);
}