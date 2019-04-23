import imp
import os, time
#import imumsg_pb2.py
import socket,struct
from bluetooth import *
import bluetooth
from dataTransferServer import commonBTAdress
from socketHandler import *

dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "\\release\\imumsg_pb2.py"
print(imuMsgPath)
imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

HOST = '127.0.0.1'  # Standard loopback interface address (localhost)
PORT = 65432        # Port to listen on (non-privileged ports are > 1023)

bluetoothHost = 1
bluetoothPort = 2

class dataTransferClient(threading.Thread):

	isConnected = False
	#1 BlueTooth 
	def __init__(self, BTAdress, dataHandler):
		threading.Thread.__init__(self)
		#self.startClientWifi()
		# self.startClientBlueTooth()
		self.serverAddress = BTAdress
		self._dataHandler = dataHandler

	def run(self):
		self.sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		while True:
			if not self.isConnected:
				self.connect()
			time.sleep(2)

	def connect(self):
		try:
			self.sock.connect((self.serverAddress,1))
			print("Connected to Socket")
			self.isConnected = True


			self._HC05LeftDataThread = socketHandler(self.sock,self, self._dataHandler)
			self._HC05LeftDataThread.start()			
		except Exception as e:	
			print("Server Not Avail")


	def onSocketShutdown(self):
		self.isConnected = False

	#Ran after connection is made
	def controlLoop(self):
		self.sendMsg(msg)
		pass


	def sendMsg(self, msg):

		msgLen = len(msg)

		#Send the length of message. I denote max of 4 bytes or unsigned int32
		msgLenArray = struct.pack("I", msgLen)

		for byte in msgLenArray:
			print("Sending")
			print(byte)
			self._client.send(byte)

		totalSent=0
		while totalSent <  msgLen:
			#Sent will always be one (as a byte is sent)
			sent = self._client.send(msg[totalSent])
			totalSent = sent + totalSent

		

class sensorMsgGenerator():
	def __init__(self):
		pass

	def getMsg():
		_imuMsg = imuMsg.IMUInfo()
		_imuMsg.acc_x=float(2.0)
		_imuMsg.acc_y=float(3.524)
		print("Value: %f" %_imuMsg.acc_x)
		print("Value: %f" %_imuMsg.acc_y)
		#len(s.encode('utf-8'))
		binaryMsg = _imuMsg.SerializeToString()
		length  = len( binaryMsg )	
		return binaryMsg

# if __name__=="__main__":
# 	#client = TCPClient()
# 	# i = 0
# 	# while i < 10:
# 	# 	client.sendMsg(getMsg())
# 	# 	i = i + 1
# 	btLookUp()
	
# 	#name = raw_input("What is your name? ")