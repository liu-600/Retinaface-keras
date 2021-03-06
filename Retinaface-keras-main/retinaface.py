import time

import cv2
import numpy as np
from keras.applications.imagenet_utils import preprocess_input
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

from nets.facenet import facenet
from nets_retinaface.retinaface import RetinaFace
from utils.anchors import Anchors
from utils.config import cfg_mnet, cfg_re50
from utils.utils import (Alignment_1, BBoxUtility, compare_faces,
                         letterbox_image, retinaface_correct_boxes)

#--------------------------------------#
#   写中文需要转成PIL来写。
#--------------------------------------#
def cv2ImgAddText(img, label, left, top, textColor=(255, 255, 255)):
    img = Image.fromarray(np.uint8(img))
    #---------------#
    #   设置字体
    #---------------#
    font = ImageFont.truetype(font='model_data/simhei.ttf', size=20)

    draw = ImageDraw.Draw(img)
    label = label.encode('utf-8')
    draw.text((left, top), str(label,'UTF-8'), fill=textColor, font=font)
    return np.asarray(img)
    
#--------------------------------------#
#   一定注意backbone和model_path的对应。
#   在更换facenet_model后，
#   一定要注意重新编码人脸。
#--------------------------------------#
class Retinaface(object):
    _defaults = {
        #----------------------------------------------------------------------#
        #   retinaface训练完的权值路径
        #----------------------------------------------------------------------#
        "retinaface_model_path" : 'model_data/retinaface_mobilenet025.h5',
        #----------------------------------------------------------------------#
        #   retinaface所使用的主干网络，有mobilenet和resnet50
        #----------------------------------------------------------------------#
        "retinaface_backbone"   : "mobilenet",
        #----------------------------------------------------------------------#
        #   retinaface中只有得分大于置信度的预测框会被保留下来
        #----------------------------------------------------------------------#
        "confidence"            : 0.5,
        #----------------------------------------------------------------------#
        #   retinaface中非极大抑制所用到的nms_iou大小
        #----------------------------------------------------------------------#
        "nms_iou"               : 0.3,
        #----------------------------------------------------------------------#
        #   是否需要进行图像大小限制。
        #   输入图像大小会大幅度地影响FPS，想加快检测速度可以减少input_shape。
        #   开启后，会将输入图像的大小限制为input_shape。否则使用原图进行预测。
        #   keras代码中主干为mobilenet时存在小bug，当输入图像的宽高不为32的倍数
        #   会导致检测结果偏差，主干为resnet50不存在此问题。
        #   可根据输入图像的大小自行调整input_shape，注意为32的倍数，如[640, 640, 3]
        #----------------------------------------------------------------------#
        "retinaface_input_shape": [640, 640, 3],
        #----------------------------------------------------------------------#
        #   是否需要进行图像大小限制。
        #----------------------------------------------------------------------#
        "letterbox_image"       : True,

        #----------------------------------------------------------------------#
        #   facenet训练完的权值路径
        #----------------------------------------------------------------------#
        "facenet_model_path"    : 'model_data/facenet_mobilenet.h5',
        #----------------------------------------------------------------------#
        #   facenet所使用的主干网络， mobilenet和inception_resnetv1
        #----------------------------------------------------------------------#
        "facenet_backbone"      : "mobilenet",
        #----------------------------------------------------------------------#
        #   facenet所使用到的输入图片大小
        #----------------------------------------------------------------------#
        "facenet_input_shape"   : [160, 160, 3],
        #----------------------------------------------------------------------#
        #   facenet所使用的人脸距离门限
        #----------------------------------------------------------------------#
        "facenet_threhold"      : 0.9,
    }

    @classmethod
    def get_defaults(cls, n):
        if n in cls._defaults:
            return cls._defaults[n]
        else:
            return "Unrecognized attribute name '" + n + "'"

    #---------------------------------------------------#
    #   初始化Retinaface+facenet
    #---------------------------------------------------#
    def __init__(self, encoding=0, **kwargs):
        self.__dict__.update(self._defaults)
        for name, value in kwargs.items():
            setattr(self, name, value)
            
        #---------------------------------------------------#
        #   不同主干网络的config信息
        #---------------------------------------------------#
        if self.retinaface_backbone == "mobilenet":
            self.cfg = cfg_mnet #参数
        else:
            self.cfg = cfg_re50

        #---------------------------------------------------#
        #   工具箱和先验框的生成
        #---------------------------------------------------#
        self.bbox_util  = BBoxUtility(nms_thresh=self.nms_iou)
        self.anchors    = Anchors(self.cfg, image_size=(self.retinaface_input_shape[0], self.retinaface_input_shape[1])).get_anchors()
        self.generate()

        try:
            print("载入人脸编码中...")
            self.known_face_encodings = np.load("model_data/{backbone}_face_encoding.npy".format(backbone=self.facenet_backbone))
            self.known_face_names     = np.load("model_data/{backbone}_names.npy".format(backbone=self.facenet_backbone))

        except:
            if not encoding:
                print("载入已有人脸特征失败，请检查model_data下面是否生成了相关的人脸特征文件。")
            pass

    #---------------------------------------------------#
    #   获得所有的分类
    #---------------------------------------------------#
    def generate(self):
        self.retinaface = RetinaFace(self.cfg, self.retinaface_backbone)
        self.facenet    = facenet(self.facenet_input_shape, backbone=self.facenet_backbone, mode='predict')
        #-------------------------------#
        #   载入模型与权值
        #-------------------------------#
        print('Loading weights into state dict...')
        self.retinaface.load_weights(self.retinaface_model_path, by_name=True)
        self.facenet.load_weights(self.facenet_model_path, by_name=True)
        print('Finished!')

    def encode_face_dataset(self, image_paths, names):
        face_encodings = []
        for index, path in enumerate(tqdm(image_paths)):
            #---------------------------------------------------#
            #   打开人脸图片
            #---------------------------------------------------#
            image       = np.array(Image.open(path), np.float32)
            #---------------------------------------------------#
            #   对输入图像进行一个备份
            #---------------------------------------------------#
            old_image   = image.copy()
            #---------------------------------------------------#
            #   计算输入图片的高和宽
            #---------------------------------------------------#
            im_height, im_width, _ = np.shape(image)
            #---------------------------------------------------#
            #   计算scale，用于将获得的预测框转换成原图的高宽
            #---------------------------------------------------#
            scale = [
                np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
            ]
            scale_for_landmarks = [
                np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
                np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
                np.shape(image)[1], np.shape(image)[0]
            ]

            #---------------------------------------------------------#
            #   letterbox_image可以给图像增加灰条，实现不失真的resize
            #---------------------------------------------------------#
            if self.letterbox_image:
                image = letterbox_image(image,[self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
                anchors = self.anchors
            else:
                anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
            #---------------------------------------------------#
            #   图片预处理，归一化
            #---------------------------------------------------#
            photo = np.expand_dims(preprocess_input(image),0)
            #---------------------------------------------------#
            #   将处理完的图片传入Retinaface网络当中进行预测
            #---------------------------------------------------#
            preds = self.retinaface.predict(photo)
            #---------------------------------------------------#
            #   Retinaface网络的解码，最终我们会获得预测框
            #   将预测结果进行解码和非极大抑制
            #---------------------------------------------------#
            results = self.bbox_util.detection_out(preds,anchors,confidence_threshold=self.confidence)

            if len(results)<=0:
                print(names[index], "：未检测到人脸")
                continue

            results = np.array(results)
            #---------------------------------------------------------#
            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            #---------------------------------------------------------#
            if self.letterbox_image:
                results = retinaface_correct_boxes(results, np.array((self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))
            # :4  前4个是框的坐标 对人脸进行截取
            # 5以后是人脸关键点坐标 对人脸进行校正
            # 4 是人脸框的置信度
            results[:, :4] = results[:, :4] * scale
            results[:, 5:] = results[:, 5:] * scale_for_landmarks

            #---------------------------------------------------#
            #   选取最大的人脸框。
            #---------------------------------------------------#
            best_face_location  = None
            biggest_area        = 0
            for result in results:
                left, top, right, bottom = result[0:4]

                w = right - left
                h = bottom - top
                if w * h > biggest_area:
                    biggest_area = w * h
                    best_face_location = result

            #---------------------------------------------------#
            #   截取图像
            #---------------------------------------------------#
               # [1][3]人脸框的上下y轴坐标 【0】【2】左右x轴坐标
            crop_img = old_image[int(best_face_location[1]):int(best_face_location[3]), int(best_face_location[0]):int(best_face_location[2])]
               #得到人脸关键点相较于左上角的坐标
            landmark = np.reshape(best_face_location[5:], (5,2)) - np.array([int(best_face_location[0]), int(best_face_location[1])])
            crop_img, _ = Alignment_1(crop_img, landmark) #矫正

                      #不失真的resize--在图像周围添加上灰条 ，归一化
            crop_img = np.array(letterbox_image(np.uint8(crop_img), (self.facenet_input_shape[1],self.facenet_input_shape[0]))) / 255
                 #添加batch_size维度，以传入facenent
            crop_img = np.expand_dims(crop_img, 0)
            #---------------------------------------------------#
            #   利用图像算取长度为128的特征向量
            #---------------------------------------------------#
               #[0]取预测结果
            face_encoding = self.facenet.predict(crop_img)[0]
            face_encodings.append(face_encoding)

        np.save("model_data/{backbone}_face_encoding.npy".format(backbone=self.facenet_backbone),face_encodings)
        np.save("model_data/{backbone}_names.npy".format(backbone=self.facenet_backbone),names)

    #---------------------------------------------------#
    #   检测图片
    #---------------------------------------------------#
    def detect_image(self, image):
        #---------------------------------------------------#
        #   对输入图像进行一个备份，后面用于绘图
        #---------------------------------------------------#
        old_image   = image.copy()
        #---------------------------------------------------#
        #   把图像转换成numpy的形式
        #---------------------------------------------------#
        image       = np.array(image, np.float32)

        #---------------------------------------------------#
        #   Retinaface检测部分-开始
        #---------------------------------------------------#
        #---------------------------------------------------#
        #   计算输入图片的高和宽
        #---------------------------------------------------#
        im_height, im_width, _ = np.shape(image)
        #---------------------------------------------------#
        #   计算scale，用于将获得的预测框转换成原图的高宽
        #---------------------------------------------------#
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        #---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        #---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image,[self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()    #获得整张图片所有先验框
        #---------------------------------------------------#
        #   图片预处理，归一化
        #---------------------------------------------------#
        photo = np.expand_dims(preprocess_input(image),0)#增加batcchsize维度

        #---------------------------------------------------#
        #   将处理完的图片传入Retinaface网络当中进行预测------
        #---------------------------------------------------#
        preds = self.retinaface.predict(photo) # 预测是获得对先验框的调整参数，人脸关键点的调整参数，人脸的预测概率

        #---------------------------------------------------#
        #   Retinaface网络的解码，最终我们会获得预测框
        #   将预测结果进行解码和非极大抑制
        #---------------------------------------------------#
        results = self.bbox_util.detection_out(preds,anchors,confidence_threshold=self.confidence) #解码
                    #预测结果是小数形式
        #---------------------------------------------------#
        #   如果没有预测框则返回原图
        #---------------------------------------------------#
        if len(results) <= 0:
            print("没检测出人脸")
            return old_image,None


        results = np.array(results)
        #---------------------------------------------------------#
        #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
        #---------------------------------------------------------#
        if self.letterbox_image:
            results = retinaface_correct_boxes(results, np.array((self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))

        #---------------------------------------------------#
        #   4人脸框置信度
        #   :4是框的坐标---人脸截取
        #   5:是人脸关键点的坐标---人脸矫正
        #---------------------------------------------------#
        results[:, :4] = results[:, :4] * scale#预测结果从小数转换成像素形式
        results[:, 5:] = results[:, 5:] * scale_for_landmarks
        #---------------------------------------------------#
        #   Retinaface检测部分-结束
        #---------------------------------------------------#

        #-----------------------------------------------#
        #   Facenet编码部分-开始
        #-----------------------------------------------#
        face_encodings = []
        for result in results:
            #----------------------#
            #   图像截取，人脸矫正
            #----------------------#
            result      = np.maximum(result, 0) #人脸框上下y坐标     左右x轴坐标
            crop_img    = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
            landmark    = np.reshape(result[5:], (5,2)) - np.array([int(result[0]), int(result[1])]) #将人脸关键点坐标转化为 相对于人脸框的坐标
            crop_img, _ = Alignment_1(crop_img, landmark)

            #----------------------#
            #   人脸编码
            #----------------------#

            #-----------------------------------------------#
            #   不失真的resize，然后进行归一化（/255）
            #-----------------------------------------------#
            crop_img = np.array(letterbox_image(np.uint8(crop_img),(self.facenet_input_shape[1],self.facenet_input_shape[0])))/255
            crop_img = np.expand_dims(crop_img,0)
            #-----------------------------------------------#
            #   利用图像算取长度为128的特征向量
            #-----------------------------------------------#
            face_encoding = self.facenet.predict(crop_img)[0]  #利用facenet进行预测--即获得特征向量
            face_encodings.append(face_encoding)#保存着人脸的特征向量
        #-----------------------------------------------#
        #   Facenet编码部分-结束
        #-----------------------------------------------#

        #-----------------------------------------------#
        #   人脸特征比对-开始
        #-----------------------------------------------#
        face_names = []
        for face_encoding in face_encodings:
            #-----------------------------------------------------#
            #   取出一张脸并与数据库中所有的人脸特征向量进行对比，计算得分
            #-----------------------------------------------------#
            matches, face_distances = compare_faces(self.known_face_encodings, face_encoding, tolerance = self.facenet_threhold)
            name = "Unknown"
            #-----------------------------------------------------#
            #   找到已知最贴近当前人脸的人脸  序号
            #-----------------------------------------------------#
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:  #判断是否为true即满足门限要求，取出他的名字name
                name = self.known_face_names[best_match_index] #可以认为是数据库中相同身份的人脸
            face_names.append(name)  #放入列表
        #-----------------------------------------------#
        #   人脸特征比对-结束
        #-----------------------------------------------#
   #绘制
        for i, b in enumerate(results): # 对所有预测框进行循环
            text    = "{:.4f}".format(b[4])#得分-置信度
            b       = list(map(int, b))
            #---------------------------------------------------#
            #   b[0]-b[3]为人脸框的坐标，b[4]为得分 画框
            #---------------------------------------------------#
            cv2.rectangle(old_image, (b[0], b[1]), (b[2], b[3]), (0, 0, 255), 2)
            cx = b[0]
            cy = b[1] + 12
            cv2.putText(old_image, text, (cx, cy),
                        cv2.FONT_HERSHEY_DUPLEX, 0.5, (255, 255, 255))


            #---------------------------------------------------#
            #   b[5]-b[14]为人脸关键点的坐标 画关键点
            #---------------------------------------------------#
            cv2.circle(old_image, (b[5], b[6]), 1, (0, 0, 255), 4)
            cv2.circle(old_image, (b[7], b[8]), 1, (0, 255, 255), 4)
            cv2.circle(old_image, (b[9], b[10]), 1, (255, 0, 255), 4)
            cv2.circle(old_image, (b[11], b[12]), 1, (0, 255, 0), 4)
            cv2.circle(old_image, (b[13], b[14]), 1, (255, 0, 0), 4)

            name = face_names[i] #取出人脸名字
            # font = cv2.FONT_HERSHEY_SIMPLEX
            # cv2.putText(old_image, name, (b[0] , b[3] - 15), font, 0.75, (255, 255, 255), 2)
            #--------------------------------------------------------------#
            #   cv2不能写中文，加上这段可以，但是检测速度会有一定的下降。
            #   如果不是必须，可以换成cv2只显示英文。
            #--------------------------------------------------------------#
            old_image = cv2ImgAddText(old_image, name, b[0]+5 , b[3] - 25)
        return old_image,face_names   #face_names我添加的返回值


    def get_FPS(self, image, test_interval):
        #---------------------------------------------------#
        #   对输入图像进行一个备份，后面用于绘图
        #---------------------------------------------------#
        old_image   = image.copy()
        #---------------------------------------------------#
        #   把图像转换成numpy的形式
        #---------------------------------------------------#
        image       = np.array(image, np.float32)

        #---------------------------------------------------#
        #   Retinaface检测部分-开始
        #---------------------------------------------------#
        #---------------------------------------------------#
        #   计算输入图片的高和宽
        #---------------------------------------------------#
        im_height, im_width, _ = np.shape(image)
        #---------------------------------------------------#
        #   计算scale，用于将获得的预测框转换成原图的高宽
        #---------------------------------------------------#
        scale = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0]
        ]
        scale_for_landmarks = [
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0], np.shape(image)[1], np.shape(image)[0],
            np.shape(image)[1], np.shape(image)[0]
        ]

        #---------------------------------------------------------#
        #   letterbox_image可以给图像增加灰条，实现不失真的resize
        #---------------------------------------------------------#
        if self.letterbox_image:
            image = letterbox_image(image,[self.retinaface_input_shape[1], self.retinaface_input_shape[0]])
            anchors = self.anchors
        else:
            anchors = Anchors(self.cfg, image_size=(im_height, im_width)).get_anchors()
        #---------------------------------------------------#
        #   图片预处理，归一化
        #---------------------------------------------------#
        photo = np.expand_dims(preprocess_input(image),0)

        #---------------------------------------------------#
        #   将处理完的图片传入Retinaface网络当中进行预测
        #---------------------------------------------------#
        preds = self.retinaface.predict(photo)

        #---------------------------------------------------#
        #   Retinaface网络的解码，最终我们会获得预测框
        #   将预测结果进行解码和非极大抑制
        #---------------------------------------------------#
        results = self.bbox_util.detection_out(preds,anchors,confidence_threshold=self.confidence)

        #---------------------------------------------------#
        #   如果没有预测框则返回原图
        #---------------------------------------------------#
        if len(results) > 0:
            results = np.array(results)
            #---------------------------------------------------------#
            #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
            #---------------------------------------------------------#
            if self.letterbox_image:
                results = retinaface_correct_boxes(results, np.array((self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))
            
            #---------------------------------------------------#
            #   4人脸框置信度
            #   :4是框的坐标
            #   5:是人脸关键点的坐标
            #---------------------------------------------------#
            results[:, :4] = results[:, :4] * scale
            results[:, 5:] = results[:, 5:] * scale_for_landmarks
            #---------------------------------------------------#
            #   Retinaface检测部分-结束
            #---------------------------------------------------#

            #-----------------------------------------------#
            #   Facenet编码部分-开始
            #-----------------------------------------------#
            face_encodings = []
            for result in results:
                #----------------------#
                #   图像截取，人脸矫正
                #----------------------#
                result      = np.maximum(result, 0)
                crop_img    = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
                landmark    = np.reshape(result[5:], (5,2)) - np.array([int(result[0]), int(result[1])])
                crop_img, _ = Alignment_1(crop_img, landmark)

                #----------------------#
                #   人脸编码
                #----------------------#

                #-----------------------------------------------#
                #   不失真的resize，然后进行归一化
                #-----------------------------------------------#
                crop_img = np.array(letterbox_image(np.uint8(crop_img),(self.facenet_input_shape[1],self.facenet_input_shape[0])))/255
                crop_img = np.expand_dims(crop_img,0)
                #-----------------------------------------------#
                #   利用图像算取长度为128的特征向量
                #-----------------------------------------------#
                face_encoding = self.facenet.predict(crop_img)[0]
                face_encodings.append(face_encoding)
            #-----------------------------------------------#
            #   Facenet编码部分-结束
            #-----------------------------------------------#

            #-----------------------------------------------#
            #   人脸特征比对-开始
            #-----------------------------------------------#
            face_names = []
            for face_encoding in face_encodings:
                #-----------------------------------------------------#
                #   取出一张脸并与数据库中所有的人脸进行对比，计算得分
                #-----------------------------------------------------#
                matches, face_distances = compare_faces(self.known_face_encodings, face_encoding, tolerance = self.facenet_threhold)
                name = "Unknown"
                #-----------------------------------------------------#
                #   找到已知最贴近当前人脸的人脸序号
                #-----------------------------------------------------#
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = self.known_face_names[best_match_index]
                face_names.append(name)
            #-----------------------------------------------#
            #   人脸特征比对-结束
            #-----------------------------------------------#
        
        t1 = time.time()
        for _ in range(test_interval):
            #---------------------------------------------------#
            #   将处理完的图片传入Retinaface网络当中进行预测
            #---------------------------------------------------#
            preds = self.retinaface.predict(photo)

            #---------------------------------------------------#
            #   Retinaface网络的解码，最终我们会获得预测框
            #   将预测结果进行解码和非极大抑制
            #---------------------------------------------------#
            results = self.bbox_util.detection_out(preds,anchors,confidence_threshold=self.confidence)

            #---------------------------------------------------#
            #   如果没有预测框则返回原图
            #---------------------------------------------------#
            if len(results) > 0:
                results = np.array(results)
                #---------------------------------------------------------#
                #   如果使用了letterbox_image的话，要把灰条的部分去除掉。
                #---------------------------------------------------------#
                if self.letterbox_image:
                    results = retinaface_correct_boxes(results, np.array((self.retinaface_input_shape[0], self.retinaface_input_shape[1])), np.array([im_height, im_width]))
                
                #---------------------------------------------------#
                #   4人脸框置信度
                #   :4是框的坐标
                #   5:是人脸关键点的坐标
                #---------------------------------------------------#
                results[:, :4] = results[:, :4] * scale
                results[:, 5:] = results[:, 5:] * scale_for_landmarks
                #---------------------------------------------------#
                #   Retinaface检测部分-结束
                #---------------------------------------------------#

                #-----------------------------------------------#
                #   Facenet编码部分-开始
                #-----------------------------------------------#
                face_encodings = []
                for result in results:
                    #----------------------#
                    #   图像截取，人脸矫正
                    #----------------------#
                    result      = np.maximum(result, 0)
                    crop_img    = np.array(old_image)[int(result[1]):int(result[3]), int(result[0]):int(result[2])]
                    landmark    = np.reshape(result[5:], (5,2)) - np.array([int(result[0]), int(result[1])])
                    crop_img, _ = Alignment_1(crop_img, landmark)

                    #----------------------#
                    #   人脸编码
                    #----------------------#

                    #-----------------------------------------------#
                    #   不失真的resize，然后进行归一化
                    #-----------------------------------------------#
                    crop_img = np.array(letterbox_image(np.uint8(crop_img),(self.facenet_input_shape[1],self.facenet_input_shape[0])))/255
                    crop_img = np.expand_dims(crop_img,0)
                    #-----------------------------------------------#
                    #   利用图像算取长度为128的特征向量
                    #-----------------------------------------------#
                    face_encoding = self.facenet.predict(crop_img)[0]
                    face_encodings.append(face_encoding)
                #-----------------------------------------------#
                #   Facenet编码部分-结束
                #-----------------------------------------------#

                #-----------------------------------------------#
                #   人脸特征比对-开始
                #-----------------------------------------------#
                face_names = []
                for face_encoding in face_encodings:
                    #-----------------------------------------------------#
                    #   取出一张脸并与数据库中所有的人脸进行对比，计算得分
                    #-----------------------------------------------------#
                    matches, face_distances = compare_faces(self.known_face_encodings, face_encoding, tolerance = self.facenet_threhold)
                    name = "Unknown"
                    #-----------------------------------------------------#
                    #   找到已知最贴近当前人脸的人脸序号
                    #-----------------------------------------------------#
                    best_match_index = np.argmin(face_distances)
                    if matches[best_match_index]:
                        name = self.known_face_names[best_match_index]
                    face_names.append(name)
                #-----------------------------------------------#
                #   人脸特征比对-结束
                #-----------------------------------------------#

        t2 = time.time()
        tact_time = (t2 - t1) / test_interval
        return tact_time
