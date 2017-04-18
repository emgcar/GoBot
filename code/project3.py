#!/usr/bin/python

import os, fcntl
import time
import RPi.GPIO as GPIO
import picamera
import picamera.array
import sys
import cv2
import numpy as np
from PIL import Image
from picamera.array import PiRGBArray

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
	camera = picamera.PiCamera()
	time.sleep(0.1)
	camera.capture('image.jpg')
	return

def applyFilter():
	img = cv2.imread('image.jpg')
	img = cv2.medianBlur(img,5)
	img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
	th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)
	return th3

def findLanes(th3):
	ydim = th3.shape[0]
	xdim = th3.shape[1]

	# from top, so I'm only looking at directly in front of it
	quarter = 0.75*ydim
	third = 0.66*ydim

	topLaneDim = [-1, -1, -1, -1]
	topInside = 0
	topHold = 0

	bottomLaneDim = [-1, -1, -1, -1]
	bottomInside = 0
	bottomHold = 0
	for x in xrange(xdim):
		topPx = th3[third, x]
		bottomPx = th3[quarter, x]
		
		if topLaneDim[1] == -1:
			if topPx > 50 and topInside == 1:
				diff = x - topLaneDim[0]
				if diff > 20:
					topLaneDim[0] = topHold
					topHold = 0
					topLaneDim[1] = x
				topInside = 0
			elif topPx < 50 and topInside == 0:
				topInside = 1
				topHold = x
		else:
			if topPx > 50 and topInside == 1:
				diff = x - topLaneDim[2]
				if diff > 20:
					topLaneDim[2] = topHold
					topHold = 0
					topLaneDim[3] = x
				topInside = 0
			elif topPx < 50 and topInside == 0:
				topInside = 1
				topHold = x
	
		if bottomLaneDim[1] == -1:
			if bottomPx > 50 and bottomInside == 1:
				diff = x - bottomLaneDim[0]
				if diff > 20:
					bottomLaneDim[0] = bottomHold
					bottomHold = 0
					bottomLaneDim[1] = x
				topInside = 0
			elif bottomPx < 50 and bottomInside == 0:
				bottomInside = 1
				bottomHold = x
		else:
			if bottomPx > 50 and bottomInside == 1:
				diff = x - bottomLaneDim[2]
				if diff > 20:
					bottomLaneDim[2] = bottomHold
					bottomHold = 0
					bottomLaneDim[3] = x
				bottomInside = 0
			elif bottomPx < 50 and bottomInside == 0:
				bottomInside = 1
				bottomHold = x
	
	#finishing row if in the middle of a lane
	if topLaneDim[2] != -1 and topLaneDim[3] == -1:
		topLaneDim[3] = xdim
	elif topLaneDim[0] != -1 and topLaneDim[1] == -1:
		topLaneDim[1] = xdim
	
	if bottomLaneDim[2] != -1 and bottomLaneDim[3] == -1:
		bottomLaneDim[3] = xdim
	elif bottomLaneDim[0] != -1 and bottomLaneDim[1] == -1:
		bottomLaneDim[1] = xdim
	
	print topLaneDim
	print bottomLaneDim

	#making turning decisions
	if topLaneDim[3] != -1 and bottomLaneDim[3] != -1:
		#for both lanes seen
		leftX1 = (topLaneDim[0] + topLaneDim[1])/2
		leftX2 = (bottomLaneDim[0] + bottomLaneDim[1])/2
		leftSlope = (quarter - third)/(leftX2 - leftX1)
		leftInt = quarter - leftSlope*leftX2
		
		rightX1 = (topLaneDim[2] + topLaneDim[3])/2
		rightX2 = (bottomLaneDim[2] + bottomLaneDim[3])/2
		rightSlope = (quarter - third)/(rightX2 - rightX1)
		rightInt = quarter - rightSlope*rightX2
	
		intX = (rightInt-leftInt)/(leftSlope-rightSlope)
		if intX < (xdim/2)-50:
			print 'L1'
			return 'L'
		elif intX > (xdim/2)+50:
			print 'R1'
			return 'R'
		else:
			print '1'
	elif topLaneDim[1] != -1 and bottomLaneDim[1] != -1 and topLaneDim[3] == -1 and bottomLaneDim[3] == -1:
		#for only one lane seen
		leftX1 = (topLaneDim[0] + topLaneDim[1])/2
		leftX2 = (bottomLaneDim[0] + bottomLaneDim[1])/2
		leftSlope = (quarter - third)/(leftX2 - leftX1)
	
		if leftSlope < -15:
			print 'L2'
			return 'L'
		elif leftSlopt > 15:
			print 'R2'
			return 'R'
		else:
			print '2'
	else:
		print '2'

	return '0'

def laneChild(r, w):
	print("starting lane detection child")
	w = os.fdopen(w, 'w')
	os.close(r)

	takePicture()
	th3 = applyFilter()
	ans = findLanes(th3)
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

