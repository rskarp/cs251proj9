# Skeleton Tk interface example
# Written by Bruce Maxwell
# Modified by Stephanie Taylor
#
# CS 251
# Spring 2015

# Personalized by Riley Karp
# display.py
# 4/4/2017

import Tkinter as tk
import tkFont as tkf
import tkFileDialog
import math
import random
import view
import data as d
import analysis as a
import numpy as np
import scipy.stats
import tkMessageBox

# create a class to build and manage the display
class DisplayApp:

	def __init__(self, width, height):

		#create fields for bioluminescence data
		self.circadian = False
		self.bio = None
		self.cellState = None

		#create fields for classifying categories
		self.categories = False

		#create fields for cluster analysis
		self.clusterIDX = []
		self.clusterColors = False
		self.clusterData = None

		#create fields for PCA analysis
		self.pcad = {}
		self.plotPCA = None
		self.pca = False

		#create fileds for linear regression data
		self.linReg = []
		self.linRegEnds = None
		self.slope = None
		self.intercept = None
		self.rval = None
		self.pval = None
		self.stderr = None
		self.ranges = None
		self.linRegEq = []
		self.ind = None #linReg
		self.dep = None #linReg

		#create Data object and fields
		self.data = None
		self.points = None
		self.zAxis = False
		self.colors = False
		self.sizes = False
		self.r = []
		self.headers = []
		self.axisLabels = []
		self.stats = []

		# create View parameters object
		self.view = view.View()

		# create fields for axes
		self.axes = np.matrix( [[0,0,0,1],[1,0,0,1],
								[0,0,0,1],[0,1,0,1],
								[0,0,0,1],[0,0,1,1]], dtype=float  )
		self.xLine = self.yLine = self.zLine = None
		self.x = self.y = self.z = None
		self.axisLines = [ self.xLine, self.yLine, self.zLine ]

		#create interaction constant fields for translation, rotation, and scaling
		self.ks = 1 #scaling
		self.kt = 1 #rotation
		self.kr = 1 #translation

		# create a tk object, which is the root window
		self.root = tk.Tk()

		# width and height of the window
		self.initDx = width
		self.initDy = height

		# set up the geometry for the window
		self.root.geometry( "%dx%d+50+30" % (self.initDx, self.initDy) )

		# set the title of the window
		self.root.title("D.A.V.I.S")

		# set the maximum size of the window for resizing
		self.root.maxsize( 1600, 900 )

		# setup the menus
		self.buildMenus()

		# build the controls
		self.buildControls()

		# build the Canvas
		self.buildCanvas()

		# build the axes
		self.buildAxes()

		# bring the window to the front
		self.root.lift()

		# - do idle events here to get actual canvas size
		self.root.update_idletasks()

		# now we can ask the size of the canvas
		print self.canvas.winfo_geometry()

		# set up the key bindings
		self.setBindings()

		# set up the application state
		self.objects = [] # list of data objects that will be drawn in the canvas
		self.data = None # will hold the raw data someday.
		self.baseClick = None # used to keep track of mouse movement
		self.baseClick2 = None
		self.origExtent = None
		self.origView = None
		self.points = None

	def buildAxes(self):
		#builds the x,y,and z axes lines and labels on the canvas
		vtm = self.view.build()
		pts = ( vtm * self.axes.T ).T
		self.xLine = self.canvas.create_line( pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
		self.yLine = self.canvas.create_line( pts[2,0], pts[2,1], pts[3,0], pts[3,1] )
		self.zLine = self.canvas.create_line( pts[4,0], pts[4,1], pts[5,0], pts[5,1] )

		self.x = self.canvas.create_text( pts[1,0], pts[1,1], text = 'X' )
		self.y = self.canvas.create_text( pts[3,0], pts[3,1], text = 'Y' )
		self.z = self.canvas.create_text( pts[5,0], pts[5,1], text = 'Z' )

	def updateAxes(self):
		#updates the x,y,and z axes lines and labels on the canvas
		vtm = self.view.build()
		pts = ( vtm * self.axes.T ).T
		#update lines
		self.canvas.coords(self.xLine, pts[0,0], pts[0,1], pts[1,0], pts[1,1] )
		self.canvas.coords(self.yLine, pts[2,0], pts[2,1], pts[3,0], pts[3,1] )
		self.canvas.coords(self.zLine, pts[4,0], pts[4,1], pts[5,0], pts[5,1] )
		#update labels
		self.canvas.coords(self.x, pts[1,0], pts[1,1])
		self.canvas.coords(self.y, pts[3,0], pts[3,1])
		self.canvas.coords(self.z, pts[5,0], pts[5,1])

	def buildMenus(self):

		# create a new menu
		menu = tk.Menu(self.root)

		# set the root menu to our new menu
		self.root.config(menu = menu)

		# create a variable to hold the individual menus
		menulist = []

		# create a file menu
		filemenu = tk.Menu( menu )
		menu.add_cascade( label = "File", menu = filemenu )
		menulist.append(filemenu)

		# create a command menu
		cmdmenu = tk.Menu( menu )
		menu.add_cascade( label = "Command", menu = cmdmenu )
		menulist.append(cmdmenu)

		# menu text for the elements
		# the first sublist is the set of items for the file menu
		# the second sublist is the set of items for the option menu
		menutext = [ [ '-', '-', 'Quit	\xE2\x8C\x98-Q', 'Open	\xE2\x8C\x98-O'],
						[ 'Linear Regression	\xE2\x8C\x98-L',
						  'Multiple Linear Regression	\xE2\x8C\x98-M',
						  'Principal Component Analysis	\xE2\x8C\x98-P',
						  'Cluster Analysis	\xE2\x8C\x98-C' ] ]

		# menu callback functions (note that some are left blank,
		# so that you can add functions there if you want).
		# the first sublist is the set of callback functions for the file menu
		# the second sublist is the set of callback functions for the option menu
		menucmd = [ [None, None, self.handleQuit, self.handleOpen],
					[ self.handleLinearRegression, self.handleMultLinReg, self.handlePCA,
					self.handleClustering ] ]

		# build the menu elements and callbacks
		for i in range( len( menulist ) ):
			for j in range( len( menutext[i]) ):
				if menutext[i][j] != '-':
					menulist[i].add_command( label = menutext[i][j], command=menucmd[i][j] )
				else:
					menulist[i].add_separator()

	def buildCanvas(self):
		# create the canvas object
		self.canvas = tk.Canvas( self.root, width=self.initDx, height=self.initDy )
		self.canvas.pack( expand=tk.YES, fill=tk.BOTH )
		return

	def buildControls(self):
		# build a frame and put controls in it

		### Control ###
		# make a control frame on the right
		rightcntlframe = tk.Frame(self.root)
		rightcntlframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

		# make a separator frame
		sep = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep.pack( side=tk.RIGHT, padx = 2, pady = 1, fill=tk.Y)

		# use a label to set the size of the right panel
		label = tk.Label( rightcntlframe, text="Control Panel", width=20 )
		label.pack( side=tk.TOP, pady=10 )

		# make a stats frame on the right
		self.statframe = tk.Frame(self.root)
		self.statframe.pack(side=tk.RIGHT, padx=2, pady=2, fill=tk.Y)

		# make a separator frame
		sep2 = tk.Frame( self.root, height=self.initDy, width=2, bd=1, relief=tk.SUNKEN )
		sep2.pack( side=tk.RIGHT, padx = 2, pady = 1, fill=tk.Y)

		# use a label to set the size of the right panel
		label = tk.Label( self.statframe, text="Stats", width=15 )
		label.pack( side=tk.TOP, pady=0.1 )

		#create buttons
		button1 = tk.Button( rightcntlframe, text = 'Plot Data', command = self.handlePlotData )
		save = tk.Button( rightcntlframe, text = 'Save Linear Regression', command = self.saveLinReg )
		pca = tk.Button( rightcntlframe, text = 'Manage PCA', command = self.handlePCA )
		cluster = tk.Button( rightcntlframe, text = 'Cluster Analysis', command = self.handleClustering )
		saveCluster = tk.Button( rightcntlframe, text = 'Save Clusters', command = self.saveClusters )

		#make sliders for interaction constants
		self.trans = tk.Scale( rightcntlframe, from_ = 0.1, to = 5.0, command = self.setKT,
								orient=tk.HORIZONTAL, label = 'Translation Speed',
								length = 125, resolution = 0.1 )
		self.rot = tk.Scale( rightcntlframe, from_ = 0.1, to = 5.0, command = self.setKR,
								orient=tk.HORIZONTAL, label = 'Rotation Speed',
								length = 125, resolution = 0.1 )
		self.scale = tk.Scale( rightcntlframe, from_ = 0.1, to = 5.0, command = self.setKS,
								orient=tk.HORIZONTAL, label = 'Scaling Speed',
								length = 125, resolution = 0.1 )

		#make slider and ListBox for bioluminescence data
		self.bio = tk.Scale( rightcntlframe, from_ = 1, to = 144, command = self.updateBio,
								orient=tk.HORIZONTAL, label = 'Bioluminescence Hour',
								length = 200, resolution = 1 )
		self.cellState = tk.Listbox(rightcntlframe, selectmode=tk.SINGLE, exportselection=0, height=3)
		for item in ['Base','Toxin','Washed']:
			self.cellState.insert( 'end', item )
		label = tk.Label( rightcntlframe, text="Choose cell environemnt", width=20 )

		#add objects to screen
		self.trans.pack( side = tk.TOP, pady=5 )
		self.rot.pack( side = tk.TOP, pady=5 )
		self.scale.pack( side = tk.TOP, pady=5 )
		button1.pack( side = tk.TOP, pady=5 )
		save.pack( side = tk.TOP, pady=5 )
		pca.pack( side = tk.TOP, pady=5 )
		cluster.pack( side = tk.TOP, pady=5 )
		saveCluster.pack( side = tk.TOP, pady=5 )
		label.pack( side = tk.TOP, pady=5 )
		self.cellState.pack( side = tk.TOP, pady=5 )
		self.bio.pack( side = tk.TOP, pady=5 )

		#set sliders to start at 1
		self.trans.set(1)
		self.rot.set(1)
		self.scale.set(1)
		self.bio.set(1)

		self.cellState.selection_set(0)

		return

	def updateBio(self,event):
		'''updates the color of the bioluminescence points based on relative value to other
		points. Bioluminescence data from column given by Listbox selection and slider
		in control panel.
		'''
		if ( len( self.objects ) == 0 ) or ( self.circadian == False ):
			return
		hour = str( self.bio.get() )
		cell = self.cellState.get( self.cellState.curselection()[0] )
		if cell == 'Base':
			head = 'B' + hour
		elif cell == 'Toxin':
			head = 'T' + hour
		else: # cell is Washed
			if int(hour) > 142:
				hour = '142'
			head = 'W' + hour

		colors = a.normalize_columns_separately([head],self.data)

		#create list of colors
		c = []
		for i in range( self.data.get_raw_num_rows() ):
			r = 255 * colors[i,0]
			g = 255 * colors[i,0]
			b = 255 * (1-colors[i,0])
			s = "#%02X%02X%02X" % (int(r), int(g), int(b))
			c.append(s)

		#updates colors of all the data points
		for i in range( len(self.objects) ):
			color = c[i]
			self.canvas.itemconfig( self.objects[i], fill = color )

	def addAxisLabels(self):
		#adds axis labels to side frame
		labels = []
		i = j = 0
		for axis in [ 'X: '+self.axisLabels[0], 'Y: '+self.axisLabels[1],
					  'Z: '+self.axisLabels[2], 'Color: '+self.axisLabels[3],
					  'Size: '+self.axisLabels[4] ]:
			label = tk.Label( self.statframe, text= axis, width=20 )
			label.pack( side=tk.TOP, pady=0.1 )
			labels.append(label)
			if self.axisLabels[j] != 'None':
				for s in [ ['Mean: ', round( self.axisLabels[5][i],2 )],
							['Standard Deviation: ', round( self.axisLabels[6][i],2 )],
							['Median: ', round( self.axisLabels[7][i],2 )],
							['Min: ', round( self.axisLabels[8][i][0],2 )],
							['Max: ', round( self.axisLabels[8][i][1],2 )] ]:
					statText = s[0]+ str(s[1])
					stat = tk.Label( self.statframe, text= statText, width=20 )
					stat.pack( side=tk.TOP, pady=0.1 )
					labels.append(stat)
			else:
				i += 1
			j += 1
		self.axisLabels = labels

	def addAxisStats(self):
		#calculates means, stdevs, medians, and ranges and adds them to self.axisLabels
		mean = a.mean(self.headers,self.data)
		stdev = a.stdev(self.headers,self.data)
		median = a.median(self.headers,self.data)
		range = a.data_range(self.headers,self.data)

		self.axisLabels.append(mean[:])
		self.axisLabels.append(stdev[:])
		self.axisLabels.append(median[:])
		self.axisLabels.append(range[:])

	def setBindings(self):
		# bind mouse motions to the canvas
		self.canvas.bind( '<Button-1>', self.handleMouseButton1 )
		self.canvas.bind( '<Control-Button-1>', self.handleMouseButton2 )
		self.canvas.bind( '<Button-2>', self.handleMouseButton2 )
		self.canvas.bind( '<Button-3>', self.handleMouseButton3 )
		self.canvas.bind( '<B1-Motion>', self.handleMouseButton1Motion )
		self.canvas.bind( '<B2-Motion>', self.handleMouseButton2Motion )
		self.canvas.bind( '<B3-Motion>', self.handleMouseButton3Motion )
		self.canvas.bind( '<Control-B1-Motion>', self.handleMouseButton2Motion )

		# bind command sequences to the root window
		self.root.bind( '<Command-q>', self.handleQuit )
		self.root.bind( '<Command-o>', self.handleOpen )
		self.root.bind( '<Command-r>', self.reset )
		self.root.bind( '<Command-z>', self.xzPlane )
		self.root.bind( '<Command-x>', self.xyPlane )
		self.root.bind( '<Command-y>', self.yzPlane )
		self.root.bind( '<Command-l>', self.handleLinearRegression )
		self.root.bind( '<Command-s>', self.saveLinReg )
		self.root.bind( '<Command-m>', self.handleMultLinReg )
		self.root.bind( '<Command-p>', self.handlePCA )
		self.root.bind( '<Command-c>', self.handleClustering )

	def setKT(self,event=None):
		#sets translation interaction constant to current slider value
		self.kt = self.trans.get()

	def setKR(self,event=None):
		#sets rotation interaction constant to current slider value
		self.kr = self.rot.get()

	def setKS(self,event=None):
		#sets scaling interaction constant to current slider value
		self.ks = self.scale.get()

	def xzPlane(self,event=None):
		#puts the view into the xz plane
		self.view.vpn = np.matrix( [0,1,0], dtype=float)
		self.view.vup = np.matrix( [-1,0,0], dtype=float)
		self.view.u = np.matrix( [0,0,1], dtype=float)
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def xyPlane(self,event=None):
		#puts the view into the xy plane
		self.view.vpn = np.matrix( [0,0,-1], dtype=float)
		self.view.vup = np.matrix( [0,1,0], dtype=float)
		self.view.u = np.matrix( [1,0,0], dtype=float)
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def yzPlane(self,event=None):
		#puts the view into the yz plane
		self.view.vpn = np.matrix( [-1,0,0], dtype=float)
		self.view.vup = np.matrix( [0,1,0], dtype=float)
		self.view.u = np.matrix( [0,0,-1], dtype=float)
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def handleQuit(self, event=None):
		#ends program and closes window
		print 'Terminating'
		self.root.destroy()

	def handleClustering( self, event=None):
		#allows user to select data and number of clusters to plot, then plots clusters
		#calculated by kmeans clustering
		if self.data == None:
			self.handleOpen()

		if self.pca:
			self.clusterData = self.plotPCA
		else:
			self.clusterData = self.data
		self.clearAxes()

		clusters = SelectClusterHeaders( self.root, self.clusterData, 'Select Cluster Headers' )
		headers = clusters.result[0]
		k = clusters.result[1]
		color = clusters.result[2]

		if color == 'Discrete':
			self.clusterColors = True

		#calculate clusters with kmeans
		codebook,codes,error = a.kmeans_numpy( self.clusterData, headers, k )

		#assign codes to self.clusterIDX list
		self.clusterIDX = codes

		#choose axes to plot
		axes = self.chooseClusterPlots()

		#draw clusters
		self.buildClusters( axes, k )

	def chooseClusterPlots( self ):
		#returns a list of the headers for the axes to plot
		axes = SelectClusterAxes(self.root, self.clusterData, 'Select Axes')
		headers = [ axes.result['x'], axes.result['y'], axes.result['z'],
					axes.result['size'] ]
		self.headers = headers[:]
		#set z, colors, and sizes variables
		if axes.result['z'] != 'None':
			self.zAxis = True
		if axes.result['size'] != 'None':
			self.sizes = True
		#remove axes whose value is 'None'
		x = 0
		for i in range( len(self.headers) ):
			if self.headers[i] == 'None':
				x += 1
		for j in range(x):
			self.headers.remove('None')
		return self.headers

	def buildClusters( self, headers, k ):
		#draws the data points in colored clusters
		self.clearData()

		self.points = a.normalize_columns_separately(headers,self.clusterData)

		#create column of ones for homogeneous coordinates
		ones = []
		for i in range( self.data.get_raw_num_rows() ):
			ones.append( 1 )
		ones = np.matrix( ones ).T

		#z data values
		if self.zAxis:
			end = self.points[0:,3:]
			self.points = self.points[0:,0:3]
		else:
			end = self.points[0:,2:]
			self.points = self.points[0:,0:2]

		#sizes
		if self.sizes:
			sizes = end
			print 'sizes'

		#add column of zeros if only 2 axes selected
		#create column of zeros
		zeros = []
		for i in range( self.data.get_raw_num_rows() ):
			zeros.append( 0 )
		zeros = np.matrix( zeros ).T
		if self.points.shape[1] == 2:
			self.points = np.hstack( [self.points, zeros] )

		#add column of ones to matrix
		self.points = np.hstack( [self.points, ones] )

		#transform data
		vtm = self.view.build()
		pts = (vtm * self.points.T).T

		colors = [ 'red','blue','green','yellow', 'cyan', 'black', 'blue violet', 'pink', 'lavender', 'brown' ]

		if k > 10 :
			for i in range( k-10 ):
				r = random.randint(0,255)
				g = random.randint(0,255)
				b = random.randint(0,255)
				colors.append( (r,g,b) )

		normcIDX = self.clusterIDX/float( max( self.clusterIDX ) )

		#create data points
		for i in range( self.clusterData.get_raw_num_rows() ):
			if self.sizes:
				self.r.append( ( 5 * math.sqrt(sizes[i,0]) ) + 1 )
				r = self.r[i]
			else:
				r = 2
			if self.clusterColors:
				color = colors[ self.clusterIDX[i] ]
			else:
				red = 255 * normcIDX[i]
				g = 255 * normcIDX[i]
				b = 255 * (1-normcIDX[i])
				color = "#%02X%02X%02X" % (int(red), int(g), int(b))
			x = pts[i,0]
			y = pts[i,1]
			pt = self.canvas.create_oval( x+r, y+r, x-r, y-r, fill=color, outline='' )
			self.objects.append(pt)
		self.clearLinReg()
		self.updateFits()
		return

	def handlePCA(self, event=None):
		if self.data == None:
			self.handleOpen()
		pca = SelectPCA( self.root, self.data, self.pcad, 'Select PCA' ).result
		self.pcad = pca['pcad']
		if pca['plotPCA'] != None:
			self.plotPCA = pca['plotPCA']
			self.clearAxes()
			axes = self.choosePCAAxes()
			self.buildPCAPoints( axes )

	def choosePCAAxes(self):
		#returns a list of the headers for the axes
		axes = SelectPCAAxes(self.root, self.plotPCA, 'Select Axes')
		headers = [ axes.result['x'], axes.result['y'], axes.result['z'],
					axes.result['color'], axes.result['size'] ]
		self.headers = headers[:]
		#set colors, and sizes variables
		if axes.result['color'] != 'None':
			self.colors = True
		if axes.result['size'] != 'None':
			self.sizes = True
		#remove axes whose value is 'None'
		x = 0
		for i in range( len(self.headers) ):
			if self.headers[i] == 'None':
				x += 1
		for j in range(x):
			self.headers.remove('None')
		return self.headers

	def buildPCAPoints(self,axes):
		self.clearData()
		self.pca = True

		points = a.normalize_columns_separately( self.plotPCA.get_headers(),self.plotPCA )

		self.points = points[0:,0:len(axes)]

		#create column of ones for homogeneous coordinates
		ones = []
		for i in range( self.plotPCA.get_raw_num_rows() ):
			ones.append( 1 )
		ones = np.matrix( ones ).T

		#z data values
		end = self.points[0:,3:]
		self.points = self.points[0:,0:3]

		#colors and sizes
		if self.colors and self.sizes:
			colors = end[0:,0]
			sizes = end[0:,1]
			print 'colors and sizes'
		elif self.colors:
			colors = end
			print 'colors'
		elif self.sizes:
			sizes = end
			print 'sizes'

		#set values of colors (gradient from blue to yellow)
		if self.colors:
			c = []
			for i in range( self.plotPCA.get_raw_num_rows() ):
				r = 255 * colors[i,0]
				g = 255 * colors[i,0]
				b = 255 * (1-colors[i,0])
				s = "#%02X%02X%02X" % (int(r), int(g), int(b))
				c.append(s)

		#add column of ones to matrix
		self.points = np.hstack( [self.points, ones] )

		#transform data
		vtm = self.view.build()
		pts = (vtm * self.points.T).T

		#create data points
		for i in range( self.plotPCA.get_raw_num_rows() ):
			if self.colors:
				color = c[i]
			else:
				color = 'black'
			if self.sizes:
				self.r.append( ( 5 * math.sqrt(sizes[i,0]) ) + 1 )
				r = self.r[i]
			else:
				r = 2
			x = pts[i,0]
			y = pts[i,1]
			pt = self.canvas.create_oval( x+r, y+r, x-r, y-r, fill=color, outline='' )
			self.objects.append(pt)
		self.clearLinReg()
		self.updateFits()

	def handleMouseButton1(self, event):
		#stores where the mouse button 1 was clicked
		self.baseClick = (event.x, event.y)

	def handleMouseButton1Motion(self, event):
		#translates the data around the screen when mouse button 1 is clicked & dragged
		# calculate the differential motion
		diff = ( event.x - self.baseClick[0], event.y - self.baseClick[1] )
		self.baseClick = (event.x, event.y)
		#calculate new vrp
		dx = diff[0]/self.view.screen[0]
		dy = diff[1]/self.view.screen[1]

		delta0 = self.kt * dx * self.view.extent[0]
		delta1 = self.kt * dy * self.view.extent[1]

		self.view.vrp += (delta0*self.view.u) + (delta1*self.view.vup)
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def handleMouseButton2(self, event):
		#stores the click position and original View
		self.baseClick2 = (event.x, event.y)
		self.origView = self.view.clone()

	def handleMouseButton2Motion(self, event):
		#rotates the axes when the right mouse button is clicked and dragged
		diff = ( event.x - self.baseClick2[0], event.y - self.baseClick2[1] )

		delta0 = self.kr * math.pi * diff[0]/200
		delta1 = self.kr * math.pi * diff[1]/200

		self.view = self.view.clone()
		self.view.rotateVRC( delta0,delta1 )

		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def handleMouseButton3(self, event):
		#stores the mouse button 3 click location and original extents
		self.baseClick = (event.x, event.y)
		self.origExtent = self.view.clone().extent

	def handleMouseButton3Motion(self, event):
		#scales the data as mouse is moved vertically while button 3 is held
		#convert distance to scale factor
		dy = 1 + self.ks*(event.y - self.baseClick[1])/self.view.screen[1]
		scale = max( min(3.0,dy),0.1 )

		#apply scale factor
		self.view.extent = ( scale*self.origExtent[0], scale*self.origExtent[1], scale*self.origExtent[2] )
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def reset(self,event=None):
		#resets the view to the original view
		self.view.reset()
		self.updateAxes()
		self.updatePoints()
		self.updateFits()

	def saveClusters( self ):
		'''Saves a data file with a column of cluster categories at the end
		'''
		if self.clusterData != None:
			filename = EnterFileName(self.root, 'Cluster Filename' )
			a.saveClusters( self.clusterData, self.clusterIDX, filename.result )

	def clearLinReg(self):
		#resets fields for linReg data to their default values
		if self.linReg != []:
			for l in self.linReg:
				self.canvas.delete(l)
		self.linReg = []

		if self.linRegEq != []:
			for l in self.linRegEq:
				self.canvas.delete(l)
		self.linRegEq = []

		self.linRegEnds = None
		self.slope = None
		self.intercept = None
		self.rval = None
		self.pval = None
		self.stderr = None
		self.ranges = None

	def saveLinReg(self,event=None):
		#saves the current linear regression data to a txt file
		if self.linReg == []:
			tkMessageBox.showwarning( 'Failed to Save',
				'There is no linear regression data to save. Press \xE2\x8C\x98-L to run a linear regression' )
			return
		f = EnterFileName( self.root,'Enter File Name' )
		filename = f.result + '.txt'
		file = open( filename, 'w' )
		string = 'Independent Variable: ' + str(self.ind) + \
			   '\nDependent Variable: ' + str(self.dep) + \
			   '\nSlope: ' + str(round( self.slope,3 )) + \
			   '\nIntercept: ' + str(round( self.intercept,3 )) + \
			   '\nR-Squared: ' + str(round( self.rval*self.rval, 3 )) + \
			   '\nStandard Error: ' + str(round( self.stderr,3 )) + \
			   '\nX minimum , maximum: ' + str(self.ranges[0][0]) + ' , ' + str(self.ranges[0][1]) + \
			   '\nY minimum , maximum: ' + str(self.ranges[1][0]) + ' , ' + str(self.ranges[1][1])
		file.write( string )

	def handleLinearRegression(self,event=None):
		#creates linear regression line from variables specified by user in dialog box
		if self.data == None:
			self.handleOpen()
		vars = SelectVariables(self.root, self.data, 'Select Variables')
		self.clearData()
		self.clearAxes()
		self.clearLinReg()
		self.reset()
		self.updateAxes()
		self.buildLinearRegression( vars.result )

	def buildLinearRegression(self,vars):
		#creates matrix of data points
		self.ind = vars[0]
		self.dep = vars[1]
		self.points = a.normalize_columns_separately(vars,self.data)
		zeros = np.matrix( np.zeros( (self.data.get_raw_num_rows(), 1) ), dtype = float )
		ones = np.matrix( np.ones( (self.data.get_raw_num_rows(), 1) ), dtype = float )
		self.points = np.hstack( [self.points,zeros,ones] )

		#transforms data
		vtm = self.view.build()
		pts = (vtm * self.points.T).T

		#draws 2D plot
		for i in range( self.data.get_raw_num_rows() ):
			x = pts[i,0]
			y = pts[i,1]
			pt = self.canvas.create_oval( x+1, y+1, x-1, y-1, fill='black', outline='' )
			self.objects.append(pt)

		#stores regression data
		d = self.data.get_data( vars )
		x = d[0:,0:1].T.tolist()[0]
		y = d[0:,1:2].T.tolist()[0]
		self.slope, self.intercept, self.rval, self.pval, self.stderr = \
			scipy.stats.linregress( x,y )
		self.ranges = a.data_range( vars, self.data )

		#determines endpoints
		xmin = self.ranges[0][0]
		xmax = self.ranges[0][1]
		ymin = self.ranges[1][0]
		ymax = self.ranges[1][1]

		#normalize end points here
		x1 = 0.0
		x2 = 1.0
		y1 = ( ( xmin * self.slope + self.intercept ) - ymin )/( ymax - ymin )
		y2 = ( ( xmax * self.slope + self.intercept ) - ymin )/( ymax - ymin )

		self.linRegEnds = np.matrix( [ [x1,y1,0.0,1.0],
									   [x2,y2,0.0,1.0] ] )

		#multiply endpoints by vtm
		ends = (vtm * self.linRegEnds.T).T

		#draw line
		line = self.canvas.create_line( ends[0,0], ends[0,1], ends[1,0], ends[1,1],
										fill = 'red' )
		self.linReg.append( line )

		#display slope, intercept, and rval
		eqString = 'y = ' + str( round(self.slope,3) ) + 'x + ' + str( round(self.intercept,3) )
		eqString += '\nR^2: ' + str( round(self.rval*self.rval,3) )
		eq = self.canvas.create_text( 3*len(eqString), self.initDy-20, text=eqString,
										fill = 'red' )
		self.linRegEq.append( eq )

	def updateFits(self):
		#updates the linReg line on the canvas
		if self.linRegEnds == None:
			return
		vtm = self.view.build()
		ends = ( vtm * self.linRegEnds.T ).T
		for l in self.linReg:
			self.canvas.coords(l, ends[0,0], ends[0,1], ends[1,0], ends[1,1] )

	def handleMultLinReg(self,event=None):
		if self.data == None:
			self.handleOpen()
		self.clearAxes()
		self.reset()
		self.updateAxes()
		vars = SelectMultiVars( self.root, self.data, 'Select Variables' )
		ind = vars.independent
		dep = vars.dependent
		if len(ind) > 1:
			self.zAxis = dep[0]
		headers = ind + dep
		self.buildPoints(headers)
		self.displayMultLinReg(ind,dep)

	def displayMultLinReg(self,ind,dep):
		#display b, sse, r^2, t, and p vals in window
		linReg = a.linear_regression( self.data, ind, dep[0] )
		eqString = ''
		b = linReg['b']
		for i in range( len(b) - 1 ):
			eqString += 'm' + str(i) + ': ' + str( round(float(b[i]),3) ) + ' , '
		eqString += ' b: ' + str( round(float(b[-1]),3) ) + ' , sse: ' + \
			str(round(float(linReg['sse']),3))

		tvals = []
		for t in linReg['t'].tolist()[0]:
			tvals.append( round(float(t),3) )
		pvals = []
		for p in linReg['p']:
			pvals.append( round(float(p),3) )

		eqString += '\nR-Squared: ' + str( round(linReg['r2'],3) ) + ' , t: ' + \
			str( tvals ) + ' , p: ' + str( pvals )

		eq = self.canvas.create_text( 3*len(eqString), self.initDy-20, text=eqString,
										fill = 'red' )
		self.linRegEq.append( eq )

	def clearAxes(self):
		#resets all fields for plotting different dimensions
		self.zAxis = False
		self.colors = False
		self.sizes = False
		self.clusterColors = False
		self.pca = False
		self.categories = False
		self.r = []
		self.headers = []
		if self.axisLabels != []:
			for l in self.axisLabels:
				l.destroy()
			self.axisLabels = []

	def handleOpen(self,event=None):
		#opens and reads the file selected in the file dialog
		self.circadian = False
		fn = tkFileDialog.askopenfilename( parent=self.root, title='Choose a data file',
										   initialdir='.' )
		self.data = d.Data( fn )
		if fn[-18:] =='circadian_data.csv':
			self.circadian = True

	def handlePlotData(self):
		#plots data based on user's axes selections
		if self.data == None:
			self.handleOpen()
		self.clearAxes()
		axes = self.handleChooseAxes()
		self.buildPoints( axes )

	def handleChooseAxes(self):
		#returns a list of the headers for the axes
		axes = SelectAxes(self.root, self.data, 'Select Axes')
		headers = [ axes.result['x'], axes.result['y'], axes.result['z'],
					axes.result['color'], axes.result['size'] ]
		self.axisLabels = headers
		self.headers = headers[:]
		#set z, colors, and sizes variables
		if axes.result['z'] != 'None':
			self.zAxis = True
		if axes.result['color'] != 'None':
			self.colors = True
		if axes.result['size'] != 'None':
			self.sizes = True
		#remove axes whose value is 'None'
		x = 0
		for i in range( len(self.headers) ):
			if self.headers[i] == 'None':
				x += 1
		for j in range(x):
			self.headers.remove('None')
		self.addAxisStats()
		self.addAxisLabels()
		return self.headers

	def buildPoints(self, headers ):
		#creates and draws the data points from the data in the given column headers
		self.clearData()
		#normalize data
		self.points = a.normalize_columns_separately(headers,self.data)

		#create column of ones for homogeneous coordinates
		ones = []
		for i in range( self.data.get_raw_num_rows() ):
			ones.append( 1 )
		ones = np.matrix( ones ).T

		#z data values
		if self.zAxis:
			end = self.points[0:,3:]
			self.points = self.points[0:,0:3]
		else:
			end = self.points[0:,2:]
			self.points = self.points[0:,0:2]

		#colors and sizes
		if self.colors and self.sizes:
			colors = end[0:,0]
			sizes = end[0:,1]
			print 'colors and sizes'
		elif self.colors:
			colors = end
			print 'colors'
		elif self.sizes:
			sizes = end
			print 'sizes'

		#check if the data has been classified into categories
		if 'Categories' in self.data.get_raw_headers():
			self.categories = True
		if self.categories:
			self.colors = False
			c = []
			unique, map = np.unique( self.data.get_data( ['Categories'] ).T.tolist()[0], return_inverse=True )
			print 'unique clustuers: ' , len(unique)
			for i in range(len(unique)):
				r = random.randint(0,255)
				g = random.randint(0,255)
				b = random.randint(0,255)
				color = "#%02X%02X%02X" % (r, g, b)
				c.append( color )

		#set values of colors (gradient from blue to yellow)
		if self.colors:
			c = []
			for i in range( self.data.get_raw_num_rows() ):
				r = 255 * colors[i,0]
				g = 255 * colors[i,0]
				b = 255 * (1-colors[i,0])
				s = "#%02X%02X%02X" % (int(r), int(g), int(b))
				c.append(s)

		#add column of zeros if only 2 axes selected
		#create column of zeros
		zeros = []
		for i in range( self.data.get_raw_num_rows() ):
			zeros.append( 0 )
		zeros = np.matrix( zeros ).T
		if self.points.shape[1] == 2:
			self.points = np.hstack( [self.points, zeros] )

		#add column of ones to matrix
		self.points = np.hstack( [self.points, ones] )

		#transform data
		vtm = self.view.build()
		pts = (vtm * self.points.T).T

		#create data points
		for i in range( self.data.get_raw_num_rows() ):
			if self.colors:
				color = c[i]
			elif self.categories:
				color = c[ map[i] ]
			else:
				color = 'black'
			if self.sizes:
				self.r.append( ( 5 * math.sqrt(sizes[i,0]) ) + 1 )
				r = self.r[i]
			else:
				r = 2
			x = pts[i,0]
			y = pts[i,1]
			pt = self.canvas.create_oval( x+r, y+r, x-r, y-r, fill=color, outline='' )
			self.objects.append(pt)
		self.clearLinReg()
		self.updateFits()

	def updatePoints(self):
		#updates all the data points
		if len( self.objects ) == 0:
			return
		vtm = self.view.build()
		pts = (vtm * self.points.T).T
		for i in range( len(self.objects) ):
			if self.sizes:
				r = self.r[i]
			else:
				r = 2
			x = pts[i,0]
			y = pts[i,1]
			self.canvas.coords( self.objects[i], x+r, y+r, x-r, y-r )

	def clearData( self, event=None ):
		#Clears all the data points on the canvas
		for obj in self.objects:
			self.canvas.delete(obj)
		self.objects = []

	def main(self):
		#runs the data point creation application
		print 'Entering main loop'
		self.root.mainloop()

class Dialog(tk.Toplevel):
	#outline class for a dialog box

	def __init__(self, parent, title = None):
		#creates dialog box object

		tk.Toplevel.__init__(self, parent)
		self.transient(parent)

		if title:
			self.title(title)

		self.parent = parent
		self.result = None

		body = tk.Frame(self)
		self.initial_focus = self.body(body)
		body.pack(padx=5, pady=5)

		self.buttonbox()

		self.grab_set()

		if not self.initial_focus:
			self.initial_focus = self

		self.protocol("WM_DELETE_WINDOW", self.cancel)

		self.geometry("+%d+%d" % (parent.winfo_rootx()+50,
								  parent.winfo_rooty()+50))

		self.initial_focus.focus_set()

		self.wait_window(self)

	# construction hooks
	def body(self, master):
		# create dialog body.  return widget that should have
		# initial focus.  this method should be overridden
		pass

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default='active')
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	# standard button semantics
	def ok(self, event=None):
		#specifies what happens when ok is clicked

		if not self.validate():
			self.initial_focus.focus_set() # put focus back
			return

		self.withdraw()
		self.update_idletasks()

		self.apply()

		self.cancel()

	def cancel(self, event=None):

		# put focus back to the parent window
		self.parent.focus_set()
		self.destroy()

	# command hooks
	def validate(self):
		#check data
		return 1 # override

	def apply(self):
		pass # override

class SelectPCA(Dialog):
	'''class that creates a dialog box where the user can select a PCA analysis to view,
	add, remove, save, or plot. '''

	def __init__(self, parent, d, pcad, title = None):
		#sets up dialog box
		self.data = d
		self.pcad = pcad
		self.parent = parent
		self.p = False
		Dialog.__init__(self,parent)

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose PCA") #instructions

		#creates ListBox to choose multiple headers
		self.options = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=8)

		#adds options to the ListBoxes
		for item in self.pcad.keys():
			self.options.insert('end',item)

		#adds the items to the grid
		label.pack()
		self.options.pack()

		if self.pcad == {}:
			self.add()

		#sets selection to first item
		self.options.selection_set(0)

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
		box = tk.Frame(self)

		w = tk.Button(box, text="Add", width=10, command=self.add)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Remove", width=10, command=self.remove)
		w.pack(side=tk.LEFT,padx=5,pady=5)
		w = tk.Button(box, text="Plot", width=10, command=self.plot)
		w.pack(side=tk.LEFT,padx=5,pady=5)
		w = tk.Button(box, text="View", width=10, command=self.view)
		w.pack(side=tk.LEFT,padx=5,pady=5)
		w = tk.Button(box, text="Save", width=10, command=self.save)
		w.pack(side=tk.LEFT,padx=5,pady=5)
		w = tk.Button(box, text="OK", width=10, command=self.ok, default='active')
		w.pack(side=tk.LEFT,padx=5,pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT,padx=5,pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def add(self):
		headers = SelectPCAHeaders(self.parent,self.data,'Select Column Headers').result
		newPCA = a.pca( self.data,headers )
		pcaName = EnterPCAName(self.parent,'Enter PCA Name').result
		self.pcad[ pcaName ] = newPCA
		self.options.insert( 'end',pcaName )

	def remove(self):
		#removes the selected item from the listbox
		remItem = self.options.get( self.options.curselection() )
		self.pcad.pop(remItem)
		self.options.delete(0,'end')
		for item in self.pcad:
			self.options.insert('end',item)

	def plot(self):
		#sets the plot field to True, and then closes the Dialog box
		self.p = True
		self.ok()

	def view(self):
		#displays the values of the selected PCA
		curPCA = self.options.get( self.options.curselection() )
		ViewPCA( self.parent, self.pcad[curPCA], curPCA )

	def save(self):
		#saves the selected PCA to a .csv file of the specified name
		curPCA = self.options.get( self.options.curselection() )
		pcaName = EnterFileName(self.parent,'Enter File Name').result
		self.pcad[curPCA].write( pcaName )

	def apply(self):
		#assigns a dictionary of the new pcad list and the currently selected pca to
		#self.result
		if self.p == True:
			pca = self.options.get( self.options.curselection() )
			plotPCA = self.pcad[pca]
		else:
			plotPCA = None
		self.result = {'pcad':self.pcad,'plotPCA':plotPCA}

class ViewPCA(Dialog):
	'''class that creates a dialog box where the user can view information of the selected
	PCA analysis '''

	def __init__(self, parent, pca, title = None):
		#sets up dialog box
		self.pca = pca
		Dialog.__init__(self,parent)

	def body(self,master):
		#displays all the PCA information in the dialog box
		total = 0
		sum = 0
		for i in range( self.pca.get_eigenvalues().size ):
			total += self.pca.get_eigenvalues()[0,i]

		for i in range( self.pca.get_eigenvectors().shape[0] + 1 ):
			for j in range( len(self.pca.get_data_headers()) + 3 ):
				if i == 0:
					if j == 0:
						string = 'E-vec'
					elif j == 1:
						string = 'E-val'
					elif j == 2:
						string = 'Cummulative'
					else:
						string = self.pca.get_data_headers()[j-3]
				else:
					if j == 0: #E-vec labels column
						string = self.pca.get_raw_headers()[i-1]
					elif j == 1: #E-val column
						string = str( round(self.pca.get_eigenvalues()[0,i-1],4) )
					elif j == 2: #cumulative column
						sum += self.pca.get_eigenvalues()[0,i-1]
						string = str( round( (sum/total),4 ) )
					else: #data columns
						string = str( round( self.pca.get_eigenvectors()[i-1,j-3],4) )
				label = tk.Label( master, text=string )
				label.grid(row=i,column=j)

class SelectPCAHeaders(Dialog):
	'''class that creates a dialog box where the user can specify column headers to
	be used in PCA analysis '''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.headers = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose columns to use for PCA") #instructions

		#creates ListBox to choose multiple headers
		self.headers = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0, height=8)

		#adds options to the ListBoxes
		for item in self.data.get_headers():
			self.headers.insert('end',item)

		#sets selection to first item
		self.headers.selection_set(0)

		#adds the items to the grid
		label.pack()
		self.headers.pack()

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default='active')
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Select All", width=10, command=self.select)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)

		box.pack()

	def select(self):
		#selects all options in the listbox
		self.headers.selection_set(0, len( self.data.get_headers() )-1 )

	def apply(self):
		#assign axes variables to the ListBox selections
		headIdx = self.headers.curselection()

		#assigns a list of headers to self.result
		self.result = []
		for h in headIdx:
			self.result.append( self.headers.get( h ) )

class SelectClusterHeaders(Dialog):
	'''class that creates a dialog box where the user can specify column headers to
	be used in cluster analysis and number of clusters'''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.headers = None
		self.k = None
		self.color = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose column headers to use for clustering") #instructions
		labelc = tk.Label(master, text="Cluster Colors: ")

		#creates ListBox to choose multiple headers
		self.headers = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0, height=8)

		#adds options to the ListBoxes
		for item in self.data.get_headers():
			self.headers.insert('end',item)

		#sets selection to first item
		self.headers.selection_set(0)

		#adds the items to the grid
		label.pack()
		self.headers.pack()

		label = tk.Label(master, text="Choose number of clusters") #instructions
		label.pack()
		maxK = len( self.data.get_headers() )
		self.k = tk.Scale( master, from_ = 1, to = maxK,
								orient=tk.HORIZONTAL,
								length = 225, resolution = 1 )
		self.k.pack()
		self.k.set(1)

		labelc.pack()

		self.color = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=2)
		for item in ['Discrete','Blue/Yellow Gradient']:
			self.color.insert( 'end', item )

		self.color.pack()
		self.color.selection_set(0)

	def buttonbox(self):
		# add standard button box. override if you don't want the
		# standard buttons
		box = tk.Frame(self)

		w = tk.Button(box, text="OK", width=10, command=self.ok, default='active')
		w.pack(side=tk.LEFT, padx=5, pady=5)
		w = tk.Button(box, text="Cancel", width=10, command=self.cancel)
		w.pack(side=tk.LEFT, padx=5, pady=5)

		self.bind("<Return>", self.ok)
		self.bind("<Escape>", self.cancel)
		self.bind("<Button-2>", self.select)

		box.pack()

	def select(self, event):
		#selects all options in the listbox
		ends = self.headers.curselection()[-2:]
		self.headers.select_clear(0,len( self.data.get_headers() )-1 )
		self.headers.selection_set(ends[0], ends[1] )

	def apply(self):
		#assign axes variables to the ListBox selections
		headIdx = self.headers.curselection()
		k = self.k.get()
		#assigns a list of headers to self.result
		heads = []
		for h in headIdx:
			heads.append( self.headers.get( h ) )

		self.color = self.color.get( self.color.curselection()[0] )

		self.result = [heads,k,self.color]

class SelectClusterAxes(Dialog):
	'''class that creates a dialog box where the user can specify data to plot on x,y,z,
	and size axes'''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.x = None
		self.y = None
		self.z = None
		self.size = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose Axes") #instructions
		labelx = tk.Label(master, text="x: ")
		labely = tk.Label(master, text="y: ")
		labelz = tk.Label(master, text="z: ")
		sz = tk.Label(master, text="Size: ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelx.grid(row=1,sticky='W')
		labely.grid(row=2,sticky='W')
		labelz.grid(row=3,sticky='W')
		sz.grid(row=4,sticky='W')

		#creates ListBoxes for the x, y, z, color, and size axes
		self.x = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.z = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.size = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)

		#adds 'None' as first option in the z and size lists
		for item in [self.z, self.size]:
			item.insert('end','None')

		#adds options to all the ListBoxes
		for item in self.data.get_headers():
			self.x.insert('end',item)
			self.y.insert('end',item)
			self.z.insert('end',item)
			self.size.insert( 'end', item )

		#adds the ListBoxes to the grid
		self.x.grid(row=1, column=1)
		self.y.grid(row=2, column=1)
		self.z.grid(row=3, column=1)
		self.size.grid(row=4, column=1)

		#sets default values to first
		for item in [self.x, self.y, self.z, self.size]:
			item.selection_set(0)

	def apply(self):
		#assign axes variables to the ListBox selections
		self.x = self.x.get( self.x.curselection()[0] )
		self.y = self.y.get( self.y.curselection()[0] )
		self.z = self.z.get( self.z.curselection()[0] )
		self.size = self.size.get( self.size.curselection()[0] )

		#assigns a dictionary of the axes to self.result
		self.result = { 'x':self.x,'y':self.y, 'z':self.z, 'size':self.size }

class SelectPCAAxes(Dialog):
	'''class that creates a dialog box where the user can specify x, y, z, shape, and color
	axes to be plotted'''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.x = None
		self.y = None
		self.z = None
		self.color = None
		self.size = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose Axes") #instructions
		labelx = tk.Label(master, text="x: ")
		labely = tk.Label(master, text="y: ")
		labelz = tk.Label(master, text="z: ")
		col = tk.Label(master, text="Color: ")
		sz = tk.Label(master, text="Size: ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelx.grid(row=1,sticky='W')
		labely.grid(row=2,sticky='W')
		labelz.grid(row=3,sticky='W')
		col.grid(row=4,sticky='W')
		sz.grid(row=5,sticky='W')

		#creates ListBoxes for the x, y, z, color, and size axes
		self.x = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.z = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.color = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.size = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)

		#adds 'None' as first option in the z, color, and size lists
		for item in [self.color, self.size]:
			item.insert('end','None')

		#adds options to all the ListBoxes
		for item in self.data.raw_headers:
			self.x.insert('end',item)
			self.y.insert('end',item)
			self.z.insert('end',item)
			self.color.insert( 'end', item )
			self.size.insert( 'end', item )

		#adds the ListBoxes to the grid
		self.x.grid(row=1, column=1)
		self.y.grid(row=2, column=1)
		self.z.grid(row=3, column=1)
		self.color.grid(row=4, column=1)
		self.size.grid(row=5, column=1)

		#sets default values to first
		for item in [self.x, self.color, self.size]:
			item.selection_set(0)
		self.y.selection_set(1)
		self.z.selection_set(2)

	def apply(self):
		#assign axes variables to the ListBox selections
		self.x = self.x.get( self.x.curselection()[0] )
		self.y = self.y.get( self.y.curselection()[0] )
		self.z = self.z.get( self.z.curselection()[0] )
		self.color = self.color.get( self.color.curselection()[0] )
		self.size = self.size.get( self.size.curselection()[0] )

		#assigns a dictionary of the axes to self.result
		self.result = { 'x':self.x,'y':self.y, 'z':self.z, 'color':self.color, 'size':self.size }

class EnterPCAName(Dialog):
	'''class that creates a dialog box where the user can specify the name of the PCA
	Analysis that it can be found as. '''

	def __init__(self, parent, title = None):
		#sets up dialog box
		Dialog.__init__(self,parent)
		self.name = None
		self.v = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Type your desired PCA analysis name.") #instructions
		labelName = tk.Label(master, text="Analysis name: ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelName.grid(row=1,sticky='W')

		#creates input textbox
		self.v = tk.StringVar()
		self.name = tk.Entry(master, textvariable = self.v)

		#adds the Entry textbox to the grid
		self.name.grid(row=1, column=1)

		self.v.set( 'TypeAnalysisNameHere' )

	def apply(self):
		#assigns a dictionary of the axes to self.result
		self.result = self.v.get()

class EnterFileName(Dialog):
	'''class that creates a dialog box where the user can specify the name of the text
	file that the linear regression data will be saved to. '''

	def __init__(self, parent, title = None):
		#sets up dialog box
		Dialog.__init__(self,parent)
		self.name = None
		self.v = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Type your desired output file name.") #instructions
		labelName = tk.Label(master, text="Output file name: ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelName.grid(row=1,sticky='W')

		#creates input textbox
		self.v = tk.StringVar()
		self.name = tk.Entry(master, textvariable = self.v)

		#adds the Entry textbox to the grid
		self.name.grid(row=1, column=1)

		self.v.set( 'TypeFileNameHere' )

	def apply(self):
		#assigns a dictionary of the axes to self.result
		self.result = self.v.get()

class SelectMultiVars(Dialog):
	'''class that creates a dialog box where the user can specify independent and dependent
	variables to find the linear regression data for. '''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.vars = None
		self.dep = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose Independent Variables") #instructions
		dep = tk.Label(master, text="Choose Dependent Variable")

		#creates ListBoxe to choose multiple variables
		self.vars = tk.Listbox(master, selectmode=tk.MULTIPLE, exportselection=0, height=8)
		self.dep = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=8)

		#adds options to the ListBoxes
		for item in self.data.get_headers():
			self.vars.insert('end',item)
			self.dep.insert('end',item)

		#adds the items to the grid
		label.pack()
		self.vars.pack()
		dep.pack()
		self.dep.pack()

		#sets default values to first elements
		self.vars.selection_set(0)
		self.dep.selection_set(0)

	def apply(self):
		#assign axes variables to the ListBox selections
		varsIdx = self.vars.curselection()

		#assigns a dictionary of the axes to self.result
		self.independent = []
		for h in varsIdx:
			self.independent.append( self.vars.get( h ) )
		self.dependent = [self.dep.get( self.dep.curselection()[0] )]

class SelectVariables(Dialog):
	'''class that creates a dialog box where the user can specify x, y ,z color, and
	size axes to plot. '''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.x = None
		self.y = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose Variables") #instructions
		labelx = tk.Label(master, text="Independent (x): ")
		labely = tk.Label(master, text="Dependent (y): ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelx.grid(row=1,sticky='W')
		labely.grid(row=2,sticky='W')

		#creates ListBoxes for the x, y, z, color, and size axes
		self.x = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=5)
		self.y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=5)

		#adds options to all the ListBoxes
		for item in self.data.get_headers():
			self.x.insert('end',item)
			self.y.insert('end',item)

		#adds the ListBoxes to the grid
		self.x.grid(row=1, column=1)
		self.y.grid(row=2, column=1)

		#sets default values to first element
		self.x.selection_set(0)
		self.y.selection_set(0)

	def apply(self):
		#assign axes variables to the ListBox selections
		self.x = self.x.get( self.x.curselection()[0] )
		self.y = self.y.get( self.y.curselection()[0] )

		#assigns a dictionary of the axes to self.result
		self.result = [ self.x, self.y ]

class SelectAxes(Dialog):
	'''class that creates a dialog box where the user can specify x and y random
	distributions, number of data points to be drawn, and shape of the data points'''

	def __init__(self, parent, d, title = None):
		#sets up dialog box
		self.data = d
		Dialog.__init__(self,parent)
		self.x = None
		self.y = None
		self.z = None
		self.color = None
		self.size = None

	def body(self,master):
		#creates all the elements of the dialog box
		label = tk.Label(master, text="Choose Axes") #instructions
		labelx = tk.Label(master, text="x: ")
		labely = tk.Label(master, text="y: ")
		labelz = tk.Label(master, text="z: ")
		col = tk.Label(master, text="Color: ")
		sz = tk.Label(master, text="Size: ")

		#adds labels to grid
		label.grid(row=0,columnspan=2, sticky='W')
		labelx.grid(row=1,sticky='W')
		labely.grid(row=2,sticky='W')
		labelz.grid(row=3,sticky='W')
		col.grid(row=4,sticky='W')
		sz.grid(row=5,sticky='W')

		#creates ListBoxes for the x, y, z, color, and size axes
		self.x = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.y = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.z = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.color = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)
		self.size = tk.Listbox(master, selectmode=tk.SINGLE, exportselection=0, height=4)

		#adds 'None' as first option in the z, color, and size lists
		for item in [self.z, self.color, self.size]:
			item.insert('end','None')

		#adds options to all the ListBoxes
		for item in self.data.get_headers():
			self.x.insert('end',item)
			self.y.insert('end',item)
			self.z.insert('end',item)
			self.color.insert( 'end', item )
			self.size.insert( 'end', item )

		#adds the ListBoxes to the grid
		self.x.grid(row=1, column=1)
		self.y.grid(row=2, column=1)
		self.z.grid(row=3, column=1)
		self.color.grid(row=4, column=1)
		self.size.grid(row=5, column=1)

		#sets default values to first
		for item in [self.x, self.y, self.z, self.color, self.size]:
			item.selection_set(0)

	def apply(self):
		#assign axes variables to the ListBox selections
		self.x = self.x.get( self.x.curselection()[0] )
		self.y = self.y.get( self.y.curselection()[0] )
		self.z = self.z.get( self.z.curselection()[0] )
		self.color = self.color.get( self.color.curselection()[0] )
		self.size = self.size.get( self.size.curselection()[0] )

		#assigns a dictionary of the axes to self.result
		self.result = { 'x':self.x,'y':self.y, 'z':self.z, 'color':self.color, 'size':self.size }

if __name__ == "__main__":
	dapp = DisplayApp(1200, 675)
	dapp.main()
