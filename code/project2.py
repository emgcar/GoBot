#!/usr/bin/python

import os, fcntl
import time
import RPi.GPIO as GPIO
import picamera
import picamera.array
import sys

sys.path.append('/usr/local/lib/python2.7/site-packages')

from detect_lane_houghlines import *
from detect_lane_fitline import *
from detect_lane_houghlinesP import *
from config_lane import *

LEFT_TRIG = 17
LEFT_ECHO = 18

RIGHT_TRIG = 27
RIGHT_ECHO = 22

INPUT_QUIT = 13
OUTPUT_WHEEL = 23

def makingDecisions(laneInp, obstInp):
	print("making decisions")
	if obstInp == '0':
		turnVeryLeft()
	elif obstInp == '1':
		turnLeft()
	elif obstInp == '4':
		turnRight()
	elif obstInp == '5':
		turnVeryRight()
	elif laneInp == 'L':
		turnLeft()
	elif laneInp == 'R':
		turnRight()
	elif obstInp == '2':
		turnLeft()
	elif obstInp == '3':
		turnRight()
	else:
		balanceOut()
	return

def turnVeryLeft():
	print("turn very left")
	GPIO.output(OUTPUT_WHEEL, ++leftSpeed)
	GPIO.output(OUTPUT_WHEEL, --rightSpeed)
	return

def turnLeft():
	print("turn left")
	GPIO.output(OUTPUT_WHEEL, ++leftSpeed)
	return

def balanceOut():
	print("balance out")
	leftSpeed = 10
	rightSpeed = 127 + 10
	GPIO.output(OUTPUT_WHEEL, leftSpeed)
	GPIO.output(OUTPUT_WHEEL, rightSpeed)
	return

def turnRight():
	print("turn right")
	GPIO.output(OUTPUT_WHEEL, ++leftSpeed)
	return

def turnVeryRight():
	print("turn very right")
	GPIO.output(OUTPUT_WHEEL, --leftSpeed)
	GPIO.output(OUTPUT_WHEEL, ++rightSpeed)
	return

def takePicture():
	with picamera.PiCamera() as camera:
		camera.start_preview()
		time.sleep(2)
		with picamera.array.PiRGBArray(camera) as stream:
			camera.capture(stream, format='bgr')
			image = stream.array
	return image

def laneChild(r, w):
	print("starting lane detection child")
	w = os.fdopen(w, 'w')
	os.close(r)

	img = takePicture()

	ans = detect_lane_over_fitline(img, gb_lane_cfg)

	w.write(ans)

	print("ending lane detection child")
	w.close()
	os._exit(0)

def obstChild(r, w):
	print("starting obstacle detection child")
	w = os.fdopen(w, 'w')
	os.close(r)

	leftDist = getCM(LEFT_ECHO, LEFT_TRIG)
	rightDist = getCM(RIGHT_ECHO, RIGHT_TRIG)
	
	diff = rightDist - leftDist
	if diff < -20:
		w.write('0')
	elif diff < -10:
		w.write('1')
	elif diff < -5:
		w.write('2')
	elif diff > 20:
		w.write('5')
	elif diff > 10:
		w.write('4')
	elif diff > 5:
		w.write('3')
	else:
		w.write('9')

	print("ending obstacle detection child")
	w.close()
	os._exit(0)

def getCM(trig, echo):
	GPIO.output(trig, True)
	time.sleep(0.00001)
	GPIO.output(trig, False)

	GPIO.input(echo)

	while GPIO.input(echo) == 0:
		startTime = time.time()

	while GPIO.input(echo) == 1:
		endTime = time.time()
	travelTime = endTime - startTime

	distance = travelTime*17150
	distance = round(distance, 2)
	return distance

def forkingSubprocesses():
	print("forking lane detection child")
	rLane,wLane = os.pipe()
	pidLane = os.fork()
	if pidLane == 0:
		laneChild(rLane, wLane)
	else:
		os.close(wLane)
		rLane = os.fdopen(rLane, 'r')

	print("forking obstacle detection child")
	rObst,wObst = os.pipe()
	pidObst = os.fork()
	if pidObst == 0:
		obstChild(rObst, wObst)
	else:
		os.close(wObst)
		rObst = os.fdopen(rObst, 'r')

	print("reading from child processes: ")
	laneInp = rLane.read()
	obstInp = rObst.read()
	print(laneInp, obstInp)

	print("turning off")
	rLane.close()
	rObst.close()
	return laneInp, obstInp

def parent():
	leftSpeed = 1
	rightSpeed = 128

	count = 0
	while count < 5 and GPIO.input(INPUT_QUIT) == 0:
		count = count + 1
		laneInp,obstInp = forkingSubprocesses()
		makingDecisions(laneInp, obstInp)

	print("turning off")

	return

def wiringSetUp():
	print("setting up wiring")
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(LEFT_ECHO, GPIO.IN)
	GPIO.setup(RIGHT_ECHO, GPIO.IN)
	GPIO.setup(INPUT_QUIT, GPIO.IN)

	GPIO.setup(LEFT_TRIG, GPIO.OUT)
	GPIO.setup(RIGHT_TRIG, GPIO.OUT)
	GPIO.setup(OUTPUT_WHEEL, GPIO.OUT)

	GPIO.output(LEFT_TRIG, 0)
	GPIO.output(RIGHT_TRIG, 0)
	GPIO.output(OUTPUT_WHEEL, 1)
	GPIO.output(OUTPUT_WHEEL, 128)

	print("finished wiring set up")
	return

def shutDownWiring():
	print("cleaning up wiring")
	GPIO.output(OUTPUT_WHEEL, 1)
	GPIO.output(OUTPUT_WHEEL, 128)
	GPIO.cleanup()
	return

# global variables
leftSpeed = 1
rightSpeed = 128

gb_lane_cfg = LaneCfg

wiringSetUp()
parent()
shutDownWiring()

