import keras.backend as K
from keras.layers import Activation, Dense, Input, Lambda
from keras.models import Model

from nets.inception_resnetv1 import InceptionResNetV1
from nets.mobilenet import MobileNet


def facenet(input_shape, num_classes=None, backbone="mobilenet", mode="train"):
    inputs = Input(shape=input_shape)
    if backbone=="mobilenet":
        model = MobileNet(inputs, dropout_keep_prob=0.4)
    elif backbone=="inception_resnetv1":
        model = InceptionResNetV1(inputs, dropout_keep_prob=0.4)
    else:
        raise ValueError('Unsupported backbone - `{}`, Use mobilenet, inception_resnetv1.'.format(backbone))

    if mode == "train": #构建分类器
        #-----------------------------------------#
        #   训练的话利用交叉熵和triplet_loss
        #   结合一起训练
        #-----------------------------------------#   #全连接的作用是辅助收敛，所以实际预测时时不需要它的
        logits = Dense(num_classes)(model.output) #全连接神经元个数是当前数据集需要区分的人脸的个数
        softmax = Activation("softmax", name = "Softmax")(logits) #需要进行交叉熵运算
           #L2标准化的目的就是进行TripletLoss的构建
        normalize = Lambda(lambda  x: K.l2_normalize(x, axis=1), name="Embedding")(model.output)
        combine_model = Model(inputs, [softmax, normalize])
        return combine_model
    elif mode == "predict":
        #--------------------------------------------#
        #   预测的时候只需要考虑人脸的特征向量就行了
        #--------------------------------------------#进行L2标准化-将不同的人脸特征向量映射到统一数量级上
        x = Lambda(lambda  x: K.l2_normalize(x, axis=1), name="Embedding")(model.output)
        model = Model(inputs,x)
        return model
    else:
        raise ValueError('Unsupported mode - `{}`, Use train, predict.'.format(mode))

