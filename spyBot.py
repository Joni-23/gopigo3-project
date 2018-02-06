# -*- coding: utf-8 -*-

import numpy as np
from time import sleep
import time
import cv2
import gopigo3
import easygopigo3 as easy

import twitter 
from myTweets import returnTweet
from datetime import datetime

gpg = easy.EasyGoPiGo3()
mySensor = gpg.init_distance_sensor()
GPG = gopigo3.GoPiGo3()
#api settings
#api = twitter.Api();


SWEEP_TIME = 5
FRONT_OBJECT_THRESHOLD = 200
SIDE_OBJECT_THRESHOLD = 250	

BOARD_THRESHOLD_LOW = ([10,90,100])
BOARD_THRESHOLD_HIGH = ([64,155,155])


class spyBot:
    def __init__(self, resolution):
        self.sendTweet("")
        print("SpyBot actived")
        print("Battery lvl is: ", GPG.get_voltage_battery())
        self.__remoteControl = False
        self.__clearRoad = True
        self.__x = 0
        self.__y = 0
        self.__lMotorVal = 0
        self.__rMotorVal = 0
        self.__resolution = resolution
        self.__bitCount = 0
        self.__targetFound = False
        self.__motorSpeed = 100
        self.__color_Threshold = 20
        self.__picture_Threshold = 11000
        self.__images=[	'pictures/go_sign.jpg',
			'pictures/left_arrow.jpg',
			'pictures/right_arrow.jpg',
			'pictures/turn_around.jpg',
			'pictures/fire_extinguisher.jpg',
			'pictures/stop_sign.jpg']

############################################
############################################
####   Functions for camera usage       ####
############################################
############################################

    def getXY(self):
        return self.__x, self.__y

    def calXY(self, mask):
        bitCountMask = mask
        xy_cal = 1
        self.__bitCount =  np.transpose(np.nonzero(bitCountMask))

        if(len(self.__bitCount) > 500):
            xy_cal = int(len(self.__bitCount) / 250)

        if(self.__bitCount != None):
            x = 0
            y = 0
            for i in range(0,len(self.__bitCount), xy_cal):
                y = y + (self.__bitCount[i][0] / len(self.__bitCount))
                x = x + (self.__bitCount[i][1] / len(self.__bitCount))
            self.__y = int(y * xy_cal)
            self.__x = int(x * xy_cal)

            return self.__x,self.__y


    def checkPicture_Threshold(self, bitCount = None):
        if(bitCount == None):
            bitCount = self.__bitCount
            
        if(bitCount > self.__picture_Threshold):
            return True
        else:
            return False

    def checkColor_Threshold(self, bitCount = None):
        if(bitCount == None):
            bitCount = self.__bitCount

        if(bitCount > self.__color_Threshold):
            return True
        else:
            return False


    def getBitCount(self, mask):
        pixels = np.transpose(np.nonzero(mask))
        self.__bitCount = len(pixels)

        return self.__bitCount

    def checkColor(self, image,LOW = BOARD_THRESHOLD_LOW,UP = BOARD_THRESHOLD_HIGH):
        lower = np.array(LOW, dtype = "uint8")
        upper = np.array(UP, dtype = "uint8")

        kernel = np.ones((2,2),np.uint8)
        mask = cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
        mask = cv2.inRange(mask, lower, upper)

        bitwise_out = cv2.bitwise_and(image,image, mask = mask)

        return mask, bitwise_out


    def compare(self,image):
        imgA = cv2.resize(image, (100,100))
        imgA = cv2.cvtColor(imgA, cv2.COLOR_BGR2GRAY)
        ret, imgA = cv2.threshold(imgA,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

        output = "None"
        minVal = 500000
        for i in range(0, len(self.__images)):
            imgB = cv2.imread(self.__images[i])

            imgB = cv2.resize(imgB, (100,100))
            imgB = cv2.cvtColor(imgB, cv2.COLOR_BGR2GRAY)
            ret, imgB = cv2.threshold(imgB,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)

            compareResult = imgA ^ imgB

            threshold = cv2.countNonZero(compareResult)
            if(threshold < minVal):
                minVal = threshold
                output = self.__images[i][9:len(self.__images[i])-4]

        return output
    
    def canny(self, image):
        out = cv2.Canny(image,100,200)
        return out

    def checkPicture(self,image):
        edges = cv2.Canny(image,100,200)

        th, contours, hierarchy = cv2.findContours(edges,cv2.RETR_LIST,cv2.CHAIN_APPROX_NONE)
        contours = sorted(contours, key = cv2.contourArea, reverse = True)[:10]
        for c in contours:
            peri = cv2.arcLength(c, True)
            approx = cv2.approxPolyDP(c, 0.02 * peri, True)
            if(len(approx) == 4):
                x,y,w,h = cv2.boundingRect(approx)
                cv2.rectangle(image,(x,y),(x+w,y+h),(255,0,0),2)
                print("rectangle: ", x,y,w,h)
                if(w > 30 and w > 30):
                    if(h < w*1.2 and h > w*0.8):
                       # print("Printataa")
                        output = image[y:y+h, x:x+w]
                       # cv2.imwrite("/var/www/html/output1.jpg", output)
        
                        return output
        return image

    def saveCamera(self,image):
        font = cv2.FONT_HERSHEY_SIMPLEX
        if(self.isRemoteControl()):
            cv2.putText(image,'RemoteControl',(40,200), font, 1,(0,0,255),2,cv2.LINE_AA)
        else:
            cv2.putText(image,'Following Color',(30,200), font, 1,(0,0,0),2,cv2.LINE_AA)
        cv2.imwrite("/var/www/html/output.jpg",image)
    
############################################
############################################
###     Function for camera actions      ###
############################################
############################################

    def pictureAction(self, picture):
        if(picture == "left_arrow"):
            self.leftArrow()
        elif(picture == "right_arrow"):
            self.rightArrow()
        elif(picture == "go_sign"):
            self.goSign()
        elif(picture == "turn_around"):
            self.turnAround()
        elif(picture == "fire_extinguisher"):
            self.fireExtinguisher()
        elif(picture == "stop_sign"):
            self.stopSign()
        else:
            print("Paska")
        self.__targetFound = False

    def leftArrow(self):
        self.sendTweet("Found left arrow")
        print("Left ARROW Fucn")
        self.setMotor(-50,50)
        sleep(3)
        
    def rightArrow(self):
        self.sendTweet("Found right arrow")
        print("Rich Arrow func")
        self.setMotor(50,-50)
        sleep(3)
        
    def goSign(self):
        self.sendTweet("Found go sign")
        print("GoSign func")

    def turnAround(self):
        self.sendTweet("Turn around")
        print("Turn Around func")

    def fireExtinguisher(self):
        self.sendTweet("Found fireee")
        print("Fire func")

    def stopSign(self):
        self.sendTweet("Found stop")
        print("stop Func")
        exit(0)

############################################
############################################
###         Functions for Twitter        ###
############################################
############################################

    def sendTweet(self, msg):
        self.setMotor(0,0)
        curDate =  datetime.now().strftime('%H:%M:%S')
        quite = returnTweet()
        tweet = msg + " " + curDate + "\n" + quite
        status = api.PostUpdate(tweet)

############################################
############################################
###     Functions for remote control     ###
############################################
############################################

    def remoteControl(self, data):
        if data  == 'w':
            self.setMotor(300,300)
        elif data  == 's':
            self.setMotor(-300,-300)
        elif data  == 'a':
            self.setMotor(-100,100) 
        elif data  == 'd':
            self.setMotor(100,-100) 
        elif data  == 'f':
            self.setMotor(0,0)
        elif data  == 'e':
            self.setRemoteControl(not self.isRemoteControl())


    def isRemoteControl(self):
        return self.__remoteControl

    def setRemoteControl(self, status):
        self.__remoteControl = status


################################################
################################################
####      Functions fire_extinguisher        ###
################################################
################################################

    def lookTarget(self,image):
        target_thres = 2000
        low_thres = [23,25,110]
        high_thres = [100,80,255]
        
        mask, thres = self.checkColor(image, low_thres, high_thres)
        target_size =  len(np.transpose(np.nonzero(mask)))
        if(not self.__targetFound):
            print(target_size, " pikselia")
            if(target_size > target_thres):
                self.__targetFound = True
                self.sendTweet("fire extinguisher found")

################################################
################################################
####  Functions for motor, servo, distance   ###
################################################
################################################


    def setMotor(self, lMotor, rMotor):
        self.__lMotorVal = lMotor
        self.__rMotorVal = rMotor
        
        GPG.set_motor_dps(GPG.MOTOR_LEFT, lMotor)
        GPG.set_motor_dps(GPG.MOTOR_RIGHT, rMotor)

    def followColor(self, x,y):
        heitto = abs(x - 160)
        
        if(x < 130): #Target left
            print("Target Left")
            self.setMotor(225, 300)
        elif(x > 190): #Target right
            print("Target Right")
            self.setMotor(300,225)
        else: #Target ahead
            print("Target ahead")
            self.setMotor(300,300)

    def getMotorVal(self):
        return self.__lMotorVal, self.__rMotorVal

    def setServo(self, value):
            GPG.set_servo(GPG.SERVO_2, value)
            sleep(0.1)

    def getDistance(self):
        distance = 0
        for i in range(0,5):
            distance = distance + mySensor.read_mm()
        return int(distance/5)

    def getDistanceV2(self):
        distance = [0,0,0] 
        for i in range(0,3):
            distance[i] = mySensor.read_mm()
        distance = sorted(distance)
        return distance[1]

    def checkRoad(self):
        return self.__clearRoad

    def setRoad(self, value):
        self.__clearRoad = value

    def lookOutObjects(self):
        servoPos = [1100,1400,1700]
        angle = 0
        while 1:
            angle = angle + 1
            if angle > 2:
                angle = 0
 
            self.setServo(servoPos[angle])
            distV = self.getDistanceV2()
            if(distV < FRONT_OBJECT_THRESHOLD):
                break

    def sweepArea(self):
        distCheck = True
        self.setMotor(0,0)
        for i in range(650, 2150, 200):
            self.setServo(i)
            dist = self.getDistanceV2()
            print(dist, " : ", i)
            if(dist < FRONT_OBJECT_THRESHOLD):
                distCheck = False
                self.__nextSweep = SWEEP_TIME
                return distCheck
            
        return distCheck

    def sweepTimeOut(self):
        if(self.__nextSweep <= 0):
            self.__nextSweep = SWEEP_TIME
            return True
        else:
            return False

    def searchColor(self):
        self.setMotor(50, -50)

    def evadeObject(self):
        distS = 0
        distF = 0
        prs = 0.5
        self.setServo(700)
        distS = self.getDistanceV2()
        self.setServo(1400)    
        distF = self.getDistanceV2()
        print("DistanceF/S:", distF,distS)

        if(distF < FRONT_OBJECT_THRESHOLD): 
            print("Object ahead")
            self.setMotor(0,100)
        else: 
            newMotorSpeed = (SIDE_OBJECT_THRESHOLD/distS)*100
            self.__motorSpeed = self.__motorSpeed * prs + newMotorSpeed * (1-prs)
            if(self.__motorSpeed > 150):
                self.setMotor(100,150)
            else:
                self.setMotor(100,self.__motorSpeed)
        if(self.__bitCount > self.__color_Threshold):
            if(self.__x > 120 and self.__x < 200):
                print("Kuva edessa ")
                if(distF > FRONT_OBJECT_THRESHOLD):
                    self.setRoad(True)
                    self.__motorSpeed = 100
                    self.followColor(self.__x,self.__y)


