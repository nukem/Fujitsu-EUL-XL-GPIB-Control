#
#  Measure the internal resistance of a battery
#

import sys
import time
from datetime import datetime
from lib.KGPIB import KGPIB

Voc = 0.0
Vl = 0.0
Ri = 0.0
Rl = 2.0		#  Load resistance
I = 0.0

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
Voc = float(gpib.read())
msg = 'Initial voltage: {}\n\r'.format(Voc)
print(msg)

if (Voc < 0.2):
	del gpib
	sys.exit('Battery disconnected');

#  Configure Load
gpib.send('RESET')
gpib.send('RA0')
gpib.send('CRSE{:3f}'.format(Rl))

#  Turn on load
gpib.send('LO1')
gpib.clearSerialBuffer()
time.sleep(3)
gpib.send('MEAS:?')
out = gpib.read()
time.sleep(0.5)
#  Turn off load
gpib.send('LO0')
outData = out.decode().strip().split(',')
Vl = float(outData[0])
I = float(outData[1])

print("Load Resistance: {:,.2f}\r\nVoltage Loaded: {:,.2f}\r\nCurrent: {:,.2f}\r\n".format(Rl, Vl, I))

Vi = Voc - Vl
Ri = (Vi / I) * 1000	#  show in milliohms
print("Battery internal resistance: {:,.2f} milliohms".format(Ri * 1000))

del gpib