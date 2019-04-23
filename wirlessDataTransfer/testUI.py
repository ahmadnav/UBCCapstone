# Import libraries
import numpy as np
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import time, os
import csv
from remotePAWDataAcquisition import *

dir_path = os.path.dirname(os.path.realpath(__file__))

### START QtApp #####
app = QtGui.QApplication([])            # you MUST do this once (initialize things)
####################



def displayStoredData():
	rightIMUDataFilePath  =  dir_path + "\\rightIMUMessage.csv"
	leftIMUDataFilePath = dir_path + "\\leftIMUMessage.csv"

	rightxData = []
	rightyData = []
	rightzData = []
	rightxgyro = []
	rightygyro = []
	rightzgyro = []


	leftxData = []
	leftyData = []
	leftzData = []
	leftxgyro = []
	leftygyro = []
	leftzgyro = []

	maxLen = 1200
	with open(rightIMUDataFilePath, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			k = 0
			for row in reader:
				#print(row['first_name'], row['last_name']) 			
				# print(row)
				if len(row) > 4 and k < maxLen:
					rightxData.append(row[0])
					rightyData.append(row[1])
					rightzData.append(row[2])
					rightygyro.append(row[3])
					rightzgyro.append(row[4])
					k = k + 1

	with open(leftIMUDataFilePath, 'rb') as csvfile:
			reader = csv.reader(csvfile, delimiter=',')
			k = 0
			for row in reader:
				#print(row['first_name'], row['last_name']) 			
				if len(row) > 4 and k < maxLen:
					leftxData.append(row[0])
					leftyData.append(row[1])
					leftzData.append(row[2])
					leftygyro.append(row[3])
					leftzgyro.append(row[4])
					k=k+1


	i = 0
	_max = 100
	while i < _max:
		# self._plotter.updateRightSensorData(np.array(rightxData[0:i], dtype=float), np.array(rightyData[0:i], dtype=float), np.array(rightzData[0:i], dtype=float))
		update(np.array(rightxData[0:i], dtype=float))
		i = i +1
		time.sleep(0.1)





import pyqtgraph as pg
import numpy as np
import threading 
from pyqtgraph.Qt import QtGui, QtCore

# app = QtGui.QApplication([])


class pyQtGrapher:

	leftxData = []
	leftyData = []
	leftzgyroData = []



	rightxData = []
	rightyData = []
	rightzgyroData = []

	maxListSize = 500

	def __init__(self):
		
		self.ready = False	
		self.avail=True
		self.run()
		return

	def run(self):
		self.setupGraph("IMUData")


	def setupGraph(self, title):


		self.win = pg.GraphicsWindow(title=title)
		self.win.resize(1000,600)
		self.win.setWindowTitle('PAW Data')

		# Enable antialiasing for prettier plots
		pg.setConfigOptions(antialias=True)


		self.p1 = self.win.addPlot(title="Right x accel")
		self.rightaccXPlot = self.p1.plot(pen=(255,0,0))

		self.p2 = self.win.addPlot(title="Right y accel")
		self.rightaccYPlot = self.p2.plot(pen=(255,0,0))

		self.p3 = self.win.addPlot(title="Right z angular")
		self.rightangZPlot = self.p3.plot(pen=(255,0,0))		


		self.win.nextRow()

		self.p4 = self.win.addPlot(title="Left x accel")
		self.leftaccXPlot = self.p4.plot(pen=(0,255,0))

		self.p5 = self.win.addPlot(title="Left y accel")
		self.leftaccYPlot = self.p5.plot(pen=(0,255,0))

		self.p6 = self.win.addPlot(title="Left z angular")
		self.leftangZPlot = self.p6.plot(pen=(0,255,0))		



		self.ready = True

	def rightHC05PlotXAxis(self,acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, color):
		# self.verifyDataSize()
		# self.p1.plot(xData, pen=(255,0,0))

		if self.ready:# and self.avail:
			self.avail = False
				
			print("displaying right data")	
			# self.rightaccXPlot.setData(self.rightxData)
			# self.rightaccYPlot.setData(self.rightyData)
			# self.rightangZPlot.setData(self.rightzgyroData)

			self.rightaccXPlot.setData(acc_x)
			self.rightaccYPlot.setData(acc_y)
			self.rightangZPlot.setData(gyr_z)

			QtGui.QApplication.processEvents()    
			self.avail = True
			return True
		else:
			return False

	def leftHC05PlotXAxis(self,acc_x, acc_y, acc_z, gyr_x, gyr_y, gyr_z, color):
		# self.verifyDataSize()
		# self.p1.plot(xData, pen=(255,0,0))
		if self.ready:# and self.avail:
			self.avail = False

			# self.leftaccXPlot.setData(self.leftxData)
			# self.leftaccYPlot.setData(self.leftyData)
			# self.leftangZPlot.setData(self.leftzgyroData)
			
			self.leftaccXPlot.setData(acc_x)
			self.leftaccYPlot.setData(acc_y)
			self.leftangZPlot.setData(gyr_z)

			QtGui.QApplication.processEvents()    

			self.avail = True
			return True
		else:
			return False

	def verifyDataSize(self):
		self.truncateData(self.rightxData)
		self.truncateData(self.rightyData)
		self.truncateData(self.rightzgyroData)
		
		self.truncateData(self.leftxData)
		self.truncateData(self.leftyData)
		self.truncateData(self.leftzgyroData)
	def truncateData(self, data):

		if len(data) > self.maxListSize:
			data.pop(0)		

	def displayStoredData(self):
		print("displaying displayStoredData")

		rightIMUDataFilePath  =  dir_path + "\\rightIMUMessage.csv"
		leftIMUDataFilePath = dir_path + "\\leftIMUMessage.csv"

		rightxData = []
		rightyData = []
		rightzData = []
		rightxgyro = []
		rightygyro = []
		rightzgyro = []


		leftxData = []
		leftyData = []
		leftzData = []
		leftxgyro = []
		leftygyro = []
		leftzgyro = []

		maxLen = 500
		with open(rightIMUDataFilePath, 'rb') as csvfile:
				reader = csv.reader(csvfile, delimiter=',')
				k = 0
				for row in reader:
								
					# print(row)
					if len(row) > 4 and k < maxLen:

						rightxData.append(row[0])
						rightyData.append(row[1])
						rightzData.append(row[2])
						rightygyro.append(row[3])
						rightzgyro.append(row[4])
						k = k + 1

		with open(leftIMUDataFilePath, 'rb') as csvfile:
				reader = csv.reader(csvfile, delimiter=',')
				k = 0

				for row in reader:
					
					# print(row)
					if len(row) > 4 and k < maxLen:
						# print(row)
						leftxData.append(row[0])
						leftyData.append(row[1])
						leftzData.append(row[2])
						leftygyro.append(row[3])
						leftzgyro.append(row[4])
						k=k+1

		# print(leftxData)
		# i = 0
		# _max = 1000
		# while i < _max:
		# 	# self._plotter.updateRightSensorData(np.array(rightxData[0:i], dtype=float), np.array(rightyData[0:i], dtype=float), np.array(rightzData[0:i], dtype=float))
		# 	self.rightHC05PlotXAxis(np.array(rightxData[0:i], dtype=float), np.array(rightyData[0:i], dtype=float), None, None, None, np.array(rightzgyro[0:i], dtype=float), None)
		# 	self.leftHC05PlotXAxis(np.array(leftxData[0:i], dtype=float), np.array(leftyData[0:i], dtype=float), None, None, None,  np.array(leftzgyro[0:i], dtype=float), None)
		# 	i = i +1
		# 	time.sleep(0.0001)

		# self.rightHC+5PlotXAxis(np.array(leftxData, dtype=float), np.array(leftyData, dtype=float), None, None, None,  np.array(leftzgyro, dtype=float), None)
		# print(rightxData)
		# while not self.ready:
		# 	print("Not ready")
		# 	pass
		self.rightHC05PlotXAxis(np.array(rightxData, dtype=float), np.array(rightyData, dtype=float), None, None, None, np.array(rightzgyro, dtype=float), None)
		self.leftHC05PlotXAxis(np.array(leftxData, dtype=float), np.array(leftyData, dtype=float), None, None, None,  np.array(leftzgyro, dtype=float), None)
### MAIN PROGRAM #####    
# this is a brutal infinite loop calling your realtime data plot
if __name__ == "__main__":
	# displayStoredData()
	grapher = pyQtGrapher()

	grapher.displayStoredData()
	# grapher.rightHC05PlotXAxis([1,2,3], [4,5,6], None, None, None,[7,8,9], None)
	# grapher.leftHC05PlotXAxis([3,2,1], [6,5,4], None, None, None,[9,8,7], None)
	# grapher.displayStoredData()
	# _remotePAWDataAcquisition  = remotePAWDataAcquisition(grapher)
	# _remotePAWDataAcquisition.start()

	### END QtApp ####
	pg.QtGui.QApplication.exec_() # you MUST put this at the end
	##################