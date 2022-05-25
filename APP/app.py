from flask import Flask,render_template,Response
import cv2
import numpy as np
import os
from flask_socketio import SocketIO,emit
import json
import time
from threading import Thread
# import serial
# ser = serial.Serial('/dev/ttyACM0',9600)
# import RPi.GPIO as gpio
# dung = 5
# lui = 6
# vuong = 13
# gpio.setwarnings(False) 
# gpio.setmode(gpio.BCM)
# gpio.cleanup()
# gpio.setup(dung,gpio.OUT)
# gpio.setup(lui,gpio.OUT)
# gpio.setup(vuong,gpio.OUT)
dulieu ='''
{
    "tendoituong":"Chưa nhận biết",
    "Nhietdo":30,
    "cambien":0
}
'''
moi = json.loads(dulieu)
print(moi['cambien'])
class Videoget:
    def __init__(self,src=0):
        self.stream = cv2.VideoCapture(src)
        (self.grabbed,self.frame) = self.stream.read()
        self.stopped = False
    def start(self):
        Thread(target=self.get,args=()).start()
        return self
    def get(self):
        while not self.stopped:
            if not self.grabbed:
                self.stop()
            else:
                (self.grabbed,self.frame) = self.stream.read()
    def stop(self):
        self.stopped = True
class Videoshow:
    def __init__(self, frame=None, thres=40, desList=None,classname=None):
        self.imgGray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        (self.kp2, self.des2) = orb.detectAndCompute(self.imgGray, None)
        self.bf = cv2.BFMatcher()
        self.matchList = []
        self.finalVal = -1
        self.thres = thres
        self.frame = frame
        self.stopped = False
        self.desList = desList
        self.classNames=classname
    def start(self):
        Thread(target=self.show,args=()).start()
        return self
    def show(self):
        while not self.stopped:
            try:
                for self.des in self.desList:
                    self.matches = self.bf.knnMatch(self.des, self.des2, k=2)
                    self.good = []
                    for self.m, self.n in self.matches:
                        if self.m.distance < 0.75 * self.n.distance:
                            self.good.append([self.m])
                    self.matchList.append(len(self.good))
            except:
                pass
            print(self.matchList)
            if len(self.matchList) != 0:
                if max(self.matchList) > self.thres:
                    self.finalVal = self.matchList.index(max(self.matchList))
                else:self.finalVal = -1
            else: self.finalVal = -1
            self.matchList = []
    def find(self):
        return self.finalVal
    def stop(self):
        self.stopped = True
path = r'C:\Users\OS\Desktop\file đĩa\PHULUC\APP\static\queryPictures1'
images = []
classname = []
myList = os.listdir(path)
orb = cv2.ORB_create(nfeatures=1000)
for cl in myList:
    imgCur = cv2.imread(f'{path}/{cl}',0)
    images.append(imgCur)
    classname.append(os.path.splitext(cl)[0])
def findDes(images):
    desList = []
    for img in images:
        kp,des = orb.detectAndCompute(img,None)
        desList.append(des)   
    return desList
desList = findDes(images)
app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
app.debug =False
app.threaded = True
socketio = SocketIO(app,async_mode='threading',cors_allowed_origins="*",engineio_logger=True,logger=True)
id = -1
def gen_frames(src=0):
    video_getter = Videoget(src).start()
    video_shower = Videoshow(video_getter.frame, 40, desList,classname).start()
    while 1:
        if video_getter.stopped or video_shower.stopped:
            video_shower.stop()
            video_getter.stop()
            video_getter.stream.release()
            cv2.destroyAllWindows()
            break
        video_shower.frame = video_getter.frame
        global id
        id = video_shower.find()
        video_shower.imgGray = cv2.cvtColor(video_getter.frame, cv2.COLOR_BGR2GRAY)
        (video_shower.kp2, video_shower.des2) = orb.detectAndCompute(video_shower.imgGray, None)
        video_shower.bf = cv2.BFMatcher()
        if not video_getter.grabbed:
            break
        else:
            ret,buffer = cv2.imencode('.jpg',video_shower.frame)
            frame = buffer.tobytes()
            yield(b'--frame\r\n'
                b'Content-Type:image/jpeg\r\n\r\n'+frame+b'\r\n')
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(),mimetype='multipart/x-mixed-replace;boundary=frame')   
@socketio.on('guidi')
def handle_request(data):
    dulieudualen = json.loads(dulieu)
    # if(ser.in_waiting>0):
    #         line = ser.readline().decode("utf-8")
    #         temp = line.split('|')[0]
    #         dis  = line.split('|')[1]
    # dulieudualen['Nhietdo'] = temp
    if id==-1:
        dulieudualen['tendoituong'] = 'ĐƯỜNG DÂY'
    else:
        dulieudualen['tendoituong'] = classname[id]
        # if classname[id]=='chuoisuneo':
        #     gpio.output(dung,1)
		# 	gpio.output(lui,0)
		# 	gpio.output(vuong,0)
        # if classname[id]=='chuoisudung':
        #     dulieudualen['cambien'] = dis
        #     if dis == 1:
        #         gpio.output(dung,0)
		# 		gpio.output(lui,1)
		# 		gpio.output(vuong,0))
        #     else:
        #         gpio.output(dung,0)
		# 		gpio.output(lui,0)
		# 		gpio.output(vuong,1)       
    print('on guidi-')
    socketio.emit('mess_from_server',json.dumps(dulieudualen))

if __name__ == '__main__':
    socketio.run(app)





