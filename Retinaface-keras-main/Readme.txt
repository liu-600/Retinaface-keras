基于深度学习人脸识别的智能防疫系统
人脸识别采用RetinaFace+FaceNet ，口罩检测使用MTCNN进行人脸检测和经过训练的Mobilenet判断是否佩戴口罩。
tkinter做可视化界面
使用flask+layUI做web端
MySQL数据库存储居民信息

运行：UI.py 、manage.py
E:.
│  encoding.py 人脸编码
│  LICENSE
│  mask_recognize.py 口罩检测预测
│  predict.py 人脸检测识别预测
│  Readme.txt
│  README0.md
│  requirements.txt 环境配置需求
│  retinaface.py   class Retinaface类，配置初始化模型权重加载，人脸数据库编码人脸检测识别，主要功能的实现
│  UI.py 项目整体运行界面-tkinter
│
├─.idea
│  │  .gitignore
│  │  facenet-retinaface-keras-main.iml
│  │  misc.xml
│  │  modules.xml
│  │  workspace.xml
│  │  
│  └─inspectionProfiles
│          profiles_settings.xml
│          Project_Default.xml
│          
├─face_dataset    人脸数据库，同时也是接收web端upload的图片
│      obama_1.jpg
│      刘媛媛_1.jpg
│      张学友_1.jpg
│      
├─logs  训练后数据存放
│      last_one.h5
│      README.md
│      
├─model_data
│      classes.txt  ---用于mobilenet检测的标签
│      facenet_mobilenet.h5   ---facenet网络   预训练权重
│      inception_resnetv1_face_encoding.npy ---以resnet为骨干的模型
│      inception_resnetv1_names.npy
│      mobilenet_face_encoding.npy  ---以mobilenet为骨干的模型 数据库人脸编码生成的.npy
│      mobilenet_names.npy          ---对应的人名标签.npy
│      onet.h5   ---mtcnn网络
│      pnet.h5
│      rnet.h5
│      retinaface_mobilenet025.h5  ---retinaface网络   预训练权重
│      simhei.ttf
│      
├─net  口罩检测所用网络
│  │  mobilenet.py
│  │  mtcnn.py
│  │  
│  └─__pycache__
│          mobilenet.cpython-37.pyc
│          mtcnn.cpython-37.pyc
│          
├─nets
│  │  facenet.py  --facenet网络模型构建
│  │  inception_resnetv1.py
│  │  mobilenet.py  -主干特征提取
│  │  
│  └─__pycache__
│          facenet.cpython-37.pyc
│          inception_resnetv1.cpython-37.pyc
│          mobilenet.cpython-37.pyc
│          
├─nets_retinaface
│  │  mobilenet.py   -主干特征提取
│  │  resnet.py
│  │  retinaface.py --retinaface网络模型构建
│  │  
│  └─__pycache__
│          mobilenet.cpython-37.pyc
│          resnet.cpython-37.pyc
│          retinaface.cpython-37.pyc
│          
├─radio   播放音频
│      play.py
│      slogan.mp3
│      slogan_short.mp3
│      tts.py
│      
├─UI     tkinterUI界面图
│  └─img
│          12.png
│          SSPU_2.png
│          
├─utils
│  │  anchors.py  先验框计算获取
│  │  config.py    参数配置
│  │  file_processing.py  文件格式处理
│  │  image_processing.py  图片格式处理
│  │  m_utils.py  口罩检测中使用的人脸图像处理
│  │  utils.py    人脸识别中使用的人脸对齐矫正，框处理等
│  │  
│  └─__pycache__
│          anchors.cpython-37.pyc
│          config.cpython-37.pyc
│          file_processing.cpython-37.pyc
│          image_processing.cpython-37.pyc
│          m_utils.cpython-37.pyc
│          utils.cpython-37.pyc
│
├─Htai -----web端
│  │  ex.py （没啥用只是我用来测试）
│  │  manage.py 主要运行 main
│  │
│  ├─.idea
│  │  │  .gitignore
│  │  │  Htai.iml
│  │  │  misc.xml
│  │  │  modules.xml
│  │  │  workspace.xml
│  │  │
│  │  └─inspectionProfiles
│  │          profiles_settings.xml
│  │          Project_Default.xml
│  │
│  ├─App
│  │  │  models.py 模型类声明
│  │  │  user_views.py 蓝图路由配置
│  │  │  __init__.py
│  │  │
│  │  └─__pycache__
│  │          models.cpython-36.pyc
│  │          models.cpython-37.pyc
│  │          user_views.cpython-36.pyc
│  │          user_views.cpython-37.pyc
│  │          __init__.cpython-36.pyc
│  │          __init__.cpython-37.pyc
│  │
│  ├─static  导入的css,js包
│  │  │  echarts.js
│  │  │
│  │  ├─css
│  │  │      base.css
│  │  │      component.css
│  │  │      css.css
│  │  │      dateIco.png
│  │  │      hack.css
│  │  │      haiersoft.css
│  │  │      manhuaDate.1.0.css
│  │  │      page.css
│  │  │      page1.css
│  │  │      print.css
│  │  │      public.css
│  │  │      reset.css
│  │  │
│  │  ├─img 前端小图标
│  │  │      coin01.png
│  │  │      coin02.png
│  │  │      coin03.png
│  │  │      coin04.png
│  │  │      coin07.png
│  │  │      coin08.png
│  │  │      coin09.png
│  │  │      coin10.png
│  │  │      coin11.png
│  │  │      coin111.png
│  │  │      coin12.png
│  │  │      coin13.png
│  │  │      coin14.png
│  │  │      coin15.png
│  │  │      coin16.png
│  │  │      coin17.png
│  │  │      coin18.png
│  │  │      coin19.png
│  │  │      coin20.png
│  │  │      coin21.png
│  │  │      coin222.png
│  │  │      coinL1.png
│  │  │      coinL2.png
│  │  │      delete.png
│  │  │      logBanner.png
│  │  │      logLOGO.png
│  │  │      logName.png
│  │  │      logPwd.png
│  │  │      logYZM.png
│  │  │      no.png
│  │  │      ok.png
│  │  │      shanchu.png
│  │  │      topic.png
│  │  │      update.png
│  │  │
│  │  ├─js
│  │  │      ajaxfileupload.js
│  │  │      classie.js
│  │  │      jquery-1.10.1.min.js
│  │  │      jquery-1.7.2.min.js
│  │  │      jquery-3.2.1.min.js
│  │  │      jquery.min.js
│  │  │      jquery.mousewheel.js
│  │  │      manhuaDate.1.0.js
│  │  │      modernizr.custom.js
│  │  │      page.js
│  │  │      popwin.js
│  │  │      public.js
│  │  │      rollover.js
│  │  │      scroll.js
│  │  │      select.js
│  │  │      side.js
│  │  │
│  │  └─layui
│  │      │  layui.js
│  │      │
│  │      ├─css
│  │      │  │  layui.css
│  │      │  │
│  │      │  └─modules
│  │      │      │  code.css
│  │      │      │
│  │      │      ├─laydate
│  │      │      │  └─default
│  │      │      │          laydate.css
│  │      │      │
│  │      │      └─layer
│  │      │          └─default
│  │      │                  icon-ext.png
│  │      │                  icon.png
│  │      │                  layer.css
│  │      │                  loading-0.gif
│  │      │                  loading-1.gif
│  │      │                  loading-2.gif
│  │      │
│  │      └─font
│  │              iconfont.eot
│  │              iconfont.svg
│  │              iconfont.ttf
│  │              iconfont.woff
│  │              iconfont.woff2
│  │
│  ├─templates  前端html界面
│  │      adduser.html
│  │      add_student.html
│  │      add_user_per.html
│  │      changepwd.html
│  │      changepwdsu.html
│  │      entry_list.html
│  │      ex.html
│  │      grade.html
│  │      hi.html
│  │      index.html
│  │      login.html
│  │      main.html
│  │      register.html
│  │      student.html
│  │      student_list.html
│  │      total.html
│  │      users.html
│  │      user_per_list.html
│  │
│  ├─utils
│  │  │  ch_login.py 每个页面前的登录要求
│  │  │  functions.py 连接mysql数据库等配置
│  │  │
│  │  │
│  │  └─__pycache__
│  │          ch_login.cpython-36.pyc
│  │          ch_login.cpython-37.pyc
│  │          functions.cpython-36.pyc
│  │          functions.cpython-37.pyc
│  │
│  └─__pycache__
│          ex.cpython-37.pyc
│          manage.cpython-37.pyc
└─__pycache__
        mask_recognize.cpython-37.pyc
        retinaface.cpython-37.pyc

(为完成本科毕设而将网上各种源码杂糅的产物)
人脸识别和口罩识别主要部分代码来自https://github.com/bubbliiiing