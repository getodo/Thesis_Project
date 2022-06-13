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

arm_data = []
hip_data = []
activity_data = [0] * 10

connected = False
disconnected = False
action = ""
notify = False
write_arm = False
write_hip = False
arm_flag = False
hip_flag = False
# could of used an array instead of globals
arm_sit = 0
arm_cross = 0
arm_stand = 0
arm_prone = 0
arm_walk = 0
arm_run = 0
arm_starjump = 0
arm_pushup = 0
arm_plank = 0

hip_sit = 0
hip_cross = 0
hip_stand = 0
hip_prone = 0
hip_walk = 0
hip_run = 0
hip_starjump = 0
hip_pushup = 0
hip_plank = 0

sit = 0
cross = 0
stand = 0
prone = 0
walk = 0
run = 0
starjump = 0
pushup = 0
plank = 0

# <--- Change to the characteristic you want to enable notifications from.
CHARACTERISTIC_UUID_HIP = "30f3ea56-10b5-11ec-82a8-0242ac130002"
CHARACTERISTIC_UUID_ARM = "30f3ea56-10b5-11ec-82a8-0242ac130003"
ADDRESS_HIP = "0E:99:E7:E0:51:61"
ADDRESS_ARM = "D3:71:90:7B:F3:D8"

sg.change_look_and_feel('Dark Grey 13')
sg.set_options(font='Calibri 14')
bleLoop = asyncio.new_event_loop()

layout = [[sg.Text('Activity Tracker')],
            [sg.Text('Arm Sensor'), sg.Text('', size=(30,1)), sg.Text('Hip Sensor'),
            sg.Text('', size=(30,1)), sg.Text('Combined Prediction')],

            [sg.Text('Sitting:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-SITTING1-'), 
            sg.Text('', size=(20,1)), sg.Text('Sitting:', size=(8, 1)), 
            sg.Text('0', size=(10, 1), key='-SITTING2-'),  sg.Text('', size=(20,1)), 
            sg.Text('Sitting:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-SITTING3-')],

            [sg.Text('Sitcross:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-SITCROSS1-'), 
            sg.Text('', size=(20,1)), sg.Text('Sitcross:', size=(8, 1)),
            sg.Text('0', size=(10, 1), key='-SITCROSS2-'),  sg.Text('', size=(20,1)),
            sg.Text('Sitcross:', size=(8,1)), sg.Text('0', size=(10, 1), key='-SITCROSS3-')],

            [sg.Text('Standing:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-STANDING1-'), sg.Text('', size=(20,1)), 
            sg.Text('Standing:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-STANDING2-'),
            sg.Text('', size=(20,1)), sg.Text('Standing:', size=(8,1)), 
            sg.Text('0', size=(10,1), key='-STANDING3-')],

            [sg.Text('Prone:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PRONE1-'), 
            sg.Text('', size=(20,1)), sg.Text('Prone:', size=(8, 1)), 
            sg.Text('0', size=(10, 1), key='-PRONE2-'), sg.Text('', size=(20,1)), 
            sg.Text('Prone:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PRONE3-')],

            [sg.Text('Walking:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-WALKING1-'), 
            sg.Text('', size=(20,1)), sg.Text('Walking:', size=(8, 1)),
            sg.Text('0', size=(10, 1), key='-WALKING2-'), sg.Text('', size=(20,1)), 
            sg.Text('Walking:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-WALKING3-')],

            [sg.Text('Running:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-RUNNING1-'), sg.Text('', size=(20,1)), 
            sg.Text('Running:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-RUNNING2-'),
            sg.Text('', size=(20,1)), sg.Text('Running:', size=(8, 1)), sg.Text('0', size=(10, 1), 
            key='-RUNNING3-')],
            
            [sg.Text('Starjump:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-STARJUMP1-'), 
            sg.Text('', size=(20,1)), sg.Text('Starjump:', size=(8, 1)), 
            sg.Text('0', size=(10, 1), key='-STARJUMP2-'), sg.Text('', size=(20,1)), 
            sg.Text('Starjump:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-STARJUMP3-')],

            [sg.Text('Pushup:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PUSHUP1-'), 
            sg.Text('', size=(20,1)), sg.Text('Pushup:', size=(8, 1)),
            sg.Text('0', size=(10, 1), key='-PUSHUP2-'), sg.Text('', size=(20,1)), 
            sg.Text('Pushup:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PUSHUP3-')],

            [sg.Text('Plank:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PLANK1-'), sg.Text('', size=(20,1)), 
            sg.Text('Plank:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PLANK2-'), sg.Text('', size=(20,1)), 
            sg.Text('Plank:', size=(8, 1)), sg.Text('0', size=(10, 1), key='-PLANK3-')],

            [sg.Text('Arm Activity:', size=(10,1), key='-ARM ACTIVITY-'), sg.Text('', size=(29,1)), 
            sg.Text('Hip Activity', size=(10,1), key='-HIP ACTIVITY-'), sg.Text('', size=(29,1)), 
            sg.Text('Activity:', size=(10,1), key='-ACTIVITY-')],

            [sg.Button('Enable Notifications'),  sg.Button('Disable Notifications')],
            [sg.Button('Collect Arm Data'), sg.Button('Collect Hip Data')],

            [sg.Text('Activity', size=(6, 1)), sg.InputText(key='-ACTIVITY-', size=(20,1)),
            sg.Text('Filename', size=(7, 1)), sg.InputText(key='-FILENAME-', size=(20,1)),
            sg.Text('Samples', size=(7, 1)), sg.InputText(key='-SAMPLES-', size=(20,1))],
            [sg.Output(size=(108, 5), key='-STATUS-')],
            [sg.Text('', size=(105,1)), sg.Button('Exit')]
]

window = sg.Window("BLE Activity Tracker", layout)

async def notification_handler_arm(sender, data):
    global notify
    global write_arm
    global arm_sit
    global arm_cross
    global arm_stand
    global arm_prone
    global arm_walk
    global arm_run
    global arm_starjump
    global arm_pushup
    global arm_plank
    global hip_sit
    global hip_cross
    global hip_stand
    global hip_prone
    global hip_walk
    global hip_run
    global hip_starjump
    global hip_pushup
    global hip_plank
    global sit
    global cross
    global stand
    global prone
    global walk
    global run
    global starjump
    global pushup
    global plank
    global activity_data
    byte_to_string = data.decode("utf-8")
    rx_data = byte_to_string.split(" ")
    if (write_arm):
        if (rx_data[0][0] == "a"):
            trainData = {"X": rx_data[1], "Y": rx_data[2], 
                "Z": rx_data[3], "Action": action}
            arm_data.append(trainData)
    if (notify):
        if (rx_data[0] == "si"):
            window['-SITTING1-'].update(rx_data[1])
            arm_sit = float(rx_data[1])
            sit = (arm_sit + hip_sit)/2
            activity_data[0] = sit
            window['-SITTING3-'].update(sit)
        if (rx_data[0] == "sc"):
            window['-SITCROSS1-'].update(rx_data[1])
            arm_cross = float(rx_data[1])
            cross = (arm_cross + hip_cross)/2
            activity_data[1] = cross
            window['-SITCROSS3-'].update(cross)
        if (rx_data[0] == "st"):
            window['-STANDING1-'].update(rx_data[1])
            arm_stand = float(rx_data[1])
            stand = (arm_stand + hip_stand)/2
            activity_data[2] = stand
            window['-STANDING3-'].update(stand)
        if (rx_data[0] == "pr"):
            window['-PRONE1-'].update(rx_data[1])
            arm_prone = float(rx_data[1])
            prone = (arm_prone + hip_prone)/2
            activity_data[3] = prone
            window['-PRONE3-'].update(prone)
        if (rx_data[0] == "wa"):
            window['-WALKING1-'].update(rx_data[1])
            arm_walk = float(rx_data[1])
            walk = (arm_walk + hip_walk)/2
            activity_data[4] = walk
            window['-WALKING3-'].update(walk)
        if (rx_data[0] == "ru"):
            window['-RUNNING1-'].update(rx_data[1])
            arm_run = float(rx_data[1])
            run = (arm_run + hip_run)/2
            activity_data[5] = run
            window['-RUNNING3-'].update(run)
        if (rx_data[0] == "sj"):
            window['-STARJUMP1-'].update(rx_data[1])
            arm_starjump = float(rx_data[1])
            starjump = (arm_starjump + hip_starjump)/2
            activity_data[6] = starjump
            window['-STARJUMP3-'].update(starjump)
        if (rx_data[0] == "pu"):
            window['-PUSHUP1-'].update(rx_data[1])
            arm_pushup = float(rx_data[1])
            pushup = (arm_pushup + hip_pushup)/2
            activity_data[7] = pushup
            window['-PUSHUP3-'].update(pushup)
        if (rx_data[0] == "pl"):
            window['-PLANK1-'].update(rx_data[1])
            arm_plank = float(rx_data[1])
            plank = (arm_plank + hip_plank)/2
            activity_data[8] = plank
            window['-PLANK3-'].update(plank)
        if (rx_data[0] == "SIT" or rx_data[0] == "SITCROSS" or rx_data[0] == "STAND" or rx_data[0] == "LIE" 
            or rx_data[0] == "WALK" or rx_data[0] == "RUN" or rx_data[0] == "STARJUMP" or rx_data[0] == "PUSHUP" or rx_data[0] == "PLANK"):
            window['-ARM ACTIVITY-'].update(rx_data[0])
        max_value = max(activity_data)
        max_index = activity_data.index(max_value)
        set_combine_activity(max_index)
    

async def notification_handler_hip(sender, data):
    global notify
    global write_hip
    global arm_sit
    global arm_cross
    global arm_stand
    global arm_prone
    global arm_walk
    global arm_run
    global arm_starjump
    global arm_pushup
    global arm_plank
    global hip_sit
    global hip_cross
    global hip_stand
    global hip_prone
    global hip_walk
    global hip_run
    global hip_starjump
    global hip_pushup
    global hip_plank
    global sit
    global cross
    global stand
    global prone
    global walk
    global run
    global starjump
    global pushup
    global plank
    global activity_data
    byte_to_string = data.decode("utf-8")
    rx_data = byte_to_string.split(" ")
    if(write_hip):
        if (rx_data[0][0] == "a"):
            trainData = {"X": rx_data[1], "Y": rx_data[2],
                        "Z": rx_data[3], "Action": action}
            hip_data.append(trainData)
    if(notify):
        if (rx_data[0] == "si"):
            window['-SITTING2-'].update(rx_data[1])
            hip_sit = float(rx_data[1])
            sit = (arm_sit + hip_sit)/2
            activity_data[0] = sit
            window['-SITTING3-'].update(sit)
        if (rx_data[0] == "sc"):
            window['-SITCROSS2-'].update(rx_data[1])
            hip_cross = float(rx_data[1])
            cross = (arm_cross + hip_cross)/2
            activity_data[1] = cross
            window['-SITCROSS3-'].update(cross)
        if (rx_data[0] == "st"):
            window['-STANDING2-'].update(rx_data[1])
            hip_stand = float(rx_data[1])
            stand = (arm_stand + hip_stand)/2
            activity_data[2] = stand
            window['-STANDING3-'].update(stand)
        if (rx_data[0] == "pr"):
            window['-PRONE2-'].update(rx_data[1])
            hip_prone = float(rx_data[1])
            prone = (hip_prone + arm_prone)/2
            activity_data[3] = prone
            window['-PRONE3-'].update(prone)
        if (rx_data[0] == "wa"):
            window['-WALKING2-'].update(rx_data[1])
            hip_walk = float(rx_data[1])
            walk = (hip_walk + arm_walk)/2
            activity_data[4] = walk
            window['-WALKING3-'].update(walk)
        if (rx_data[0] == "ru"):
            window['-RUNNING2-'].update(rx_data[1])
            hip_run = float(rx_data[1])
            run = (arm_run + hip_run)/2
            activity_data[5] = run
            window['-RUNNING3-'].update(run)
        if (rx_data[0] == "sj"):
            window['-STARJUMP2-'].update(rx_data[1])
            hip_starjump = float(rx_data[1])
            starjump = (arm_starjump + hip_starjump)/2
            activity_data[6] = starjump
            window['-STARJUMP3-'].update(starjump)
        if (rx_data[0] == "pu"):
            window['-PUSHUP2-'].update(rx_data[1])
            hip_pushup = float(rx_data[1])
            pushup = (arm_pushup + hip_pushup)/2
            activity_data[7] = pushup
            window['-PUSHUP3-'].update(pushup)
        if (rx_data[0] == "pl"):
            window['-PLANK2-'].update(rx_data[1])
            hip_plank = float(rx_data[1])
            plank = (arm_plank + hip_plank)/2
            activity_data[8] = plank
            window['-PLANK3-'].update(plank)
        if (rx_data[0] == "SIT" or rx_data[0] == "SITCROSS" or rx_data[0] == "STAND" or rx_data[0] == "LIE" 
            or rx_data[0] == "WALK" or rx_data[0] == "RUN" or rx_data[0] == "STARJUMP" or rx_data[0] == "PUSHUP" or rx_data[0] == "PLANK"):
            window['-HIP ACTIVITY-'].update(rx_data[0])
        max_value = max(activity_data)
        max_index = activity_data.index(max_value)
        set_combine_activity(max_index)

def set_combine_activity(max_index):
    if (max_index == 0):
        window['-ACTIVITY-'].update('Sitting')
    elif (max_index == 1):
        window['-ACTIVITY-'].update('SitCross')
    elif (max_index == 2):
        window['-ACTIVITY-'].update('Stand')
    elif (max_index == 3):
        window['-ACTIVITY-'].update('Prone')
    elif (max_index == 4):
        window['-ACTIVITY-'].update('Walk')
    elif (max_index == 5):
        window['-ACTIVITY-'].update('Run')
    elif (max_index == 6):
        window['-ACTIVITY-'].update('Starjump')
    elif (max_index == 7):
        window['-ACTIVITY-'].update('Pushup')
    elif (max_index == 8):
        window['-ACTIVITY-'].update('Plank')


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
                   # print("test2")
                    if (len(arm_data) >= int(input_samples)):
                        write_arm_data(values['-ACTIVITY-'], values['-FILENAME-'])
                        arm_flag = False
                        write_arm = False
                        input_samples = 0
                        arm_data.clear()
                        print('Arm Data Collection Complete!')
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
                        print('Hip Data Collection Complete!')
                else:
                    window['-OUTPUT-'].update("Please fill both filename and activity fields")

if __name__ == "__main__": 
    loop = asyncio.get_event_loop()
    loop.create_task(gui())
    loop.run_forever()
