import socket
import os, imp, struct, threading, csv
from bluetooth import *
import bluetooth, signal, sys
from enum import Enum
from cobs import cobs

HOST = '127.0.0.1'  # The server's hostname or IP address
PORT = 65432        # The port used by the server

dir_path = os.path.dirname(os.path.realpath(__file__))

imuMsgPath = dir_path+ "/release/imumsg_pb2.py"

imuMsg = imp.load_source("imumsg_pb2",imuMsgPath)

#Class defines mode of data transfer
class dataTransferMode(Enum):

	TCP = 1
	BLUETOOTH = 2

class commonBTAdress(Enum):
	
	RASPBERRYBTADDR = "B8:27:EB:6B:15:7F"
	HC05LeftTeensy = "98:D3:51:FD:AD:F5"
	HC05RIGHT = "98:D3:81:FD:48:C9"


#####Primary class used to communicate data over bt.
class msgServer(threading.Thread):
	connected = False
	#If true choose blueTooth connection
	blueTooth = False
	_maxClients = 1
	_numClients = 0
	_serverRunning = True
	def __init__(self, dataTransferMode, clientAddress):
		threading.Thread.__init__(self)

		print("Binding to port")
		self.transferMode = dataTransferMode
		self.btAdress = clientAddress

	def run(self):
		#self.startServer()
		if(self.transferMode == dataTransferMode.TCP):
			self.startTCPServer()
		elif(self.transferMode == dataTransferMode.BLUETOOTH):
			self.startServerBlueTooth()

	
	def startTCPServer(self):
			print("Binding to port")
			#create an INET, STREAMing socket
			self.serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
			#bind the socket to a public host,
			# and a well-known port
			print("Binding to port")
			self.serversocket.bind((HOST, PORT))
			print("Succesfully connected to a client")


			self.controlLoop()


			#while True:
			
	#Ran after connection is made
	def controlLoop(self):
		_thread = IMUMsgThread(self.clientsocket,self)
		_thread.start()		

		
	
	def getLeftIMUData(self):
		return self._HC05LeftDataThread.getLatestStoredIMUData()
	

	@property
	def numClients(self):
		return self._numClients

	def removeClient(self):
		##For now just lower number clients connected
		self._numClients = self._numClients - 1
	
	def startServerBlueTooth(self):

		while self._serverRunning:
			
			if self._numClients < self._maxClients:

				self.connectToHC05Left()
				pass

	def shutDown(self):
		self._serverRunning = False
		sys.exit(0)
	def getIMUMsg(self):
	 
		dataSizeArray = self.receive(4)

		dataSize = struct.unpack("<L", dataSizeArray)[0]
		print(dataSize)

		data = self.receive(dataSize)		
		#Get incoming data.
		_imuMsg = imuMsg.IMUInfo()				
		_imuMsg.ParseFromString(data)
		print("Value: %f" %_imuMsg.acc_x)
		print("Msg from sensor " + _imuMsg.sensorID)

		

	def receive(self, MSGLEN):
		chunks = []
		bytes_recd = 0
		while bytes_recd < MSGLEN:
			chunk = self.clientsocket.recv(1)
			chunks.append(chunk)
			bytes_recd = bytes_recd + len(chunk)
		return ''.join(chunks)	

	def connectToHC05Left(self):
		sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
		sock.connect((self.btAdress,1))
		print("Connected to Socket")
		self._numClients = self._numClients + 1
		#~ while 1:
			#~ s = sock.recv(1)
			#~ print(s)
		self._HC05LeftDataThread = IMUMsgThread(sock,self)
		self._HC05LeftDataThread.start()			
		#~ input("Press enter to close")
		#~ sock.close()

class IMUMsgThread(threading.Thread):
	#Thread is running
	_running = True
	#Whether to store incoming data in a CSV file.
	_recordData=False

	def __init__(self, clientSocket, parentServer):
		threading.Thread.__init__(self)
		self.clientsocket = clientSocket
		self._parentServer = parentServer
		

	def run(self):
		self.csvFile = open(dir_path+"/data.csv", 'wb')
		self.CSVData = csv.writer(self.csvFile)		
		self.COBSIntialClear()
		while self._running: 
			# try:
			# 	# self._currentIMUData = self.getIMUMsg()
			# 	self.receiveCOBSMessage()
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

		
		# #Cobs MEssage
		# msg = []
		# byte = self.receive(1)
		# #Once we have read a zero the every thing else is a message, until next zero is hit.
		# while ord( byte ) != 0:
		# 	msg.append( byte ) 
		# 	byte = self.receive(1)
		# # self.getIMUMsg()
		# self.decodeCOBS(''.join(msg))

		# MAX = 1000
		# chunks = []
		# bytes_recd = 0
		# #Overflow safety
		# while bytes_recd < MAX:
		# 	print("Waiting for msg")
		# 	chunk = self.clientsocket.recv(1)

		# 	print(chunk[0])
		# 	print(ord(chunk))
		# 	if chunk == '':

		# 		#raise RuntimeError("socket connection broken")
		# 		print("socket connection broken shutting down this thread")
		# 		self.shutDown()
		# 		return 0


		# 	if ord(chunk) == 0:
		# 			break
		# 	chunks.append(chunk)
		# 	bytes_recd = bytes_recd + len(chunk)

		# data = []
		while True:
			data = []
			c = self.clientsocket.recv(1)
			print("Running")
			if c == b'':
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
		


	def readBuffer(self):
		return self.clientsocket.recv(1)

	def decodeCOBS(self,encodedCobsMsg):
		print(len(encodedCobsMsg))
		msg = cobs.decode(encodedCobsMsg)
		dataSizeArray = msg[:4]
		dataSize = struct.unpack("<L", dataSizeArray)[0]
		print(len(msg))			
		print(dataSize)			
		data = msg[4:]
		print("Data Size " + str(len(data)))
		# for d in data:
		# 	print(ord(d))
		#Get incoming data.
		_imuMsg = imuMsg.IMUInfo()				
		_imuMsg.ParseFromString(data)
		print("Value: %f" %_imuMsg.acc_x)
		print("Data from sensor "+ _imuMsg.sensorID)


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
		self.csvFile.close()
		self._running = False
		self._parentServer.removeClient()


def connect():
	sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
	sock.connect((commonBTAdress.HC05RIGHT,1))
	print("Connected to Socket")
	input("Press enter to close")
	sock.close()

def findBT():

	targetname
if __name__=="__main__":
	
	print("Binding to port")
	# connect()
	_msgServerThread = msgServer(dataTransferMode.BLUETOOTH, commonBTAdress.HC05LeftTeensy)
	_msgServerThread.start()

	#signal.signal(signal.SIGINT, _msgServerThread.shutDown)
	#signal.pause()
	# while True:
	# 	if _msgServer.connected:
	# 		_msgServer.getIMUMsg()
