#!/usr/bin/env python

"""color-5.py: Similar to color-4 but inside a class."""

"""
Performance @ 640x480 resolution: 

RMBP -> 0.005s each detection or 20hz 

RPI 2 -> 0.15s each detection or 6.66hz 

RPI 3 -> 0.12s each detection or 8.33hz 

"""

__author__ = "Aldo Vargas"
__copyright__ = "Copyright 2015 Aldux.net"

__license__ = "GPL"
__version__ = "1"
__maintainer__ = "Aldo Vargas"
__email__ = "alduxvm@gmail.com"
__status__ = "Development"


import numpy as np
import cv2
import time, threading


class vision:
	"""
	1st argumet:
	Colors:
	- red
	- blue
	- green
	- white

	2nd argument: 
	- True -> if you want to see camera output
	- False -> if you dont want to see camera output
	"""
	def __init__(self, targetcolor, show):
		self.cam = cv2.VideoCapture(0)
		#self.cam = cv2.VideoCapture('roomba.mp4')
		self.position = {'color':targetcolor,'found':False,'x':0,'y':0,'rate':0.0,'serX':0.0,'serY':0.0}
		self.resX=640
		self.resY=480
		self.cam.set(3,self.resX)
		self.cam.set(4,self.resY)
		self.targetcolor = targetcolor
		self.show = show

	def findcolor(self):
		while True:
			t1 = time.time()
			ret, frame = self.cam.read()
			hsv=cv2.cvtColor(frame,cv2.COLOR_BGR2HSV)
			if self.targetcolor is 'red':
				color = cv2.inRange(hsv,np.array([0,150,0]),np.array([5,255,255]))
			elif self.targetcolor is 'blue':
				color=cv2.inRange(hsv,np.array([100,50,50]),np.array([140,255,255]))
			elif self.targetcolor is 'green':
				color=cv2.inRange(hsv,np.array([40,50,50]),np.array([80,255,255]))
			else: # white is default
				sensitivity = 10
				color = cv2.inRange(hsv,np.array([0,0,255-sensitivity]),np.array([255,sensitivity,255]))
			image_mask=color
			element = cv2.getStructuringElement(cv2.MORPH_RECT,(3,3))
			image_mask = cv2.erode(image_mask,element, iterations=2)
			image_mask = cv2.dilate(image_mask,element,iterations=2)
			image_mask = cv2.erode(image_mask,element)
			contours, hierarchy = cv2.findContours(image_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
			maximumArea = 0
			bestContour = None
			for contour in contours:
				currentArea = cv2.contourArea(contour)
				if currentArea > maximumArea:
					bestContour = contour
					maximumArea = currentArea
			#Create a bounding box around the biggest color object
			if bestContour is not None:
				x,y,w,h = cv2.boundingRect(bestContour)
				cv2.rectangle(frame, (x,y),(x+w,y+h), (0,0,255), 3)
				t2 = time.time()
				self.position['found']=True
				self.position['x']=x+(w/2)
				self.position['y']=y+(h/2)
				self.position['serX'] = (self.position['x']-(self.resX/2.0))*(50.0/(self.resX/2))
				self.position['serY'] = (self.position['y']-(self.resY/2.0))*(50.0/(self.resX/2))
				self.position['rate']=round(1.0/(t2-t1),1)
				print self.position
			else:
				self.position['found']=False
				self.position['serX']=0.0
				self.position['serY']=0.0
				print self.position				
			if self.show:
				cv2.imshow( 'vision' ,frame)
			if cv2.waitKey(1) == 27:
				break


test = vision('white',True)

def aldo():
	global test
	#test = vision('white',True)
	test.findcolor()

try:
	#test = vision('red',True)
	#test.findcolor()
	#aldo()
	testThread = threading.Thread(target=test.findcolor)
	testThread.daemon=True
	testThread.start()
	testThread.join()
	while True:
		print test.position
		if cv2.waitKey(1) == 27:
			break
		time.sleep(0.1)
		pass
except Exception,error:
	print "Error in main: "+str(error)
