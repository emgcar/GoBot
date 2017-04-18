import serial
import time

def sendSpeed(speed):
	ser.write(addr)
	ser.write(0)
	ser.write(speed)
	ser.write((addr + 0 + speed) & 127)
	return

ser = serial.Serial(port="/dev/ttyAMA0", baudrate=9600, timeout=3.0)

addr = 128
sendSpeed(1)

count = 1
while count < 256:
	count = count + 1
	sendSpeed(count)
	time.sleep(0.1)

sendSpeed(0)