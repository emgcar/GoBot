#!/usr/bin/python

import picamera
import time
import cv2
import numpy as np
from PIL import Image
from picamera.array import PiRGBArray

camera = picamera.PiCamera()
time.sleep(0.1)
camera.capture('image.jpg')