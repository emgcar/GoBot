#!/usr/bin/python

import RPi.GPIO as GPIO
import time

ECHO = 18
TRIG = 17

def wiringSetUp():
	print("setting up wiring")
	GPIO.setmode(GPIO.BCM)

	GPIO.setup(ECHO, GPIO.IN)
	GPIO.setup(TRIG, GPIO.OUT)
	GPIO.output(TRIG, False)
	time.sleep(2)

	print("finished wiring set up")
	return

def shutDownWiring():
	print("cleaning up wiring")
	GPIO.cleanup()
	return

def getCM():
	GPIO.output(TRIG, True)
	time.sleep(0.00001)
	GPIO.output(TRIG, False)

	GPIO.input(ECHO)

	while GPIO.input(ECHO) == 0:
		startTime = time.time()

	while GPIO.input(ECHO) == 1:
		endTime = time.time()
	travelTime = endTime - startTime

	distance = travelTime*17150
	distance = round(distance, 2)
	return distance

def parent():
	count = 0
	while count < 15:
		count = count + 1
		print getCM()
		time.sleep(2)

wiringSetUp()
parent()
shutDownWiring()