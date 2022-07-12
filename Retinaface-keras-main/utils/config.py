# config.py

cfg_mnet = {
    'name'              : 'mobilenet0.25',#小目标卷积次数多，有更多的语义信息，图像在多次卷积后小目标的特征容易消失
    'min_sizes'         : [[16, 32], [64, 128], [256, 512]],#不同大小特征层对应的先验框大小
    'steps'             : [8, 16, 32],#特征层压缩次数 压缩3次4次5次 由浅到深

    'clip'              : False,#是否将先验框固定0-1之间
    'loc_weight'        : 2.0,
    #------------------------------------------------------------------#
    #   视频上看到的训练图片大小为640，为了提高大图状态下的困难样本
    #   的识别能力，我将训练图片进行调大
    #------------------------------------------------------------------#
    'train_image_size'  : 832,
    'out_channel'       : 64  #输出通道数64
}

cfg_re50 = {
    'name'              : 'Resnet50',
    'min_sizes'         : [[16, 32], [64, 128], [256, 512]],
    'steps'             : [8, 16, 32],
    
    'clip'              : False,
    'loc_weight'        : 2.0,
    #------------------------------------------------------------------#
    #   视频上看到的训练图片大小为840，为了满足32的倍数要求，修改成了832
    #------------------------------------------------------------------#
    'train_image_size'  : 832,
    'out_channel'       : 256
}

