#!/usr/bin/python

import picamera
import time
import cv2
import numpy as np
from PIL import Image

#img = cv2.imread('image.jpg')
#img = cv2.medianBlur(img,5)
#img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

#th3 = cv2.adaptiveThreshold(img,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)

#n = th3.shape

#im = Image.fromarray(th3)
#im.save('image2.jpg')

img = cv2.imread('image3.png')
th3 = np.asarray(img)

print th3.shape

xdim = th3.shape[0]
ydim = th3.shape[1]

quarter = 0.33*ydim
third = 0.25*ydim

topLaneDim = [-1, -1, -1, -1]
topInside = 0
topHold = 0

bottomLaneDim = [-1, -1, -1, -1]
bottomInside = 0
bottomHold = 0

for x in xrange(xdim):
	topPx = th3[third, x, 0]
	bottomPx = th3[quarter, x, 0]
	
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
	img[third, leftX1] = [255, 0, 0]
	leftX2 = (bottomLaneDim[0] + bottomLaneDim[1])/2
	img[quarter, leftX2] = [255, 0, 0]
	leftSlope = (quarter - third)/(leftX2 - leftX1)
	leftInt = quarter - leftSlope*leftX2
	
	rightX1 = (topLaneDim[2] + topLaneDim[3])/2
	img[third, rightX1] = [255, 0, 0]
	rightX2 = (bottomLaneDim[2] + bottomLaneDim[3])/2
	img[quarter, rightX2] = [255, 0, 0]
	rightSlope = (quarter - third)/(rightX2 - rightX1)
	rightInt = quarter - rightSlope*rightX2

	intX = (rightInt-leftInt)/(leftSlope-rightSlope)
	if intX < (xdim/2)-50:
		print 'L1'
	elif intX > (xdim/2)+50:
		print 'R1'
	else:
		print '1'
elif topLaneDim[1] != -1 and bottomLaneDim[1] != -1 and topLaneDim[3] == -1 and bottomLaneDim[3] == -1:
	#for only one lane seen
	leftX1 = (topLaneDim[0] + topLaneDim[1])/2
	img[third, leftX1] = [255, 0, 0]
	leftX2 = (bottomLaneDim[0] + bottomLaneDim[1])/2
	img[quarter, leftX2] = [255, 0, 0]
	leftSlope = (quarter - third)/(leftX2 - leftX1)

	if leftSlope < -15:
		print 'L2'
	elif leftSlopt > 15:
		print 'R2'
	else:
		print '2'
else:
	print '2'

im = Image.fromarray(img)
im.save('image4.jpg')









