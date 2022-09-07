#
#  Keithley 500-SERIAL
#  RS-232 to IEEE-488 Converter
#
#  Helper class to communicate with a serial GPIB adaptor
#
import time
import serial

class KGPIB:

	def __init__(self, COM, address):
		self.address = address
		self.ser = serial.Serial(
			port=COM,
			baudrate=19200,
			parity=serial.PARITY_NONE,
			stopbits=serial.STOPBITS_ONE,
			bytesize=serial.EIGHTBITS,
			xonxoff=False
		)
		self.ser.dtr = True			# DTR powers the GPIB interface
	
	def __del__(self):
		self.ser.dtr = False
		self.ser.close()

	def init(self):
		# ensure the device have started, its old and slow device
		time.sleep(2)
		# send five carriage return for auto baud rate of device
		for i in range(0,5):
			self.ser.write(b'\r')
		time.sleep(0.5)
		self.ser.write(b'I\r\n')		#  Send 'Init' command
		self.ser.write(b'EC;0\r\n')		#  turn echo off
		self.ser.write(b'H;1\r\n')		#  turn on hardware handshake
		self.ser.write(b'X;0\r\n')		#  XON/XOFF turned off
		self.ser.write(b'TC;2\r\n')		#  terminator set to CR
		self.ser.write(b'TB;4\r\n')		#  terminator set to CRLF
		time.sleep(0.1)
		# empty the receive buffer of echo and garbage characters
		out = self.ser.read(self.ser.in_waiting)

	def send(self, command):
		out = 'OA;{:02d};{}\r\n'
		#  print(out.format(self.address, command).encode())
		self.ser.write(out.format(self.address, command).encode())
		time.sleep(0.1)		#  we need this delay

	def read(self):
		out = b'';
		#  print('EN;{:02d}\r\n'.format(self.address).encode())
		self.ser.write('EN;{:02d}\r\n'.format(self.address).encode())
		self.ser.write(b'/UT\r\n')
		time.sleep(0.1)
		if self.ser.in_waiting > 0:
			out = self.ser.read(self.ser.in_waiting)

		return out

	def clearSerialBuffer(self):
		if self.ser.in_waiting > 0:
			out = self.ser.read(self.ser.in_waiting)