from itertools import product as product
from math import ceil

import numpy as np


class Anchors(object):
    def __init__(self, cfg, image_size=None):
        super(Anchors, self).__init__()
        self.min_sizes  = cfg['min_sizes'] #先验框基础宽高
        self.steps      = cfg['steps'] #压缩倍数
        self.clip       = cfg['clip']
        #---------------------------#
        #   图片的尺寸
        #---------------------------#
        self.image_size = image_size
        #---------------------------#
        #   模拟三个有效特征层高和宽
        #---------------------------#  ceil(self.image_size[0] / step)有效特征层宽高
        self.feature_maps = [[ceil(self.image_size[0] / step), ceil(self.image_size[1] / step)] for step in self.steps]

    def get_anchors(self):
        anchors = []
        for k, f in enumerate(self.feature_maps): #三个特征层的宽高循环
            min_sizes = self.min_sizes[k]
            #-----------------------------------------#
            #   对特征层的高和宽进行循环迭代
            #-----------------------------------------#
            for i, j in product(range(f[0]), range(f[1])):#生成先验框x,y坐标--生成大网格以使先验框遍布在整张图片上
                for min_size in min_sizes: #对每个有效特征层里的两个先验框循环
                    s_kx = min_size / self.image_size[1]
                    s_ky = min_size / self.image_size[0]
                    dense_cx = [x * self.steps[k] / self.image_size[1] for x in [j + 0.5]]#计算先验框中心
                    dense_cy = [y * self.steps[k] / self.image_size[0] for y in [i + 0.5]]
                    for cy, cx in product(dense_cy, dense_cx):
                        anchors += [cx, cy, s_kx, s_ky]  #先验框中心，宽高
     
        anchors = np.reshape(anchors,[-1,4])

        output = np.zeros_like(anchors[:,:4])
        #-----------------------------------------#
        #   将先验框的形式由中心，宽高转换成左上角，右下角的形式
        #-----------------------------------------#
        output[:,0] = anchors[:,0] - anchors[:,2]/2
        output[:,1] = anchors[:,1] - anchors[:,3]/2
        output[:,2] = anchors[:,0] + anchors[:,2]/2
        output[:,3] = anchors[:,1] + anchors[:,3]/2

        if self.clip:
            output = np.clip(output, 0, 1)
        return output
#一个网格点两个大小不同的先验框   20*20特征层又800特征点，每个特征点两个先验框
#网络就是对这些预先设定好的先验框进行调整判断