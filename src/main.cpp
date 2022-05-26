#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>

#include "LSM9DS1.h"
#include "ble.h"
#include "predictor.h"

float *p_one;
float *p_two;
float *p_three;
float *p_four;
float *p_five;
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
    p_one = read_LSM9DS1();
    p_two = read_LSM9DS1();
    p_three = read_LSM9DS1();
    p_four = read_LSM9DS1();
    p_five = read_LSM9DS1();
    String x = String(p_one[0], 3);
    String y = String(p_one[1], 3);
    String z = String(p_one[2], 3);
    String x2 = String(p_two[0], 3);
    String y2 = String(p_two[1], 3);
    String z2 = String(p_two[2], 3);
    String x3 = String(p_three[0], 3);
    String y3 = String(p_three[1], 3);
    String z3 = String(p_three[2], 3);
    String x4 = String(p_four[0], 3);
    String y4 = String(p_four[1], 3);
    String z4 = String(p_four[2], 3);
    String x5 = String(p_five[0], 3);
    String y5 = String(p_five[1], 3);
    String z5 = String(p_five[2], 3);
    String xyz = "a " + x + " " +  y + " " + z;
    prediction = predictor(p_one[0], p_one[1], p_one[2], p_two[0], p_two[1], p_two[2], p_three[0], p_three[1], p_three[2],
        p_four[0], p_four[1], p_four[2], p_five[0], p_five[1], p_five[2]); // this is scuffed
    
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
