import os
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

PORT_STOP_THREAD = True
PORT_OBJ = {'thread':None, 'Object':None}
PortQue = queue.Queue()
raw_imu = queue.Queue()
#raw_imu = queue.Queue()

points = np.ndarray((0,3)) #[[x,y,z], [x, y ,z] ...]
btn_arr = np.ndarray((0,), dtype = int) #[btn0, btn1, ...]
mesQue = queue.Queue()



def process_imu( _queue:queue.Queue):
	points = np.ndarray((0,3))
	btn_arr = np.ndarray((0,), dtype = int)
	num_samples = _queue.qsize()

	sample_rate = 60
	ahrs = MadgwickAHRS(sampleperiod=(1/sample_rate),  beta=0.1)

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
	filtCutOff = 0.1
	b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
	linVelHP = signal.filtfilt(b, a, linVel, axis = 0)

	
	linPos = np.zeros_like(linVelHP)

	for i in range (1, len(linVelHP)):
		linPos[i,:] = linPos[i-1,:] + linVelHP[i,:] * (1/sample_rate)

	order = 1
	filtCutOff = 0.1
	b, a = signal.butter(order, (2*filtCutOff)/(sample_rate), btype='highpass')
	linPosHP = signal.filtfilt(b, a, linPos, axis = 0)


	points = np.append(points, linPosHP, axis=0)
	btn_arr = np.append(btn_arr, btn)

	return points, btn_arr

def plotter(points, btn_arr):
	fig = plt.figure()	
	ax = fig.add_subplot(111, projection='3d', proj_type = 'ortho')
	flag = 1 #이거는 메인코드 위의 init에서 한번만 실행되야되는거
	if flag == 1:
		end = len(points) - 1 # 끝값
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
	last_idx = 0
	for idx in range(len(btn_arr)-1):
		if btn_arr[idx] == 0 and btn_arr[idx+1] == 1:
			ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 1.0)
			last_idx = idx
		elif btn_arr[idx] == 1 and btn_arr[idx+1] == 0:
			ax.plot(points[last_idx:idx-1,0], points[last_idx:idx-1,1], points[last_idx:idx-1,2], alpha = 0.0)
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

def make_main_win():
	sg.theme("DarkBlue")#("HotDogStand"
	LAYOUT = [
		[sg.Text('Smart-Pen', font="Helvetica 20 bold")],
		[
			sg.Column([
				[sg.Frame("Connect BLE",[
					[sg.Button('Connect', key="_BLE_CONNECT",expand_x = True)]
				])],
                [sg.Frame("SmartPen",[
					[sg.Button('Connect', key="_PEN_CONNECT",expand_x = True)],
                    [sg.Button('Draw', key="_Draw",expand_x = True)],
                    [sg.Button('Calibration', key="_CALIB",expand_x = True)]
				])],
			], vertical_alignment='top'),
		],
		[sg.StatusBar("Status Area Ready", key="_STATUS")],
	]
	return sg.Window('Smart-pen', LAYOUT, resizable=True,finalize=True, element_justification='center')

def make_draw_win():
	sg.theme("DarkBlue")	
	layout = [
		[sg.Text('Getting data from smartpen', font="Helvetica 20 bold")],
		[sg.Text('Click OK', font="Helvetica 20 bold")],
		[sg.Button('OK', key="_OK",expand_x = True)]
	]
	
	return sg.Window('Drawing', layout, resizable=True, finalize=True,element_justification='center')

if __name__ == "__main__":
	
	com_proc = mp.Process(target = make_BLEport, daemon = True)
	ser = serial.Serial()
	

	wind , draw_wind= make_main_win(), None
	while True:
		#_event, _values = wind.Read(timeout=100)
		window, _event, _values = sg.read_all_windows()
		#if sg.WIN_CLOSED == _event:
		#	break
		if _event == sg.WIN_CLOSED or _event==  "_OK":
			window.close()
			if window == draw_wind:  
				PortQue.put_nowait('F')   
				PORT_OBJ["thread"].join() 
				print(raw_imu)
				window2 = None
				points, btn_arr = process_imu(raw_imu)
				plotter(points, btn_arr)
			elif window == wind:     
				break
		elif "_BLE_CONNECT" == _event:
			if(not com_proc.is_alive()):
				com_proc = mp.Process(target = make_BLEport, daemon = True)
			if "Connect" == wind['_BLE_CONNECT'].get_text(): 
				com_proc.start()
				wind['_BLE_CONNECT'].update('Stop')
			else:
				com_proc.terminate()
				com_proc.join()
				wind['_BLE_CONNECT'].update('Connect')
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
			
			

				

	#wind.Close()
	#del wind
'''
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

		#try:
		#	message = mesQue.get_nowait()
		#except queue.Empty:
		#	message = None
		#else:
		#	#_output, _status = message.split('$')
		#	#_prev_output = wind['_OUTPUT'].get()
		#	#wind['_OUTPUT'].update(_prev_output+'\n'+points)
		#	#wind['_STATUS'].update(_status)
		#	pass
	

    wind.Close()
	del wind
    '''