import os
import threading
import time

import cv2
import numpy as np
import pygame
from keras.applications.imagenet_utils import preprocess_input

from net.mobilenet import MobileNet
from net.mtcnn import mtcnn
from retinaface import Retinaface
from utils import m_utils
file_slogan_short='./radio/slogan_short.mp3'
pygame.mixer.init(frequency=16000, size=-16, channels=2, buffer=4096)
def slogan_short():
    timeplay = 1.5
    global playflag_short
    playflag_short = 0
    while True:
        if playflag_short == 1:
            track = pygame.mixer.music.load(file_slogan_short)
            print("------------请您戴好口罩")
            pygame.mixer.music.play()
            time.sleep(timeplay)
            playflag_short = 0
        time.sleep(0)
def facesdetecter_init():
    global thread_slogan
    global thread_slogan_short

    #多线程进行播放
    thread_slogan_short = threading.Thread(target=slogan_short).start()

class mask_rec():
    def __init__(self):
        #-------------------------#
        #   创建mtcnn的模型
        #   用于检测人脸
        #-------------------------#
        facesdetecter_init()
        self.mtcnn_model = mtcnn()
        self.retinaface = Retinaface()
        self.threshold = [0.5,0.6,0.8]
               
        #-------------------------#
        #   创建mobilenet的模型
        #   用于判断是否佩戴口罩
        #-------------------------#
        self.classes_path = "model_data/classes.txt"
        self.class_names = self._get_class()
        self.Crop_HEIGHT = 224
        self.Crop_WIDTH = 224
        self.NUM_CLASSES = len(self.class_names)
        self.mask_model = MobileNet(input_shape=[self.Crop_HEIGHT,self.Crop_WIDTH,3], classes=self.NUM_CLASSES)
        self.mask_model.load_weights("./logs/last_one.h5")

    def _get_class(self):
        classes_path = os.path.expanduser(self.classes_path)
        with open(classes_path) as f:
            class_names = f.readlines()
        class_names = [c.strip() for c in class_names]
        return class_names

    def recognize(self,draw):
        height,width,_ = np.shape(draw)
        # print("h,w",height,width) 480 640
        draw_rgb = cv2.cvtColor(draw,cv2.COLOR_BGR2RGB)

        #--------------------------------#
        #   检测人脸
        #--------------------------------#
        rectangles = self.mtcnn_model.detectFace(draw_rgb, self.threshold)
        if len(rectangles)==0:
            return
        rectangles = np.array(rectangles,dtype=np.int32)
        rectangles_temp = m_utils.rect2square(rectangles) #clip防止人脸框超出预测范围，并将长方形框变成正方形
        rectangles_temp[:, [0,2]] = np.clip(rectangles_temp[:, [0,2]], 0, width)
        rectangles_temp[:, [1,3]] = np.clip(rectangles_temp[:, [1,3]], 0, height)
        #-----------------------------------------------#
        #   对检测到的人脸进行编码
        #-----------------------------------------------#
        classes_all = []
        for rectangle in rectangles_temp:
            #---------------#
            #   截取图像
            #---------------#
            landmark = np.reshape(rectangle[5:15], (5,2)) - np.array([int(rectangle[0]), int(rectangle[1])])
            crop_img = draw_rgb[int(rectangle[1]):int(rectangle[3]), int(rectangle[0]):int(rectangle[2])]
            #-----------------------------------------------#
            #   利用人脸关键点进行人脸对齐
            #-----------------------------------------------#
            crop_img,_ = m_utils.Alignment_1(crop_img,landmark)

            crop_img = cv2.resize(crop_img, (self.Crop_WIDTH,self.Crop_HEIGHT))
            crop_img = preprocess_input(np.reshape(np.array(crop_img, np.float64),[1, self.Crop_HEIGHT, self.Crop_WIDTH, 3]))
               #                      判断标签              判断是否佩戴口罩
            classes = self.class_names[np.argmax(self.mask_model.predict(crop_img)[0])]
            if(classes=="nomask"):                     # 传入模型中进行预测
                global playflag_short
                playflag_short = 1
                print("请佩戴口罩")

            classes_all.append(classes)

        rectangles = rectangles[:, 0:4]
        print("classes_all",classes_all)
        #-----------------------------------------------#
        #   画框~!~
        #-----------------------------------------------#
        for (left, top, right, bottom), c in zip(rectangles,classes_all):
            cv2.rectangle(draw, (left, top), (right, bottom), (0, 0, 255), 2)
            font = cv2.FONT_HERSHEY_SIMPLEX
            cv2.putText(draw, c, (left , bottom - 15), font, 0.75, (255, 255, 255), 2)  
        return draw

if __name__ == "__main__":
    dududu = mask_rec()

    video_capture = cv2.VideoCapture(0)
    while True:
        ret, draw = video_capture.read()

        dududu.recognize(draw) 

        cv2.imshow('Video', draw)
        if cv2.waitKey(20) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()