#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
#include "LSM9DS1.h"

String pos;
float x, y, z;
static float xyz[3];

void init_LSM9DS1()
{
    if (!IMU.begin())
    {
        Serial.println("LSM9DS1 failed to initiate");
    }
}

float *read_LSM9DS1()
{
    if (IMU.accelerationAvailable())
    {
        IMU.readAcceleration(x, y, z);
    }
    xyz[0] = x;
    xyz[1] = y;
    xyz[2] = z;

    return xyz;
}

void print_x()
{
    Serial.print("x: ");
    Serial.println(xyz[0]);
}

void print_y()
{
    Serial.print("y: ");
    Serial.println(xyz[1]);
}

void print_z()
{
    Serial.print("z: ");
    Serial.println(xyz[2]);
}