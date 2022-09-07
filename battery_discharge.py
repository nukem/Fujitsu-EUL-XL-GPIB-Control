#
#
#
import sys
import time
from datetime import datetime

from lib.KGPIB import KGPIB

dischargeRate = 3.0			#  discharge rate in Amps
lowVoltageCutOff = 6.0		#  voltage to turn off load
logFilename = "dlog" + datetime.now().strftime("%Y%m%d%H%M%S") + ".csv"



gpib = KGPIB('COM1', 6)
gpib.init()

#  check model number
gpib.send('MDEL:?')
out = gpib.read()
print(out.decode())
if 'EUL-300' not in out.decode():
	sys.exit('Electronic Load not Found');

#  Read battery pack initial voltage
gpib.send('MEAS:V?')
voltage = float(gpib.read())
msg = 'Initial voltage: {}\n\r'.format(voltage)

if (voltage < 0.2):
	del gpib
	sys.exit('Battery disconnected');

#  Open file for logging
logFile = open(logFilename, 'w')
logFile.write(datetime.now().strftime("%Y%m%d %H:%M:%S\n\n"))

#  Configure Load
gpib.send('RESET')
gpib.send('CCSE{:3f}'.format(dischargeRate))

#  Turn on load
startTime = time.time()
endTime = startTime
gpib.send('LO1')
gpib.clearSerialBuffer()

voltage = 0
totalCurrent = 0
while (True):
	gpib.send('MEAS:?')
	out = gpib.read()
	time.sleep(1)
	logFile.write(out.decode())
	print(out.decode())
	outData = out.decode().strip().split(',')
	voltage = float(outData[0])
	current = float(outData[1])
	totalCurrent = totalCurrent + current

	if (voltage <= lowVoltageCutOff):
		endTime = time.time()
		gpib.send('LO0')
		break

totalTime = endTime - startTime

# capacity discharged calculation
capacityAh = totalTime / 3600
capacitymAh = capacityAh * 1000
summary = "Total time: {:,}s\nTotal current: {:,}\nCapacity: {:,.2f}Ah\nCapacity: {:,.2f}mAh".format(totalTime, totalCurrent, capacityAh, capacitymAh)
logFile.write(summary)

del gpib
logFile.close()