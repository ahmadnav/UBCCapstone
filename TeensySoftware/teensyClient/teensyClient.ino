#include <PacketSerial.h>

#include <MPU6050.h>

#include <pbSensorMsgGen.h>
#include <pb_decode.h>
#include <imumsg.pb.h>
#include <stddef.h>

//**** IMU DEFINATIONS ****//
// Pin definitions
int intPin = 12;  // This can be changed, 2 and 3 are the Arduinos ext int pins
int16_t accelCount[3];           // Stores the 16-bit signed accelerometer sensor output
float ax, ay, az;                // Stores the real accel value in g's
int16_t gyroCount[3];            // Stores the 16-bit signed gyro sensor output
float gx, gy, gz;                // Stores the real gyro value in degrees per seconds
float gyroBias[3], accelBias[3]; // Bias corrections for gyro and accelerometer
int16_t tempCount;               // Stores the internal chip temperature sensor output 
float temperature;               // Scaled temperature in degrees Celsius
float SelfTest[6];               // Gyro and accelerometer self-test sensor output
uint32_t count = 0;
float aRes, gRes; // scale resolutions per LSB for the sensors
MPU6050lib mpu;

//********//


#define bluetooth Serial1
/* Sending msg Buffer.*/
uint8_t msgBuffer[2000];
/* Recv message buffer.*/
uint8_t rcvmsgBuffer[2000];


String receivedText = "";
String cmd = "";
IMUInfo _msg = IMUInfo_init_zero;

pbSensorMsgGenerator pbMsgGenerator;
COBS cobs;

PacketSerial cobsBTSerial;//(0, nullptr,bluetooth, nullptr);
void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);

  IMUsetup();

//  bluetooth.begin(38400);
  bluetooth.begin(115200); //rx1 and tx1 = pins 0 and 1 on Teensy
  cobsBTSerial.begin(&bluetooth);
  
  delay(200);


}


void loop() {

    
//     bluetooth.write((byte)1); bluetooth.write((byte)0x00);
//    delay(1000);
    
//   while (Serial.available() > 0 ){
//    cmd+=(char)Serial.read();
//   }
//   if (cmd!=""){    
////      sendMsg();  
////      sendATCmd();
//      for (int i = 0;i < 100; i++){
//        controlLoop();
//        
//      }
//   }
//   
//   cmd = "";
// if(Serial.available() > 0 )  {
//  Serial.println("In Serial");
   controlLoop();
// }
//  
//  sendATCmd();
//rcvData();
}


void rcvData(){
  String receivedText = "";
  while(bluetooth.available() > 0) { // While there is more to be read, keep reading.
    receivedText += (char)bluetooth.read();
    delay(100);  
  } 
  if(receivedText != "") Serial.println(receivedText);
  receivedText = ""; 
   
}

void sendATCmd(){ 
   while (Serial.available() > 0 ){
    cmd+=(char)Serial.read();
   }
   if (cmd!=""){
    bluetooth.write("AT+" );
//    bluetooth.write(cmd.c_str());
    bluetooth.write("UART=115200,0,0");
//    bluetooth.write("UART?");
    bluetooth.write("\r\n"); 
    Serial.println("SendingMSG" );
    Serial.println(cmd);
   }
   
   cmd = "";
 
  while(bluetooth.available() > 0) { // While there is more to be read, keep reading.
    receivedText += (char)bluetooth.read();
    //delay(10);  
  } 
  if(receivedText != "") Serial.println(receivedText);
  receivedText = ""; 
}

void recieveMsg(){
  
  unsigned int msgLength;
  uint8_t _msgLenBuffer[4];
  if(bluetooth.available()){
    Serial.println("Recieving msgs");
    //Recieve length of message
    for(int i=0;i<4;i++){
      _msgLenBuffer[i] = bluetooth.read(); 
    } 

    msgLength = *(int *)_msgLenBuffer;

    uint8_t msg[msgLength];
    //Recieve length of message
    for(int i=0;i<msgLength;i++){
      
      msg[i] = bluetooth.read(); 
      
    }    

      /* Allocate space for the decoded message. */
      IMUInfo message = IMUInfo_init_zero;
      
      /* Create a stream that reads from the buffer. */
      pb_istream_t stream = pb_istream_from_buffer(msgBuffer, msgLength);
      
      /* Now we are ready to decode the message. */
      bool status = pb_decode(&stream, IMUInfo_fields, &message);
      
      /* Check for errors... */
      if (!status)
      {
          //printf("Decoding failed: %s\n", PB_GET_ERROR(&stream));
          
          return ;
      }
      Serial.println("Time Stamped Recieved");
      Serial.println(message.time_stamp);
    
  }
}

void sendMsg(uint8_t* msg, int msgLen){
  uint8_t _msgLenBuffer[4];

  _msgLenBuffer[3] = (msgLen >> 24) & 0xFF;
  _msgLenBuffer[2] = (msgLen >> 16) & 0xFF;
  _msgLenBuffer[1] = (msgLen >> 8) & 0xFF;
  _msgLenBuffer[0] = msgLen & 0xFF;
  Serial.print("Sending Message of length\n");
  Serial.println(msgLen );

  //Send length of message
  for(int i=0;i<4;i++){
    int sent = bluetooth.write((byte) _msgLenBuffer[i]); 
  } 
//  //Send Message
  for(int i=0;i<msgLen;i++){
//    Serial.print("Sebding MESSAGE BYTES\n");
    bluetooth.write(msg[i]);
  }
}

void sendMsgCobs(uint8_t* msg, int msgLen){
  uint8_t _msgLenBuffer[4+msgLen];

  _msgLenBuffer[3] = (msgLen >> 24) & 0xFF;
  _msgLenBuffer[2] = (msgLen >> 16) & 0xFF;
  _msgLenBuffer[1] = (msgLen >> 8) & 0xFF;
  _msgLenBuffer[0] = msgLen & 0xFF;
  Serial.print("Sending Message of length\n");
  Serial.println(msgLen );

  /* Append message to end of length*/
  for(int i = 0;i<msgLen;i++){
    _msgLenBuffer[4+i] = msg[i];
    Serial.println("Sending byte" );

    Serial.println((byte)msg[i]);
  }
    
    /* Convert message to COBS*/
    size_t cobsBufferLength = cobs.getEncodedBufferSize(msgLen+4);
    //Buffer to store cobs encoded message.
    uint8_t cobsBuffer[cobsBufferLength]; 
    size_t cobsMsgLength = cobs.encode(_msgLenBuffer, msgLen+4, cobsBuffer);

  cobsBTSerial.send(_msgLenBuffer, msgLen+4);
//  //Send Message
//  for(int i=0;i<cobsMsgLength+1;i++){
//    Serial.print("Sebding MESSAGE BYTES\n");
//   Serial.println((byte)cobsBuffer[i], BIN);
//   int sent =  bluetooth.write((byte)cobsBuffer[i]);
//  }
  
}



void IMUsetup()
{
  Wire.begin();
  
  // Set up the interrupt pin, its set as active high, push-pull
  pinMode(intPin, INPUT);
  digitalWrite(intPin, LOW);
  
  Serial.println("MPU6050");
  Serial.println("6-DOF 16-bit");
  Serial.println("motion sensor");
  Serial.println("60 ug LSB");
 
   // Read the WHO_AM_I register, this is a good test of communication
  uint8_t c = mpu.readByte(MPU6050_ADDRESS, WHO_AM_I_MPU6050);  // Read WHO_AM_I register for MPU-6050
  Serial.print("I AM ");
  Serial.print(c, HEX);  
  Serial.print(" I Should Be ");
  Serial.println(0x68, HEX); 

  if (c == 0x68) // WHO_AM_I should always be 0x68
  {  
    Serial.println("MPU6050 is online...");
    
    mpu.MPU6050SelfTest(SelfTest); // Start by performing self test and reporting values
    Serial.print("x-axis self test: acceleration trim within : "); Serial.print(SelfTest[0],1); Serial.println("% of factory value");
    Serial.print("y-axis self test: acceleration trim within : "); Serial.print(SelfTest[1],1); Serial.println("% of factory value");
    Serial.print("z-axis self test: acceleration trim within : "); Serial.print(SelfTest[2],1); Serial.println("% of factory value");
    Serial.print("x-axis self test: gyration trim within : "); Serial.print(SelfTest[3],1); Serial.println("% of factory value");
    Serial.print("y-axis self test: gyration trim within : "); Serial.print(SelfTest[4],1); Serial.println("% of factory value");
    Serial.print("z-axis self test: gyration trim within : "); Serial.print(SelfTest[5],1); Serial.println("% of factory value");

    if(SelfTest[0] < 1.0f && SelfTest[1] < 1.0f && SelfTest[2] < 1.0f && SelfTest[3] < 1.0f && SelfTest[4] < 1.0f && SelfTest[5] < 1.0f) {
    Serial.println("Pass Selftest!");  
      
    mpu.calibrateMPU6050(gyroBias, accelBias); // Calibrate gyro and accelerometers, load biases in bias registers  
    mpu.initMPU6050(); Serial.println("MPU6050 initialized for active data mode...."); // Initialize device for active mode read of acclerometer, gyroscope, and temperature

   }
   else
   {
    Serial.print("Could not connect to MPU6050: 0x");
    Serial.println(c, HEX);
    while(1) ; // Loop forever if communication doesn't happen
   }

  }
}

void controlLoop()
{  
  // If data ready bit set, all data registers have new data
  if(mpu.readByte(MPU6050_ADDRESS, INT_STATUS) & 0x01) {  // check if data ready interrupt

    mpu.readAccelData(accelCount);  // Read the x/y/z adc values
    aRes=mpu.getAres();
    
    // Now we'll calculate the accleration value into actual g's
    ax = (float)accelCount[0]*aRes ;//- accelBias[0];  // get actual g value, this depends on scale being set
    ay = (float)accelCount[1]*aRes ;//- accelBias[1];   
    az = (float)accelCount[2]*aRes ;//- accelBias[2];  
   
    mpu.readGyroData(gyroCount);  // Read the x/y/z adc values
    gRes=mpu.getGres();
 
    // Calculate the gyro value into actual degrees per second
    gx = (float)gyroCount[0]*gRes - gyroBias[0];  // get actual gyro value, this depends on scale being set
    gy = (float)gyroCount[1]*gRes - gyroBias[1];  
    gz = (float)gyroCount[2]*gRes - gyroBias[2];   

    tempCount = mpu.readTempData();  // Read the x/y/z adc values
    temperature = ((float) tempCount) / 340. + 36.53; // Temperature in degrees Centigrade
   }  
   
//    uint32_t deltat = millis() - count;
//    if(deltat > 500) {
// 
////    // Print acceleration values in milligs!
////    Serial.print("X-acceleration: "); Serial.print(1000*ax); Serial.print(" mg "); 
////    Serial.print("Y-acceleration: "); Serial.print(1000*ay); Serial.print(" mg "); 
////    Serial.print("Z-acceleration: "); Serial.print(1000*az); Serial.println(" mg"); 
//// 
////    // Print gyro values in degree/sec
////    Serial.print("X-gyro rate: "); Serial.print(gx, 1); Serial.print(" degrees/sec "); 
////    Serial.print("Y-gyro rate: "); Serial.print(gy, 1); Serial.print(" degrees/sec "); 
////    Serial.print("Z-gyro rate: "); Serial.print(gz, 1); Serial.println(" degrees/sec"); 
////    
////   // Print temperature in degrees Centigrade      
////    Serial.print("Temperature is ");  Serial.print(temperature, 2);  Serial.println(" degrees C"); // Print T values to tenths of s degree C
////    Serial.println("");
////        
//    count = millis();
//    }

    //*****Recieve Time Stamp*******//
    //recieveMsg();
    
    //*****SEND MESSAGE OVER BT*****//
    //Update the value of IMU sensor.
    pbMsgGenerator.addIMUData( ax,ay,az,gx,gy,gz);
    
    int lengthf = pbMsgGenerator.generatePBMessage();


    
//    sendMsg(pbMsgGenerator.getPBMessage(),lengthf);

 
    sendMsgCobs(pbMsgGenerator.getPBMessage(), lengthf);

    //delay(10);
}
