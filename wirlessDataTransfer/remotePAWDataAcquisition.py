
from dataTransferClient import *
import numpy as np
import time
from enum import *
import csv, sys


#Import classes in UI folder
sys.path.insert(0, 'C:\\Users\\Ahmad\\OneDrive\\School\\Mech46x\\wirlessDataTransfer\\UI\\WheelSense_UI')
from pyqtGraph import pyQtGrapher
import pyqtgraph as pg

dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "\\release\\imumsg_pb2.py"
print(imuMsgPath)
imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

class HC05Sensors(Enum):
	Right=1
	Left=2


class dataCallBackClass:
	xData = []
	yData = []
	zData = []

	leftxData = []

	xGyro = []
	yGyro = []
	zGyro = []

	maxListSize = 1000

	rightIMUDataFilePath  =  dir_path + "\\rightIMUMessage.csv"
	leftIMUDataFilePath = dir_path + "\\leftIMUMessage.csv"

	#Parent lass (caller, and the sensor type)
	def __init__(self, _parent=None, sensorType=None):
		self.parentUI = _parent

		self._sensorType= sensorType
		
		rightIMU = open(self.rightIMUDataFilePath, mode='w') 
		leftIMU = open(self.leftIMUDataFilePath, mode='w') 
		self.rightIMUCSV = csv.writer(rightIMU)
		self.leftIMUCSV = csv.writer(leftIMU)

		# self.storeData()
		# self.displayData()
		

	def onRecieveData(self, msg):



		dataSizeArray = msg[:4]
		dataSize = struct.unpack("<L", dataSizeArray)[0]
		print(len(msg))			
		print(dataSize)			
		data = msg[4:]
		# print("Data Size " + str(len(data)))
		# for d in data:
		# 	print(ord(d))
		#Get incoming data.
		_imuMsg = imuMsg.IMUInfo()				
		_imuMsg.ParseFromString(data)

		print("Value In onRecieveData: %f" %_imuMsg.acc_x)
		print("Value: %f" %_imuMsg.acc_y)
		print("Data from sensor "+ _imuMsg.sensorID)

		# self.xData.append(2)
		# print(self.xData)
		# self.verifyDataSize()

		self._acc_x =_imuMsg.acc_x 
		self._acc_y =_imuMsg.acc_y 
		self._acc_z =_imuMsg.acc_z 

		self._angular_x = _imuMsg.angular_x
		self._angular_y = _imuMsg.angular_y
		self._angular_z = _imuMsg.angular_z

		

		# self.xData.append(_imuMsg.acc_x )
		# self.yData.append(_imuMsg.acc_y )
		# self.zData.append(_imuMsg.acc_z )
		# print("Plotting Data of length onRecieveData " + str(len(self.yData)))
		# self.xGyro.append(_imuMsg.angular_x)
		# self.yGyro.append(_imuMsg.angular_y)
		# self.zGyro.append(_imuMsg.angular_z)
		
		self.storeData()	

	def verifyDataSize(self):
		self.truncateData(self.xData)
		self.truncateData(self.yData)
		self.truncateData(self.zData)
		
		self.truncateData(self.xGyro)
		self.truncateData(self.yGyro)
		self.truncateData(self.zGyro)
	def truncateData(self, data):

		if len(data) > self.maxListSize:
			data.pop(0)		
	

	def plotStoredData(self):
		pass

	def storeData(self):

		if self._sensorType == "right":
			self.rightIMUCSV.writerow([self._acc_x, self._acc_y, self._acc_z, self._angular_x, self._angular_y, self._angular_z])
			# self.rightIMUCSV.writerow([4, 3, 2, None, None, 1])
			self.parentUI.rightxData.append(self._acc_x)
			self.parentUI.rightyData.append(self._acc_y)
			self.parentUI.rightzgyroData.append(self._angular_z)
		elif self._sensorType == "left":
			
			self.leftIMUCSV.writerow([self._acc_x, self._acc_y, self._acc_z, self._angular_x, self._angular_y, self._angular_z])
			# self.leftIMUCSV.writerow([1, 2, 2, None, None, 3])
			self.parentUI.leftxData.append(self._acc_x)
			self.parentUI.leftyData.append(self._acc_y)
			self.parentUI.leftzgyroData.append(self._angular_z)
			

class remotePAWDataAcquisition(threading.Thread):

	def __init__(self, _parent):
		threading.Thread.__init__(self)
		self.parent= _parent

		
		# self.d
		pass

	def run(self):

		# self.displayStoredData()

		self.RightHC05CallBackClass = dataCallBackClass(self.parent, "right")#HC05Sensors.Right)
		# self._dataClientThread = dataTransferClient("B8:27:EB:A3:ED:6F", d)
		self._dataClientThreadRight = dataTransferClient(commonBTAdress.HC05RIGHT, self.RightHC05CallBackClass)
		self._dataClientThreadRight.start()

		self.LeftHC05CallBackClass = dataCallBackClass(self.parent, "left")#HC05Sensors.Left)
		self._dataClientThreadLeft = dataTransferClient(commonBTAdress.HC05LeftTeensy, self.LeftHC05CallBackClass)
		self._dataClientThreadLeft.start()
		

		self.controlLoop()

		
 
 	def controlLoop(self):

 		while True:
 			self.displayData("right")
 			self.displayData("left")
 			# self.parent.displayStoredData()
 			time.sleep(0.5)	


	def displayData(self,  sensorType):

		if "right" == sensorType:
			self.parent.rightHC05PlotXAxis(self.RightHC05CallBackClass.xData, self.RightHC05CallBackClass.yData, self.RightHC05CallBackClass.zData, self.RightHC05CallBackClass.xGyro, self.
				RightHC05CallBackClass.yGyro, self.RightHC05CallBackClass.zGyro,'r-')

			# self.parent.rightHC05PlotXAxis([1,2,3,4,5,6],[1,2,3,4,5,6],None,None,None,[1,2,3,4,5,6],'r-')
			# self.parent.leftHC05PlotXAxis([6,5,4,3,2,1],[6,5,4,3,2,1], None, None, None, [6,5,4,3,2,1],'r-')	
			
		elif "left" == sensorType:
			self.parent.leftHC05PlotXAxis(self.LeftHC05CallBackClass.xData, self.LeftHC05CallBackClass.yData , self.LeftHC05CallBackClass.zData, self.LeftHC05CallBackClass.xGyro, 
				self.LeftHC05CallBackClass.yGyro, self.LeftHC05CallBackClass.zGyro,'b-')
			# # self.parent.leftHC05PlotXAxis([6,5,4,3,2,1],[6,5,4,3,2,1], None, None, None, [6,5,4,3,2,1],'r-')			
			# self.parent.rightHC05PlotXAxis([1,2,3,4,5,6],[1,2,3,4,5,6],None,None,None,[1,2,3,4,5,6],'r-')

 	def displayStoredData(self):
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
						rightygyro.append(row[4])
						rightzgyro.append(row[5])
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
						leftygyro.append(row[4])
						leftzgyro.append(row[5])
						k=k+1

# def plotData( data):
# 	x = np.linspace(0, len(data), len(data))
# 	y = data
# 	pg.plot(x, y, pen=None, symbol='o')

# if __name__ == "__main__":
	# _remotePAWDataAcquisition = remotePAWDataAcquisition(None)
	# _remotePAWDataAcquisition.start()
	 

	# d = dataCallBackClass()
	# _dataClientThread = dataTransferClient(commonBTAdress.HC05LeftTeensy, d)
	# _dataClientThread.start()