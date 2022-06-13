import sys
import asyncio
import csv
import os
import PySimpleGUI as sg
import threading
import time
import sys
import multiprocessing as mp


from bleak import BleakClient
from bleak import _logger as logger

sg.change_look_and_feel('Dark Grey 13')
sg.set_options(font='Calibri 14')
bleLoop = asyncio.new_event_loop()

layout = [[sg.Text('Activity Tracker')],
            [sg.Text('Arm Sensor'), sg.Text('', size=(24,1)), sg.Text('Hip Sensor')],
            [sg.Text('x1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-X1-'), 
            sg.Text('', size=(20,1)), sg.Text('Sitting:', size=(2, 1)), 
            sg.Text('0', size=(10, 1), key='-SITTING-')],
            [sg.Text('y1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Y1-'), 
            sg.Text('', size=(20,1)), sg.Text('Sitcross:', size=(2, 1)),
            sg.Text('0', size=(10, 1), key='-SITCROSS-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Standing:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-STANDING-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Prone:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-PRONE-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Walking:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-WALKING-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Running:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-RUNNING-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Starjump:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-STARJUMP-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Pushup:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-PUSHUP-')],
            [sg.Text('z1:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-Z1-'), sg.Text('', size=(20,1)), 
            sg.Text('Plank:', size=(2, 1)), sg.Text('0', size=(10, 1), key='-PLANK-')],
            
            [sg.Text('Arm Activity:', size=(10,1), key='-ARM ACTIVITY-'), sg.Text('', size=(23,1)), 
            sg.Text('Hip Activity', size=(10,1), key='-HIP ACTIVITY-')],
            [sg.Button('Enable Notifications'),  sg.Button('Disable Notifications')],
            [sg.Button('Collect Arm Data'), sg.Button('Collect Hip Data')],
            [sg.Text('Activity', size=(6, 1)), sg.InputText(key='-ACTIVITY-', size=(20,1)),
            sg.Text('Filename', size=(7, 1)), sg.InputText(key='-FILENAME-', size=(20,1)),
            sg.Text('Samples', size=(7, 1)), sg.InputText(key='-SAMPLES-', size=(20,1))],
            [sg.Output(size=(108, 10), key='-STATUS-')],
            [sg.Text('', size=(105,1)), sg.Button('Exit')]
]

window = sg.Window("BLE Activity Tracker", layout)

arm_data = []
hip_data = []
connected = False
disconnected = False
action = ""
notify = False
write_arm = False
write_hip = False
arm_flag = False
hip_flag = False

# <--- Change to the characteristic you want to enable notifications from.
CHARACTERISTIC_UUID_HIP = "30f3ea56-10b5-11ec-82a8-0242ac130002"
CHARACTERISTIC_UUID_ARM = "30f3ea56-10b5-11ec-82a8-0242ac130003"
ADDRESS_HIP = "0E:99:E7:E0:51:61"
ADDRESS_ARM = "D3:71:90:7B:F3:D8"


async def notification_handler_arm(sender, data):
    global notify
    global write_arm
    byte_to_string = data.decode("utf-8")
    rx_data = byte_to_string.split(" ")
    if(write_arm):
        if (rx_data[0][0] == "-" or rx_data[0][0] == "0" or rx_data[0][0] == "1"):
            trainData = {"X": rx_data[0], "Y": rx_data[1],
                        "Z": rx_data[2], "Action": action}
            arm_data.append(trainData)
    if(notify):
        window['-X1-'].update(rx_data[0])
        window['-Y1-'].update(rx_data[1])
        window['-Z1-'].update(rx_data[2])

async def notification_handler_hip(sender, data):
    global notify
    global write_hip
    byte_to_string = data.decode("utf-8")
    rx_data = byte_to_string.split(" ")
    if(write_hip):
        if (rx_data[0][0] == "-" or rx_data[0][0] == "0" or rx_data[0][0] == "1"):
            trainData = {"X": rx_data[0], "Y": rx_data[1],
                        "Z": rx_data[2], "Action": action}
            hip_data.append(trainData)
        else: 
            window['-HIP ACTIVITY-'].update(rx_data[0])
    if(notify):
        window['-X2-'].update(rx_data[0])
        window['-Y2-'].update(rx_data[1])
        window['-Z2-'].update(rx_data[2])

def connect_ble():
    bleLoop.run_forever()

async def ble_connect_async(address, uuid):
    global connected
    global disconnected
    if (connected == False):
        async with BleakClient(address) as client:
            connected = await client.is_connected()
            if (connected):
                if address == ADDRESS_HIP:
                    await client.start_notify(uuid, notification_handler_hip)
                elif address == ADDRESS_ARM:
                    await client.start_notify(uuid, notification_handler_arm)
                while True:
                    if (disconnected):
                        await client.stop_notify(uuid) 
                    await asyncio.sleep(1)
                    loop.stop()
bleConnectTask2 = bleLoop.create_task(ble_connect_async(ADDRESS_ARM, CHARACTERISTIC_UUID_ARM))
bleConnectTask1 = bleLoop.create_task(ble_connect_async(ADDRESS_HIP, CHARACTERISTIC_UUID_HIP))

def write_arm_data(action, filename):
    csv_file = f"{filename}.csv"
    csv_columns = ['X', 'Y', 'Z', 'Action']
    try:
        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            for data in arm_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

def write_hip_data(action, filename):
    csv_file = f"{filename}.csv"
    csv_columns = ['X', 'Y', 'Z', 'Action']
    try:
        with open(csv_file, 'a', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
            for data in hip_data:
                writer.writerow(data)
    except IOError:
        print("I/O error")

async def gui():
    global notify, write_arm, write_hip, arm_flag, hip_flag
    connectThread = threading.Thread(target=connect_ble)
    connectThread.start()
    while True:
        event, values = window.read(timeout=100)
        if event == 'Exit' or event == sg.WIN_CLOSED:
            window.close()
            bleLoop.stop()
            connectThread.join()
            sys.exit()
        if event == 'Enable Notifications':
            notify = True
            print("Enabling Notifications")
        if event == 'Disable Notifications':
            notify = False
            print("Disabling Notifications")
        if event == 'Collect Arm Data' or write_arm == True:
            input_samples = values['-SAMPLES-']
            input_filename = values['-FILENAME-']
            input_activity = values['-ACTIVITY-']
            if input_samples.isnumeric() == False:    
                print('Please enter an integer')
            else:
                if (input_filename and input_activity) or (arm_flag == 1):
                    arm_flag = True
                    write_arm = True
                    if (len(arm_data) >= int(input_samples)):
                        write_arm_data(values['-ACTIVITY-'], values['-FILENAME-'])
                        arm_flag = False
                        write_arm = False
                        input_samples = 0
                        arm_data.clear()
                else:
                    window['-OUTPUT-'].update("Please fill both filename and activity fields")

        if event == 'Collect Hip Data' or write_hip == True:
            input_samples = values['-SAMPLES-']
            input_filename = values['-FILENAME-']
            input_activity = values['-ACTIVITY-']
            if input_samples.isnumeric() == False:    
                print('Please enter an integer')
            else:
                if (input_filename and input_activity) or (hip_flag == 1):
                    hip_flag = True
                    write_hip = True
                    if (len(hip_data) >= int(input_samples)):
                        write_hip_data(values['-ACTIVITY-'], values['-FILENAME-'])
                        hip_flag = False
                        write_hip = False
                        input_samples = 0
                        hip_data.clear()
                else:
                    window['-OUTPUT-'].update("Please fill both filename and activity fields")

if __name__ == "__main__": 
    loop = asyncio.get_event_loop()
    loop.create_task(gui())
    loop.run_forever()
