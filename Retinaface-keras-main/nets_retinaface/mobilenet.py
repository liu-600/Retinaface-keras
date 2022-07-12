from keras import backend as K
from keras.layers import (Activation, BatchNormalization, Conv2D,
                          DepthwiseConv2D)


def relu6(x):
    return K.relu(x, max_value=6)

#----------------------------------#
#   普通的卷积块
#----------------------------------#
def _conv_block(inputs, filters, kernel=(3, 3), strides=(1, 1)):
    x = Conv2D(filters, kernel,
               padding='same',#Zeropading
               use_bias=False,
               strides=strides,
               name='conv1')(inputs) #卷积
    x = BatchNormalization(name='conv1_bn')(x)  #标准化
    return Activation(relu6, name='conv1_relu')(x) #激活函数

#----------------------------------#
#   深度可分离卷积块
#----------------------------------#
def _depthwise_conv_block(inputs, pointwise_conv_filters,
                          depth_multiplier=1, strides=(1, 1), block_id=1):
    x = DepthwiseConv2D((3, 3), #深度可分离卷积
                        padding='same',
                        depth_multiplier=depth_multiplier,
                        strides=strides,
                        use_bias=False,
                        name='conv_dw_%d' % block_id)(inputs)
    x = BatchNormalization(name='conv_dw_%d_bn' % block_id)(x)
    x = Activation(relu6, name='conv_dw_%d_relu' % block_id)(x)

    x = Conv2D(pointwise_conv_filters, (1, 1), #1*1卷积--调整通道数
               padding='same',
               use_bias=False,
               strides=(1, 1),
               name='conv_pw_%d' % block_id)(x)
    x = BatchNormalization(name='conv_pw_%d_bn' % block_id)(x)
    return Activation(relu6, name='conv_pw_%d_relu' % block_id)(x)

def MobileNet(img_input, depth_multiplier=1):
    # 640,640,3 -> 320,320,8
    x = _conv_block(img_input, 8, strides=(2, 2))
    
    # 320,320,8 -> 320,320,16
    x = _depthwise_conv_block(x, 16, depth_multiplier, block_id=1)

    # 320,320,16 -> 160,160,32  #strides=(2, 2)步长2*2改变了特征层shape宽高
    x = _depthwise_conv_block(x, 32, depth_multiplier, strides=(2, 2), block_id=2)
    x = _depthwise_conv_block(x, 32, depth_multiplier, block_id=3)

    # 160,160,32 -> 80,80,64
    x = _depthwise_conv_block(x, 64, depth_multiplier, strides=(2, 2), block_id=4)
    x = _depthwise_conv_block(x, 64, depth_multiplier, block_id=5)
    feat1 = x  #取x作为有效特征层

    # 80,80,64 -> 40,40,128
    x = _depthwise_conv_block(x, 128, depth_multiplier, strides=(2, 2), block_id=6)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=7)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=8)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=9)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=10)
    x = _depthwise_conv_block(x, 128, depth_multiplier, block_id=11)
    feat2 = x

    # 40,40,128 -> 20,20,256
    x = _depthwise_conv_block(x, 256, depth_multiplier, strides=(2, 2), block_id=12)
    x = _depthwise_conv_block(x, 256, depth_multiplier, block_id=13)
    feat3 = x
    return feat1, feat2, feat3  #返回三个有效特征层，进行fpn特征金字塔的构建

#初步特征提取--主干特征提取网络
#mobilenetv1对特征层进行5次长和宽的压缩，同时通道数进行扩张--下采样