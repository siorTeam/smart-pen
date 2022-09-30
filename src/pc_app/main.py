import os
import subprocess
import threading
import multiprocessing as mp 
import queue
import serial
import serial.tools.list_ports as list_ports
import PySimpleGUI as sg

from madgwickahrs import MadgwickAHRS
from scipy import signal
from quatern2rotMat import quaternion_rotation_matrix as Rotation
import numpy as np
import csv
import math
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import time

BLE_CMD = "ble-serial -s 7078692c-2793-11ed-a261-0242ac120002 -w 70786cec-2793-11ed-a261-0242ac120002 -r 70786bca-2793-11ed-a261-0242ac120002"
PORT_STOP_THREAD = True
PORT_OBJ = {'thread':None, 'Object':None}
PortQue = queue.Queue()
raw_imu = queue.Queue()
#raw_imu = queue.Queue()

points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]
mesQue = queue.Queue()




def process_imu(_queue:queue.Queue, mag_calib:list):
    beta = 0.041
    cutoff = 0.3

    points = np.ndarray((0,3))
    btn_arr = np.ndarray((0,), dtype = int)
    num_samples = _queue.qsize()

    sample_rate = 60
    ahrs = MadgwickAHRS(sampleperiod=(1/sample_rate),  beta=beta)

    data_block = list()
    
    gyr = np.ndarray((num_samples, 3))
    acc = np.ndarray((num_samples, 3))
    mag = np.ndarray((num_samples, 3))
    btn = np.ndarray((num_samples,), dtype = int)

    for i in range(num_samples):
        line = _queue.get_nowait().strip().split(", ")
        gyr[i, :] = np.array([float(line[0]), float(line[1]), float(line[2])])
        acc[i, :] = np.array([float(line[3]), float(line[4]), float(line[5])])
        mag[i, :] = np.array([float(line[6]), float(line[7]), float(line[8])])
        btn[i] = int(line[9])

    #mag = [mag_calib[:, 0] - mag_calib[0], mag_calib[:, 1] - mag_calib[1], mag_calib[:, 2] - mag_calib[2]]
    
    
    Q = np.zeros((num_samples, 4))
    R = np.zeros((3, 3, num_samples))

    for i in range(num_samples):
        ahrs.update(gyroscope = gyr[i, :]*(math.pi/180), accelerometer = acc[i, :], magnetometer = mag[i, :])
        R[:,:,i] = np.transpose(Rotation(ahrs.quaternion.q))
        Q[i, :] = ahrs.quaternion.q

    tcAcc = np.zeros_like(acc)

    for i in range (0, len(acc)):
        tcAcc[i,:] = np.matmul(R[:,:,i], np.transpose(acc[i,:]))

    linAcc = tcAcc - np.tile([0.,0.,1.], (len(tcAcc),1))
    linAcc = linAcc * 9.81 

    linVel = np.zeros_like(linAcc)
    for i in range (1,len(linAcc)):
        linVel[i,:] = linVel[i-1,:] + linAcc[i,:] * (1/sample_rate)

    order = 1
    filtCutOff = cutoff
    b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
    linVelHP = signal.filtfilt(b, a, linVel, axis = 0)

    
    linPos = np.zeros_like(linVelHP)

    for i in range (1, len(linVelHP)):
        linPos[i,:] = linPos[i-1,:] + linVelHP[i,:] * (1/sample_rate)

    order = 1
    filtCutOff = cutoff
    b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
    linPosHP = signal.filtfilt(b, a, linPos, axis = 0)


    points = np.append(points, linPosHP, axis=0)
    btn_arr = np.append(btn_arr, btn)

    return points, btn_arr

def plotter(points, btn_arr):
    fig = plt.figure()  
    ax = fig.add_subplot(111, projection='3d', proj_type = 'ortho')
    
    #clicked_idx = np.where(btn_arr == 1)
    #s_idx = clicked_idx[0][0]
    #for idx in range(s_idx, len(btn_arr)-1):
    #    if btn_arr[idx+1] == 0:
    #        last_idx = idx
    #        break
    #first_line = points[s_idx:last_idx]
    
    #end = len(first_line) - 1 # 끝값
    end = len(points) - 1 # 끝값
    mid = end // 2 - 1 # 중간값
    fir = 0

    #vector_1 = first_line[mid]-first_line[fir]
    #vector_2 = first_line[mid]-first_line[end]
    vector_1 = points[mid]-points[fir]
    vector_2 = points[mid]-points[end]
    vector_n = np.cross(vector_1, vector_2)

    elev_rad = np.arctan2(vector_n[1], vector_n[0])
    azim_rad = np.arctan2(vector_n[2], np.sqrt(vector_n[0]**2 + vector_n[1]**2))

    # pi = 3.141592
    ax.view_init(elev=(elev_rad*np.pi/180),azim=(azim_rad*np.pi/180))

    plt.axis('off')
    ax.grid(False)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_zticks([])
    plt.grid(False)


    last_idx = 0
    for idx in range(len(btn_arr)-1):
        if btn_arr[idx] == 1 and btn_arr[idx+1] == 0:
            ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], color="b", alpha = 1.0)
            last_idx = idx
        elif btn_arr[idx] == 0 and btn_arr[idx+1] == 1:
            ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], color="b", alpha = 0.0)
            last_idx = idx

    plt.show()
    

def make_BLEport ():
    os.system("ble-serial -s 7078692c-2793-11ed-a261-0242ac120002 -w 70786cec-2793-11ed-a261-0242ac120002 -r 70786bca-2793-11ed-a261-0242ac120002")
    while True:
        pass
    
def start_serial(_port_id: str, _baud_rate: int):
    return serial.Serial(_port_id, _baud_rate)
    
def get_imu_data(ser, data_que, port_que):
    while True:
        if not port_que.empty() and port_que.get() == 'F':
            break
        if ser.is_open:
            data = ser.readline()
            if None != data:
                data_que.put_nowait(data.decode("utf-8"))

def magnetometer_calib(_queue:queue.Queue):
    
    num_samples = _queue.qsize()
    mag = np.ndarray((num_samples, 3))
    for i in range(num_samples):
        line = _queue.get_nowait().strip().split(", ")
        mag[i, :] = np.array([float(line[6]), float(line[7]), float(line[8])])

    magx_min = np.min(mag[:,0])
    magx_max = np.max(mag[:,0])
    magy_min = np.min(mag[:,1])
    magy_max = np.max(mag[:,1])
    magz_min = np.min(mag[:,2])
    magz_max = np.max(mag[:,2])

    magx_correction = (magx_max+magx_min) / 2
    magy_correction = (magy_max+magy_min) / 2
    magz_correction = (magz_max+magz_min) / 2

    f = open("mag.txt",'w')
    data = str(magx_correction) + ", "+str(magy_correction) +","+str(magy_correction)
    f.write(data)
    f.close()

    return [magx_correction, magy_correction, magz_correction]

        
def make_main_win():
    sg.theme("DarkBlue")#("HotDogStand"
    LAYOUT = [
        [sg.Text('Space-Pen', font="Helvetica 20 bold")],
        [
            sg.Column([
                [sg.Frame("Connect BLE",[
                    [sg.Button('Connect', key="_BLE_CONNECT",expand_x = True)]
                ])],
                [sg.Frame("SpacePen",[
                    [sg.Button('Connect', key="_PEN_CONNECT",expand_x = True)],
                    [sg.Button('Draw', key="_Draw",expand_x = True)],
                    [sg.Button('Calibration', key="_CALIB",expand_x = True)]
                ])],
            ], vertical_alignment='top'),
        ],
        [sg.StatusBar("Status Area Ready", key="_STATUS")],
    ]
    return sg.Window('Space-pen', LAYOUT, resizable=True,finalize=True, element_justification='center')

def make_draw_win():
    sg.theme("DarkBlue")    
    layout = [
        [sg.Text('Getting data from spacepen', font="Helvetica 13")],
        [sg.Text('Click OK if your are finished drawing', font="Helvetica 11")],
        [sg.Button('OK', key="_OK",expand_x = True)]
    ]
    
    return sg.Window('Drawing', layout, resizable=True, finalize=True,element_justification='center')

def make_calib_win():
    sg.theme("DarkBlue")    
    layout = [
        [sg.Text('Rotate pen all direction', font="Helvetica 13")],
        [sg.Text('Calibration will be finished after 5sec', font="Helvetica 11")],
    ]
    return sg.Window('Calibrating', layout, resizable=True, finalize=True,element_justification='center')

if __name__ == "__main__":

    ser = serial.Serial()
    
    calib_txt = open("mag.txt", 'r')
    line = calib_txt.readline()
    mag_calib = [float(f) for f in line.split(",")]
    calib_txt.close()

    wind , draw_wind, calib_wind = make_main_win(), None, None
    while True:
        #_event, _values = wind.Read(timeout=100)
        window, _event, _values = sg.read_all_windows()
        #if sg.WIN_CLOSED == _event:
        #   break
        if _event == sg.WIN_CLOSED or _event==  "_OK":
            window.close()
            if window == draw_wind:  
                PortQue.put_nowait('F')   
                PORT_OBJ["thread"].join() 
                draw_wind = None
                points, btn_arr = process_imu(raw_imu, mag_calib)
                plotter(points, btn_arr)
            elif window == calib_wind:
                calib_wind = None
            elif window == wind:     
                break
        elif "_BLE_CONNECT" == _event:
            #if(not com_proc.is_alive()):
            #   com_proc = mp.Process(target = make_BLEport, daemon = True)
            if "Connect" == wind['_BLE_CONNECT'].get_text(): 
                result = subprocess.Popen(BLE_CMD.split(' '), stdout=subprocess.DEVNULL, creationflags=subprocess.CREATE_NEW_CONSOLE)
        elif "_PEN_CONNECT" == _event:
            if "Connect" == wind['_PEN_CONNECT'].get_text(): 
                wind['_PEN_CONNECT'].update('Stop')
                ser = start_serial("COM9", 9600)
            else:
                wind['_PEN_CONNECT'].update('Connect')
                ser.close()
        elif "_Draw" == _event:
            draw_wind = make_draw_win()
            raw_imu = queue.Queue()
            PortQue =  queue.Queue()
            points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
            btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]
            PORT_OBJ["thread"] = threading.Thread(target= get_imu_data, args = (ser, raw_imu, PortQue), daemon= True)
            PORT_OBJ["thread"].start()
        elif "_CALIB" == _event:
            calib_wind = make_calib_win()
            raw_imu = queue.Queue()
            PortQue =  queue.Queue()
            points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
            btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]
            PORT_OBJ["thread"] = threading.Thread(target= get_imu_data, args = (ser, raw_imu, PortQue), daemon= True)
            PORT_OBJ["thread"].start()
            start_time = time.time()
            while True:
                if (time.time() - start_time) >= 5:
                    calib_wind.close()
                    break
            PortQue.put_nowait('F')   
            PORT_OBJ["thread"].join()
            mag_calib = magnetometer_calib(raw_imu)
            print(mag_calib)