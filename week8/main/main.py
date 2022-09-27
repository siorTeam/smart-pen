#!/usr/bin/env python3
'''
@file: main.py
@author: lucusowl<lucusowl@gmail.com>
@version: 0.1.0
@date: 2022-08-28
@encoding: utf-8
@license: Copyright (c) 2022
'''
import os
import threading
import multiprocessing as mp 
import queue
import serial
import serial.tools.list_ports as list_ports
import PySimpleGUI as sg

from madgwickahrs import MadgwickAHRS
from ahrs.filters import Madgwick
from scipy import signal
from quatern2rotMat import quaternion_rotation_matrix as Rotation
import numpy as np
import csv
import math
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation
import time

PORT_OBJ = {'thread':None, 'Object':None}
FILTER_OBJ = {'thread':None, 'Object':None}
PLOT_OBJ = {'thread':None, 'Object':None}
PORT_STOP_THREAD = True
PORT_INFO = {}
BLE_PORT = False
wind = None

raw_imu = queue.Queue()
points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]
mesQue = queue.Queue()

sample_rate = 60
ahrs = MadgwickAHRS(sampleperiod=(1/sample_rate),  beta=0.1)
last_Vel = np.array([0., 0., 0. ])
last_Pos = np.array([0., 0., 0. ])

def make_BLEport ():
	os.system("ble-serial -s 7078692c-2793-11ed-a261-0242ac120002 -w 70786cec-2793-11ed-a261-0242ac120002 -r 70786bca-2793-11ed-a261-0242ac120002")
	while True:
		pass
def process_imu(_stop_thread: bool, _queue:queue.Queue):
	global points
	global ahrs
	global last_Vel
	global last_Pos
	global btn_arr
	
	num_samples = 128
	while True:

		if not _stop_thread():
			break
		if(_queue.qsize() >= num_samples):
			data_block = list()
			gyr = np.ndarray((128, 3))
			acc = np.ndarray((128, 3))
			mag = np.ndarray((128, 3))
			btn = np.ndarray((128,), dtype = int)

			for i in range(num_samples):
				line = _queue.get_nowait().split('$')[0].strip().split(", ")
				gyr[i, :] = np.array([float(line[0]), float(line[1]), float(line[2])])
				acc[i, :] = np.array([float(line[3]), float(line[4]), float(line[5])])
				mag[i, :] = np.array([float(line[6]), float(line[7]), float(line[8])])
				btn[i] = int(line[9])
			
			#i=0
			#for f in data_block[:, 9]:
			#	if f<0.5:
			#		btn[0,i] = 0
			#	else:
			#		btn[0,i] = 1
			#	i += 1
			#		
			#btn = data_block_int[:, 9]

			
			
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
			linVel[0, :] = last_Vel
			for i in range (1,len(linAcc)):
				linVel[i,:] = linVel[i-1,:] + linAcc[i,:] * (1/sample_rate)

			order = 1
			filtCutOff = 0.1
			b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
			linVelHP = signal.filtfilt(b, a, linVel, axis = 0)

			last_Vel = linVelHP[-1,:]
			linPos = np.zeros_like(linVelHP)
			linPos[0, :] = last_Pos

			for i in range (1, len(linVelHP)):
				linPos[i,:] = linPos[i-1,:] + linVelHP[i,:] * (1/sample_rate)

			order = 1
			filtCutOff = 0.1
			b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
			linPosHP = signal.filtfilt(b, a, linPos, axis = 0)

			last_Pos = linPosHP[-1, :]


			#print(linPosHP.shape)
			#print(btn.reshape(128,1))
			points = np.append(points, linPosHP, axis=0)
			btn_arr = np.append(btn_arr, btn)
			
def plotter(_stop_thread: bool):
	global points
	global btn_arr
	flag = 1
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d', proj_type = 'ortho')

	last_idx = 0
	while True:
		if not _stop_thread():
			break
		if(len(btn_arr)>=128 and flag == 1):
			end = len(points) - 1
			mid = end // 2 - 1 # 중간값
			fir = 0
			
			vector_1 = points[mid]-points[fir]
			vector_2 = points[mid]-points[end]
			vector_n = np.cross(vector_1, vector_2)

			elev_rad = np.arctan2(vector_n[1], vector_n[0])
			azim_rad = np.arctan2(vector_n[2], np.sqrt(vector_n[0]**2 + vector_n[1]**2))

			pi = 3.141592
			ax.view_init(elev=(elev_rad*pi/180),azim=(azim_rad*pi/180))

			plt.axis('off')
			ax.grid(False)
			ax.set_xticks([])
			ax.set_yticks([])
			ax.set_zticks([])
			plt.grid(False)
    
			flag = 0
		if(flag == 0):
			for idx in range(len(btn_arr)-1):
				if btn_arr[idx] == 1 and btn_arr[idx+1] == 0:
					ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 1.0)
					last_idx = idx
				elif btn_arr[idx] == 0 and btn_arr[idx+1] == 1:
					ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 0.0)
					last_idx = idx
			plt.show()
	pass
def search_port_list() -> list:
	tar = []
	_ports = list_ports.comports()
	for _port in _ports:
		tar.append(_port.device)
		PORT_INFO[_port.device] = [_port.vid, _port.pid, _port.serial_number]
	return tar

def get_port_info(_port_id: str) -> str:
	return f"VID:{PORT_INFO[_port_id][0]}\nPID:{PORT_INFO[_port_id][1]}\nSN :{PORT_INFO[_port_id][2]}"

def start_serial_data(_port_id: str, _baud_rate: int, _stop_thread: bool, _queue:queue.Queue):
	ser = serial.Serial(_port_id, _baud_rate)
	ser.flush()
	ser.readline()
	# alpha = 
	# beta = 
	# pre_remain = 
	# cur_remain = 
	# pre_time = 
	# cur_time = 
	while True:
		if not _stop_thread():
			ser.close()
			break

		if ser.is_open:
			data = ser.readline()
			if None != data:
				#print(data)
				_queue.put_nowait(f'{data.decode("utf-8")}$connect success')
		#else:
	#		_queue.put('$the connect is lost')

matplotlib.use('TkAgg')
def draw_figure(canvas, figure):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg

if __name__ == "__main__":
	
	flag = 1
	fig = plt.figure()
	ax = fig.add_subplot(111, projection='3d', proj_type = 'ortho')

	sg.theme("DarkBlue")#("HotDogStand")
	com_process = mp.Process(target = make_BLEport, daemon= True)

	LAYOUT = [
		[sg.Text('Smart-Pen', font="Helvetica 20 bold")],
		[
			sg.Column([
				[sg.Frame("Port Setting", [
					[sg.Button('Reload', key="_PORT_RELOAD", expand_x=True)],
					[sg.Listbox(search_port_list(), key="_PORT_SELECT", size=(20,6), expand_x=True, enable_events=True)],
					[sg.Text('Port Information', key="_PORT_INFO",size=(20,None), expand_x=True)],
					# [sg.Text("How many sample?"), sg.Input('', key="_DATA_SAMPLE", expand_x=True)],
					[sg.Button('Select', key="_PORT_EVENT", expand_x=True)]
				])],
				[sg.Frame("Connect BLE",[
					[sg.Button('Connect', key="_BLE_CONNECT",expand_x = True)]
				])],
				[sg.Frame("Graph Type", [
					[sg.Text('Graph Information', size=(20,None), expand_x=True)],
					[sg.Radio('type 1', "GraphType", key="_GRAPH_SELECT1", expand_x=True)],
					[sg.Radio('type 2', "GraphType", key="_GRAPH_SELECT2", expand_x=True)],
					[sg.Radio('type 3', "GraphType", key="_GRAPH_SELECT3", expand_x=True)],
					[sg.Radio('type 4', "GraphType", key="_GRAPH_SELECT4", expand_x=True)],
				])],
				[sg.Frame("Filter Setting", [
					[sg.Text('Filter Information', size=(20,None), expand_x=True)],
					[sg.Radio('type 1', "FilterType", key="_FILTER_SELECT1", expand_x=True)],
					[sg.Radio('type 2', "FilterType", key="_FILTER_SELECT2", expand_x=True)],
					[sg.Radio('type 3', "FilterType", key="_FILTER_SELECT3", expand_x=True)],
					[sg.Radio('type 4', "FilterType", key="_FILTER_SELECT4", expand_x=True)],
				])],
			], vertical_alignment='top'),
			#sg.Multiline("output Area Ready...", key="_OUTPUT", size=(80,40), border_width=2, autoscroll=True)
		],
		[sg.StatusBar("Status Area Ready", key="_STATUS")],
	]
	plot_layout = [[sg.Text('Plot test')],
          [sg.Canvas(key='-CANVAS-')],
          [sg.Button('Ok')]]
	wind = sg.Window('Smart-pen', LAYOUT, resizable=True,finalize=True, element_justification='center')
	#plot_wind = sg.Window('Matplotlib Single Graph', plot_layout, location=(0,0), finalize=True, element_justification='center', font='Helvetica 18')

	while True:
		_event, _values = wind.Read(timeout=100)
		# print([_event, _values])
		if sg.WIN_CLOSED == _event:
			break
		elif "_PORT_RELOAD" == _event:
			wind['_PORT_SELECT'].update(search_port_list())
		elif "_PORT_SELECT" == _event:
			if 0 < len(_values['_PORT_SELECT']):
				wind['_PORT_INFO'].update(get_port_info(_values['_PORT_SELECT'][0]))
				wind['_STATUS'].update(f'{_values["_PORT_SELECT"][0]} was selected')
		elif "_PORT_EVENT" == _event:
			if "Select" == wind['_PORT_EVENT'].get_text():
				if 0 < len(_values["_PORT_SELECT"]):
					wind['_PORT_EVENT'].update('Stop')
					#wind['_OUTPUT'].update('')
					PORT_STOP_THREAD = True
					PORT_OBJ["thread"] = threading.Thread(target=start_serial_data, args=(
						_values["_PORT_SELECT"][0],
						115200,
						lambda: PORT_STOP_THREAD,
						mesQue
						), daemon=True)
					PORT_OBJ["thread"].start()
			else:
				PORT_STOP_THREAD = False
				PORT_OBJ["thread"].join()
				wind['_PORT_EVENT'].update('Select')
				wind['_STATUS'].update('Stop Receiving Data')
		elif "_BLE_CONNECT" == _event:
			if "Connect" == wind['_BLE_CONNECT'].get_text():
				#com_process.start()
				wind['_BLE_CONNECT'].update('Stop')
				#wind['_OUTPUT'].update('')
				PORT_STOP_THREAD = True
				PORT_OBJ["thread"] = threading.Thread(target=start_serial_data, args=(
					"COM9",
					9600,
					lambda: PORT_STOP_THREAD,
					raw_imu
					), daemon=True)
					
				FILTER_OBJ["thread"] = threading.Thread(target=process_imu, args=(
					lambda: PORT_STOP_THREAD,
					raw_imu
					), daemon=True)
				PLOT_OBJ["thread"] = threading.Thread(target = plotter, args =(
					lambda: PORT_STOP_THREAD,
				), daemon=True)
				FILTER_OBJ["thread"].start()
				PORT_OBJ["thread"].start()
				PLOT_OBJ["thread"].start()
			else:
				PORT_STOP_THREAD = False
				#com_process.join()
				PORT_OBJ["thread"].join()
				FILTER_OBJ["thread"].join()
				PLOT_OBJ["thread"].join()
				wind['_BLE_CONNECT'].update('Connect')
				wind['_STATUS'].update('Stop Receiving Data')

		try:
			message = mesQue.get_nowait()
		except queue.Empty:
			message = None
		else:
			#_output, _status = message.split('$')
			#_prev_output = wind['_OUTPUT'].get()
			#wind['_OUTPUT'].update(_prev_output+'\n'+points)
			#wind['_STATUS'].update(_status)
			pass
	

	wind.Close()
	del wind