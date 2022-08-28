import traceback
import serial
import serial.tools.list_ports as list_ports

def print_port_prop(_port):
	print("device - description : ", _port)

	print("device          : ", _port.device)			# str | portname	_port[0], _port.__hash__
	print("description     : ", _port.description)		# str | 'n/a'		_port[1]
	print("hwid            : ", _port.hwid)				# str | 'n/a'		_port[2]
	print("interface       : ", _port.interface)		# str | NoneType
	print("location        : ", _port.location)			# str | NoneType
	print("manufacturer    : ", _port.manufacturer)		# str | NoneType
	print("name            : ", _port.name)				# str | basename of device
	print("pid             : ", _port.pid)				# str | NoneType
	print("product         : ", _port.product)			# str | NoneType
	print("serial_number   : ", _port.serial_number)	# str | NoneType
	print("vid             : ", _port.vid)				# str | NoneType
	print("usb_description : ", _port.usb_description())	# method
	print("usb_info        : ", _port.usb_info())			# method

if __name__ == "__main__":

	ports = list_ports.comports()
	print("Total port detected: ", len(ports))
	for port in ports:
		print_port_prop(port)

	_device = input("================\n위의 포트중 연결할 포트의 device를 입력해주세요:")
	try:
		with serial.Serial(_device, 115200, timeout=1.0) as ser:
			while True:
				print(ser.readline())
	except Exception as err:
		traceback.print_exc()