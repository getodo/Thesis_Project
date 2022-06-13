#include <ArduinoBLE.h>
#include <Arduino_LSM9DS1.h>
#include "LSM9DS1.h"

String pos;
float acc_x, acc_y, acc_z;
float gyro_x, gyro_y, gyro_z;
static float xyz_acc[3];
static float xyz_gyro[3];

void init_LSM9DS1()
{
    if (!IMU.begin())
    {
        Serial.println("LSM9DS1 failed to initiate");
    }
}

float *read_accel()
{
    if (IMU.accelerationAvailable())
    {
        IMU.readAcceleration(acc_x, acc_y, acc_z);
    }
    xyz_acc[0] = acc_x;
    xyz_acc[1] = acc_y;
    xyz_acc[2] = acc_z;

    return xyz_acc;
}

float *read_gyro()
{
    if (IMU.gyroscopeAvailable())
    {
        IMU.readGyroscope(gyro_x, gyro_y, gyro_z);
    }
    xyz_gyro[0] = gyro_x;
    xyz_gyro[1] = gyro_y;
    xyz_gyro[2] = gyro_z;

    return xyz_gyro;
}


void print_x()
{
    Serial.print("x: ");
    Serial.println(xyz_acc[0]);
}

void print_y()
{
    Serial.print("y: ");
    Serial.println(xyz_acc[1]);
}

void print_z()
{
    Serial.print("z: ");
    Serial.println(xyz_acc[2]);
}
