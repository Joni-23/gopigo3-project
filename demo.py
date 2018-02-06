import threading 
import time 
import socket 
from picamera.array import PiRGBArray 
import numpy as np 
import picamera 
import spybot 
import cv2
from mysql.connector import (connection)

class myThread (threading.Thread):
   def __init__(self, threadID, name):
      threading.Thread.__init__(self)
      self.threadID = threadID
      self.name = name
   def run(self):
      if(self.threadID == 1):
          server()
      elif(self.threadID == 2):
          servo()
      elif(self.threadID == 3):
          mysql()

resolution = (320,240)
cam = picamera.PiCamera()
cam.resolution  = resolution
cam.framerate = 16
rawCapture = PiRGBArray(cam, size=resolution)
USSR_spyBot = spybot.spyBot(resolution)

def mysql():
   try:
     # cnx = connection.MySQLConnection() mySQL connection settings
      cursor = cnx.cursor()
   except mysql.connector.Error as err:
     if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
       print("Something is wrong with your user name or password")
     elif err.errno == errorcode.ER_BAD_DB_ERROR:
       print("Database does not exist")
     else:
       print(err)
      
      
   while 1:
      time.sleep(1)
      direction = ""
      lMotor, rMotor = USSR_spyBot.getMotorVal()
      x,y = USSR_spyBot.getXY()
      if(lMotor == 0 and rMotor == 0): direction = "Still"
      elif(lMotor < rMotor):   direction = "Left"
      elif(lMotor > rMotor): direction = "Right"
      else: direction = "Forward"
         
      add_data = ("INSERT INTO motors" "(idArvo, left_motor, right_motor, suunta, Timestamp)" "VALUES(NULL, %s,%s, %s, NOW())")
      cursor.execute(add_data, (lMotor,rMotor,direction))
      cnx.commit()

def server():
    TCP_IP = '192.168.1.38'
    TCP_PORT = 5006
    BUFFER_SIZE = 20
    while 1:
       print ("Kuunteleee")
       s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
       s.bind((TCP_IP, TCP_PORT))
       s.listen(1)
       conn, addr = s.accept()

       print ('Connection incoming from address:', addr)
       USSR_spyBot.setRemoteControl(True)
       while USSR_spyBot.isRemoteControl:
          data = conn.recv(BUFFER_SIZE)
          if not data: break

          newData = chr(data[len(data)-1])
          print(newData)
       
          com = USSR_spyBot.remoteControl(newData)

def servo():
    servoPos = [2000,1800,1000,800]
    distVal = [0,0,0,0]
    while 1:
       while not USSR_spyBot.checkRoad():
          time.sleep(0.01)
                                 
       USSR_spyBot.lookOutObjects()
       USSR_spyBot.setRoad(False)
       if(USSR_spyBot.sweepArea()): 
          USSR_spyBot.setRoad(True)
       else: #Este edessa
          USSR_spyBot.setRoad(False)
          USSR_spyBot.setMotor(-25, 50)
          time.sleep(1)

def Car():
    for frame in cam.capture_continuous(rawCapture, format="bgr", use_video_port=True):
        image = np.asarray(frame.array)
 
        if(not USSR_spyBot.isRemoteControl()):

            mask, thres = USSR_spyBot.checkColor(image)
            x,y = USSR_spyBot.calXY(mask)
            pixels =  USSR_spyBot.getBitCount(mask)
            USSR_spyBot.lookTarget(image)
           # print("Target size: ", pixels)

            if(USSR_spyBot.checkPicture_Threshold()):
                USSR_spyBot.setMotor(0,0)
                print("Take picture")
                crop_image = USSR_spyBot.checkPicture(image)
                if(crop_image != None):
                   pic_action = USSR_spyBot.compare(crop_image)
                   USSR_spyBot.pictureAction(pic_action)

            if(USSR_spyBot.checkRoad()):    
                if(USSR_spyBot.checkColor_Threshold()):
                    cv2.circle(image,(x,y),5,(0,0,255),-1)
                    USSR_spyBot.followColor(x,y)
                else:
                    print("Looking target", pixels)
                    USSR_spyBot.searchColor()
            else: #Not clear Road
                print("Not Clear")
                USSR_spyBot.evadeObject()
        
        cv2.imwrite("/var/www/html/output.jpg",mask)
        #USSR_spyBot.saveCamera(image)
        rawCapture.truncate(0)


USSR_spyBot.setMotor(0,0)
USSR_spyBot.setServo(1400)
time.sleep(1)

thread1 = myThread(1, "TCP-Server")
thread2 = myThread(2, "Servo")
thread3 = myThread(3, "mysql")

thread1.start()
thread2.start()
thread3.start()

while 1:
    Car()

