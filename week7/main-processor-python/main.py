#!/usr/bin/env python3
'''
@file: main.py
@author: lucusowl<lucusowl@gmail.com>
@version: 0.1.0
@date: 2022-08-28
@encoding: utf-8
@license: Copyright (c) 2022
'''
import threading
import queue
import serial
import serial.tools.list_ports as list_ports
import PySimpleGUI as sg

PORT_OBJ = {'thread':None, 'Object':None}
PORT_STOP_THREAD = True
PORT_INFO = {}
wind = None

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
				_queue.put(f'{data.decode("utf-8")}$connect success')
		else:
			_queue.put('$the connect is lost')

if __name__ == "__main__":

	sg.theme("DarkBlue")#("HotDogStand")

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
			sg.Multiline("output Area Ready...", key="_OUTPUT", size=(80,40), border_width=2, autoscroll=True)
		],
		[sg.StatusBar("Status Area Ready", key="_STATUS")],
	]

	wind = sg.Window('Smart-pen', LAYOUT, resizable=True)
	mesQue = queue.Queue()

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
					wind['_OUTPUT'].update('')
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

		try:
			message = mesQue.get_nowait()
		except queue.Empty:
			message = None
		else:
			_output, _status = message.split('$')
			_prev_output = wind['_OUTPUT'].get()
			wind['_OUTPUT'].update(_prev_output+'\n'+_output)
			wind['_STATUS'].update(_status)

	wind.Close()
	del wind