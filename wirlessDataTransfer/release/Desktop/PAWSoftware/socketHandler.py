
import threading
from cobs import cobs
import imp
import os, time 
#import imumsg_pb2.py
import socket,struct, threading
from bluetooth import *
import bluetooth
from mainSensorAcquisition import *

class dataHandler(object):
	def __init__(self):
		pass

	def onRecieveData(self, data):
		#This function needs to be set at run time by instantiating class
		self.dataCallBack.dataHandler(data)




dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "/release/imumsg_pb2.py"
print(imuMsgPath)
imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

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

class socketHandler( threading.Thread):

	#Thread is running
	_running = True
	#Whether to store incoming data in a CSV file.
	_recordData=False

	_isConnected = False

	_msgBuffer = []
	#callbackHanlder must have an implemented dataHandler
	def __init__(self, clientSocket, parentServer, callBackHandler):
		threading.Thread.__init__(self)
		self.clientsocket = clientSocket
		self._parentServer = parentServer

		print("In socket handler")
		self.dataCallBack = dataHandler()
		#Set the call back
		self.dataCallBack = callBackHandler
		
		self._mainSensorAcquisition = mainSensorAcquisition()
		
		self._mainSensorAcquisition.start()
		

	def run(self):
		self.controlLoop()		
			

	#Ran after connection is made
	def controlLoop(self):
		while(True):
			#self.addMsgToBuffer(getMsg())
			print("Buffer Length " + str( len(self._msgBuffer)))
			self.addMsgToBuffer( self._mainSensorAcquisition.getSensorData() )
			self.sendMsgToClient() 
			time.sleep(0.1)

	def sendMsg(self, msg):

		msgLen = len(msg)

		#Send the length of message. I denotes max of 4 bytes or unsigned int32
		msgLenArray = struct.pack("I", msgLen)

		_msg = msgLenArray + msg
		self.sendCobsMessage(_msg)
		
	def addMsgToBuffer(self, msg):
		self._msgBuffer.append(msg)
	
	def sendMsgToClient(self):
		
		if( len(self._msgBuffer) > 0):
			print("Message Buffer Size: %i" %(len(self._msgBuffer)))
			msg = self._msgBuffer[0]
			del self._msgBuffer[0]
			self.sendMsg(msg)
		else:
			pass

	def sendCobsMessage(self, msg):
		encodedmsg = cobs.encode(msg)

		msgLen = len(encodedmsg)
		
		totalSent=0
		while totalSent <  msgLen:
			#Sent will always be one (as a byte is sent)
			print(encodedmsg[totalSent])
			print("Sending message of length " + str(msgLen))
			sent = self.clientsocket.send(encodedmsg[totalSent])
			totalSent = sent + totalSent

		self.clientsocket.send(struct.pack(">I", 0))

 
	def getLatestStoredIMUData(self):

		return self._currentIMUData

	def COBSIntialClear(self):
		byte = self.receive(1)
		#Keep looping while byte recieved is not 0, i.e. the end/start of a cobs message.
		while ord(byte) != 0:
			#Keep looping while not 0
			byte = self.receive(1)
			print("Not 0")
			#Clear out potential initial garbage
			pass
	#Recieves COBS encoded Message.
	def receiveCOBSMessage(self):

		while True:
			data = []
			c = self.clientsocket.recv(1)
			# print("Running")
			if c == b'':
				self.onDisconnect()
				break
			while c != b'\x00' and c != b'':
				data.append(c)
				c = self.clientsocket.recv(1)
			data = b''.join(data)
			#printSensor(cobs.decode(data))
			# self.decodeCOBS(data) 
			try:
				self.decodeCOBS(data) 	
			except Exception as e:
				print("Failed to decode message")
		
			
	def onDisconnect(self):
		print("Disconnected from server")
		self.shutDown()

	def readBuffer(self):
		return self.clientsocket.recv(1)

	def decodeCOBS(self,encodedCobsMsg):
		# print("Encoded message length "+ str(len(encodedCobsMsg)))
		msg = cobs.decode(encodedCobsMsg)
		self.dataCallBack.onRecieveData(msg)


	def getIMUMsg(self):
	 #
		dataSizeArray = self.receive(4)
		

		dataSize = struct.unpack("<L", dataSizeArray)[0]
		print(dataSize)
		if dataSize > 100:
			print("data corruption")
			return
		data = self.receive(dataSize)	
		

		#Get incoming data.
		_imuMsg = imuMsg.IMUInfo()				
		_imuMsg.ParseFromString(data)
		print("Value: %f" %_imuMsg.acc_x)
		print("Data from sensor "+ _imuMsg.sensorID)
		if self._recordData:
			self.CSVData.writerow([_imuMsg.acc_x])
		return _imuMsg
		

	###
	def receive(self, MSGLEN):
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			print("Waiting for msg")
			chunk = self.clientsocket.recv(1)
			print(chunk[0])
			print(ord(chunk))
			if chunk == '':

				#raise RuntimeError("socket connection broken")
				print("socket connection broken shutting down this thread")
				self.shutDown()
				return 0


			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		return ''.join(chunks)	

	def shutDown(self):
		self.clientsocket.close()
		# self.csvFile.close()
		self._running = False
		self._parentServer.onSocketShutdown()


# if __name__ == "__main__":
# 	_p = socketHandler(None, None, None)
