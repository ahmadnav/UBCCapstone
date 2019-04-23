
import threading
from cobs import cobs
import time

class dataHandler(object):
	def __init__(self):
		pass

	def onRecieveData(self, data):
		#This function needs to be set at run time by instantiating class
		self.dataCallBack.dataHandler(data)

class socketHandler( threading.Thread):

	#Thread is running
	_running = True
	#Whether to store incoming data in a CSV file.
	_recordData=False

	_isConnected = False
	#callbackHanlder must have an implemented dataHandler
	def __init__(self, clientSocket, parentServer, callBackHandler):
		threading.Thread.__init__(self)
		self.clientsocket = clientSocket
		self._parentServer = parentServer

		print("In socket handler")
		self.dataCallBack = dataHandler()
		#Set the call back
		self.dataCallBack = callBackHandler
		

	def run(self):
		# self.csvFile = open(dir_path+"/data.csv", 'wb')
		# self.CSVData = csv.writer(self.csvFile)		
		self.COBSIntialClear()
		while self._running: 
			# try:
			# 	# self._currentIMUData = self.getIMUMsg()
				# self.receiveCOBSMessage()
			# except:
			# 	print("ERROR getting message")
			# 	pass	

			self.receiveCOBSMessage()			
			

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
		# time.sleep(0.01)


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