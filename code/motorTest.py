import serial
import time

ser = serial.Serial(port="/dev/ttyAMA0", baudrate=115200, timeout=3.0)

ser.write('1')
ser.write('128')

count = 0
leftSpeed = 1+10
rightSpeed = 128+10
ser.write(str(leftSpeed))
ser.write(str(rightSpeed))
time.sleep(3)

leftSpeed = 1+5
rightSpeed = 128+15
ser.write(str(leftSpeed))
ser.write(str(rightSpeed))
time.sleep(3)

leftSpeed = 1+15
rightSpeed = 128+5
ser.write(str(leftSpeed))
ser.write(str(rightSpeed))
time.sleep(3)

leftSpeed = 1+10
rightSpeed = 128+10
ser.write(str(leftSpeed))
ser.write(str(rightSpeed))
time.sleep(3)

ser.write('1')
ser.write('128')
	