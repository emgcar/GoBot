#!/usr/bin/python

import os
import RPi.GPIO as GPIO
import time
import fcntl

INPUT_LEFT_SENSOR = 11
INPUT_RIGHT_SENSOR = 13
INPUT_QUIT = 33

OUTPUT_LEFT_SENSOR = 12
OUTPUT_RIGHT_SENSOR = 15
OUTPUT_WHEEL = 16

def wiringSetUp():
	print("setting up wiring\n")
	#GPIO.setmode(GPIO.BCM)
	GPIO.setmode(GPIO.BOARD)

	GPIO.setup(INPUT_LEFT_SENSOR, GPIO.IN)
	GPIO.setup(INPUT_RIGHT_SENSOR, GPIO.IN)
	GPIO.setup(INPUT_QUIT, GPIO.IN)

	GPIO.setup(OUTPUT_LEFT_SENSOR, GPIO.OUT)
	GPIO.setup(OUTPUT_RIGHT_SENSOR, GPIO.OUT)
	GPIO.setup(OUTPUT_WHEEL, GPIO.OUT)

	GPIO.output(OUTPUT_LEFT_SENSOR, 0)
	GPIO.output(OUTPUT_RIGHT_SENSOR, 0)
	GPIO.output(OUTPUT_WHEEL, 0)

	print("finished wiring set up\n")
	return


# input L is for lane detection to turn left
# input R is for lane detection to turn right
def laneChild(r, w):
	print("starting lane detection child\n")
	r = os.fdopen(r)
	w = os.fdopen(w, 'w')

	count = 0
	#while count < 100 and not r.read():
	while count < 100:
		count = count + 1

	print("ending lane detection child\n")
	r.close()
	w.close()
	os._exit(0)	


def getCM(inputSensor, outputSensor):
	GPIO.output(outputSensor, 1)
	time.sleep(20 / 1000000.)
	GPIO.output(outputSensor, 0)

	count = 0
	while GPIO.input(inputSensor) == 0 and count < 100:
		count = count + 1

	startTime = time.time()

	count = 0
	while GPIO.input(inputSensor) == 1 and count < 100:
		count = count + 1
	travelTime = time.time() - startTime

	distance = travelTime / 58
	return distance


# input 0-2 is turn left, 0 most urgent, 2 least urgent
# input 3-5 is turn right, 5 most urgent, 3 least urgent
def obstChild(r, w):
	print("starting obstacle detection child\n")
	r = os.fdopen(r)
	w = os.fdopen(w, 'w')

	count = 0
	#while count < 100 and not r.read():
	while count < 100:
		count = count + 1
		leftDist = getCM(INPUT_LEFT_SENSOR, OUTPUT_LEFT_SENSOR)
		rightDist = getCM(INPUT_RIGHT_SENSOR, OUTPUT_RIGHT_SENSOR)

		diff = rightDist - leftDist
		if diff < -20:
			os.write(w, '0')
		elif diff < -10:
			os.write(w, '1')
		elif diff < -5:
			os.write(w, '2')
		elif diff > 20:
			os.write(w, '5')
		elif diff > 10:
			os.write(w, '4')
		elif diff > 5:
			os.write(w, '3')

	print("ending obstacle detection child\n")
	r.close()
	w.close()
	os._exit(0)


def processSetup():
	print("forking lane detection child\n")
	rLane,wLane = os.pipe()
	pidLane = os.fork()
	if pidLane == 0:
		laneChild(rLane, wLane)
	else:
		wLane = os.fdopen(wLane, 'w')
		fcntl.fcntl(wLane, fcntl.F_SETFL, os.O_NONBLOCK)

	print("forking obstacle detection child\n")
	rObst,wObst = os.pipe()
	pidObst = os.fork()
	if pidObst == 0:
		obstChild(rObst, wObst)
	else:
		wObst = os.fdopen(wObst, 'w')
		fcntl.fcntl(wObst, fcntl.F_SETFL, os.O_NONBLOCK)

	return rLane,wLane,rObst,wObst


def turnLeft(leftSpeed):
	GPIO.output(OUTPUT_WHEEL, ++leftSpeed)
	return leftSpeed


def turnRight(rightSpeed):
	GPIO.output(OUTPUT_WHEEL, ++rightSpeed)
	return rightSpeed


def balanceOut(leftSpeed, rightSpeed):
	if rightSpeed - 127 < leftSpeed:
		GPIO.output(OUTPUT_WHEEL, --rightSpeed)
	elif rightSpeed - 127 < leftSpeed:
		GPIO.output(OUTPUT_WHEEL, --leftSpeed)
	elif leftSpeed > 10:
		GPIO.output(OUTPUT_WHEEL, --leftSpeed)
		GPIO.output(OUTPUT_WHEEL, --rightSpeed)
	elif leftSpeed < 10:
		leftSpeed = turnLeft(leftSpeed)
		rightSpeed = turnRight(rightSpeed)
	return leftSpeed, rightSpeed

def shutDownWiring():
	print("cleaning up wiring\n")
	GPIO.cleanup()
	return

def makingDecisions(rL, wL, rO, wO):
	print("making decisions\n")
	leftSpeed = 1
	rightSpeed = 128

	count = 0
	#while count < 100 and GPIO.input(INPUT_QUIT) == 0:
	while count < 100:
		count = count + 1

		rLane = os.fdopen(rL)
		fcntl.fcntl(rLane, fcntl.F_SETFL, os.O_NONBLOCK)
		#laneInp = rLane.read()
		laneInp = '-1';

		rObst = os.fdopen(rO)
		fcntl.fcntl(rObst, fcntl.F_SETFL, os.O_NONBLOCK)
		#obstInp = rObst.read()
		obstInp = '-1';

		if obstInp == '0':
			GPIO.output(OUTPUT_WHEEL, --leftSpeed)
			leftSpeed = turnLeft(leftSpeed)
		elif obstInp == '1':
			leftSpeed = turnLeft(leftSpeed)
		elif obstInp == '4':
			rightSpeed = turnRight(rightSpeed)
		elif obstInp == '5':
			GPIO.output(OUTPUT_WHEEL, --rightSpeed)
			rightSpeed = turnRight(rightSpeed)
		elif laneInp == 'L':
			leftSpeed = turnLeft(leftSpeed)
		elif laneInp == 'R':
			rightSpeed = turnRight(rightSpeed)
		elif obstInp == '2':
			leftSpeed = turnLeft(leftSpeed)
		elif obstInp == '3':
			rightSpeed = turnRight(rightSpeed)
		else:
			leftSpeed, rightSpeed = balanceOut(leftSpeed, rightSpeed)
		rLane.close()
		rObst.close()

	print("turning off\n")
	os.write(wL, 'q')
	os.write(wO, 'q')
	os.close(rL)
	os.close(wL)
	os.close(rO)
	os.close(wO)
	shutDownWiring()

	return

wiringSetUp()
rL,wL,rO,wO = processSetup()
makingDecisions(rL,wL,rO,wO)

