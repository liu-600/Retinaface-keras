#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 前端库
import tkinter
from tkinter import *
from tkinter import ttk
import cv2 as cv
import keras
import pymysql
from PIL import Image, ImageTk
import os
from tkinter.simpledialog import askstring
# 后端库
import cv2
import numpy as np

from mask_recognize import mask_rec
from retinaface import Retinaface
from utils import file_processing, image_processing
import winsound
from playsound import playsound
import copy
import time
from tkinter.messagebox import askquestion, showinfo
import threading

# 后端申明
resize_width = 160
resize_height = 160
# 存放facenet预训练模型的路径
model_path = 'models/20180408-102900'
# 存放人脸特征数据库的路径
npy_dataset_path = 'dataset/emb/faceEmbedding.npy'
filename = 'dataset/emb/name.txt'
# 加载retinaface




# 前端声明
camera_switch = False
# mask_detc_switch = False
count = 1

# 临时变量
tempimagepath = r"face_dataset\\"

# 摄像机设置
# 0是代表摄像头编号，只有一个的话默认为0
capture = cv.VideoCapture(0)


def getframe():
    ref, frame = capture.read()
    cv.imwrite(tempimagepath, frame)


def closecamera():
    capture.release()


# 界面相关
window_width = 1050
window_height = 578
image_width = int(window_width * 0.5)  # 画布的大小
image_height = int(window_height * 0.6)
imagepos_x = int(window_width * 0.01)  # 画布的坐标
imagepos_y = int(window_height * 0.02)
but1pos_x = 50  # 拍照按钮坐标
but1pos_y = 380
top = Tk()
top.wm_title("智能防疫系统")
top.geometry(str(window_width) + 'x' + str(window_height))
top.resizable(0, 0)


# 线程
def thread_it(func, *args):
    # 创建线程
    t = threading.Thread(target=func, args=args)
    # 守护
    t.setDaemon(True)
    # 启动
    t.start()





def tkImage(isFrame):
    """
    对摄像头发回的照片进行处理并返回，同时将原生照片返回
    """
    ref, frame = capture.read() #实时
    frame = cv.flip(frame, 1)  # 翻转 0:上下颠倒 大于0水平颠倒
    if isFrame is True:
        return frame
    else:
        cvimage = cv.cvtColor(frame, cv.COLOR_BGR2RGBA)
        pilImage1 = Image.fromarray(cvimage)
        # 第一个参数为指定宽和高的元组，第二个参数指定过滤器类型NEAREST、BILINER、BICUBIC、ANTALIAS，其中ANTALIAS为最高品质。
        pilImage2 = pilImage1.resize((image_width, image_height), Image.ANTIALIAS)
        tkImage = ImageTk.PhotoImage(image=pilImage2)
        return tkImage


# 开启和关闭摄像头
def button1():
    global camera_switch
    global count
    camera_switch = bool(1 - camera_switch)  # 摄像头开关
    while True:
        if camera_switch is False:
            closecamera()
            bg_image1 = Image.open(r"UI\img\12.png")
            bg_image2 = bg_image1.resize((image_width, image_height), Image.ANTIALIAS)
            bg_im = ImageTk.PhotoImage(bg_image2)
            canvas.create_image(0, 0, anchor='nw', image=bg_im)  # 显示背景
        else:
            if capture.isOpened() is False:  # 判断摄像头是否处于开启状态
                capture.open(0)
            picture = tkImage(isFrame=False)
            canvas.create_image(0, 0, anchor='nw', image=picture)
        top.update()  # 显示图片后面加上这两句
        top.after(100)


# 拍照
def button2():
    ref, frame = capture.read()
    name = askstring(title="输入姓名", prompt="请输入姓名_1")
    path = tempimagepath + name + ".jpg"
    print(path)
    print(cv.imencode('.jpg', frame)[1].tofile(path))


# 签到-人脸识别
def button3():
    keras.backend.clear_session()

    retinaface = Retinaface()
    while True:  # 摄像头照片实时处理

        fps = 0.0
        while (True):
            t1 = time.time()
            draw = tkImage(True)
            frame = copy.deepcopy(draw)

            # 读取某一帧

            # 格式转变，BGRtoRGB
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # 进行检测
            old=[]
            pred_name=[]
            old,pred_name = retinaface.detect_image(frame)  #人脸框，名字已画完
            old = np.array(old)
            print("pre_name",pred_name)

            if pred_name!=None and pred_name[0]!='Unknown':

        ###存入数据库
                connection = pymysql.connect(host='localhost', user='root', password='1234', db='htai')
                cursor = connection.cursor()
                c = cursor.execute('select * FROM entry ORDER BY e_id DESC LIMIT 1')
                list_re = cursor.fetchall()
                e_id = list_re[0][0] + 1
                c = cursor.execute('select * from entry where e_name=("%s")' % (str(pred_name[0])))
                print("c=", c)
                if c==0:
                    e_status = "入"
                    cursor.execute(
                        'insert into entry(e_id,e_name,e_status,e_date,e_time,e_day) values ("%d","%s","%s","%s","%s","%d")' % (
                        e_id,
                        str(pred_name[0]), e_status, str(time.strftime("%Y-%m-%d", time.localtime())),
                        str(time.strftime("%H:%M:%S", time.localtime())), now_time))
                    last = len(treeview.get_children())
                    treeview.insert('', last + 1,
                                    values=(str(last + 1), str(pred_name[0]),
                                            time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))  # 将名字加入签到表格
                    winsound.Beep(600, 100)  # 蜂鸣
                    frame = Image.open(  # 显示人脸库中图片，给用户及时的反馈
                        r"face_dataset\\" +
                        str(pred_name[0]) + "_1.jpg")
                    bg_image = frame.resize((image_width, image_height), Image.ANTIALIAS)
                    bg_im = ImageTk.PhotoImage(bg_image)
                    time1 = time.time()
                    count = 200
                    while count != 0:
                        count = count - 1
                        canvas.create_image(0, 0, anchor='nw', image=bg_im)  # 显示背景
                    tkinter.messagebox.showinfo('提示', '人脸识别通过')
                else:
                    if c % 2 == 0:  # 偶数 现在是出
                        e_status = "出"
                    else:
                        e_status = "入"
                # 在30秒内同一人不再录入----以此避免重复记录出入信息
                    c = cursor.execute('select * from entry where e_name="%s" order by e_id desc limit 1' % (str(pred_name[0])))
                    list_re = cursor.fetchall()
                    print("list_re:",list_re)
                    last_time = list_re[0][5]
                    print("day", last_time)
                    now_time = time.localtime().tm_hour * 3600 + time.localtime().tm_min * 60 + time.localtime().tm_sec
                    if abs(now_time - last_time) > 30: #绝对值
                        cursor.execute(
                            'insert into entry(e_id,e_name,e_status,e_date,e_time,e_day) values ("%d","%s","%s","%s","%s","%d")' % (e_id,
                                str(pred_name[0]), e_status, str(time.strftime("%Y-%m-%d", time.localtime())),
                                str(time.strftime("%H:%M:%S", time.localtime())), now_time))
                        last = len(treeview.get_children())
                        treeview.insert('', last + 1,
                                        values=(str(last + 1), str(pred_name[0]),
                                                time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))  # 将名字加入签到表格
                        winsound.Beep(600, 100)  # 蜂鸣
                        frame = Image.open(  # 显示人脸库中图片
                            r"face_dataset\\" +
                            str(pred_name[0]) + "_1.jpg")
                        bg_image = frame.resize((image_width, image_height), Image.ANTIALIAS)
                        bg_im = ImageTk.PhotoImage(bg_image)
                        time1 = time.time()
                        count = 200
                        while count != 0:
                            count = count - 1
                            canvas.create_image(0, 0, anchor='nw', image=bg_im)  # 显示背景
                        tkinter.messagebox.showinfo('提示', '人脸识别通过')

                # 提交并关闭
                connection.commit()
                connection.close()

     #都要进行的部分：转格式-画fps-转格式-裁剪-放tkinter上-更新
            old = cv2.cvtColor(old, cv2.COLOR_RGB2BGR)
            # 画上fps
            fps = (fps + (1. / (time.time() - t1))) / 2
            print("fps= %.2f" % (fps))
            old = cv2.putText(old, "fps= %.2f" % (fps), (0, 40), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

            # 人脸显示
            cvimage = cv.cvtColor(old, cv.COLOR_BGR2RGBA)

            pilImage = Image.fromarray(cvimage)
            # 第一个参数为指定宽和高的元组，第二个参数指定过滤器类型NEAREST、BILINER、BICUBIC、ANTALIAS，其中ANTALIAS为最高品质。
            pilImage = pilImage.resize((image_width, image_height), Image.ANTIALIAS)
            picture = ImageTk.PhotoImage(image=pilImage)
            canvas.create_image(0, 0, anchor='nw', image=picture)
            top.update()  # 显示图片后面加上这两句

            c = cv2.waitKey(1) & 0xff
            if c == 27:
                capture.release()
                break


# 建立人脸数据库--在对人脸图片库建立人脸数据库
def button4():
    # success = create_face_embedding(model_path, dataset_path, out_emb_path, out_filename)
    # if len(success) >= 0:
    #     showinfo("提示", "特征库已经制作完毕")
    keras.backend.clear_session()

    retinaface = Retinaface(1)

    list_dir = os.listdir("face_dataset")
    image_paths = []
    names = []
    for name in list_dir:
        image_paths.append("face_dataset/" + name)
        names.append(name.split("_")[0])

    retinaface.encode_face_dataset(image_paths, names)
    showinfo("提示", "特征库已经制作完毕")
#口罩检测
def button6():
    keras.backend.clear_session()

    dududu = mask_rec()
    while True:  # 摄像头照片实时处理

        draw = tkImage(True)
        frame = copy.deepcopy(draw)

        nframe = dududu.recognize(frame)
        # 人脸显示
        if nframe is None:
            nframe = frame
            print("没有返回图---即佩戴口罩") # 一般没有返回图都是因为佩戴口罩，所以假装是佩戴了口罩就不画框，不提醒
        cvimage = cv.cvtColor(nframe, cv.COLOR_BGR2RGBA)

        pilImage = Image.fromarray(cvimage)
        # 第一个参数为指定宽和高的元组，第二个参数指定过滤器类型NEAREST、BILINER、BICUBIC、ANTALIAS，其中ANTALIAS为最高品质。
        pilImage = pilImage.resize((image_width, image_height), Image.ANTIALIAS)
        picture = ImageTk.PhotoImage(image=pilImage)
        canvas.create_image(0, 0, anchor='nw', image=picture)
        top.update()  # 显示图片后面加上这两句




# 清空所有条目
def button5(tree):
    # 误删除
    a1 = askquestion(title="删除所有！", message="是否删除所有？")
    print(a1)
    if a1 == "yes":
        x = tree.get_children()
        for item in x:
            tree.delete(item)
    else:
        pass


# 删除单条
def delitrem(event):
    item = treeview.selection()
    a1 = askquestion(title="删除！", message="确定删除？")
    if a1 == "yes":
        print(treeview.item(item, "value"))
        print(treeview.get_children())
        treeview.delete(item)
    else:
        pass


# 控件定义
canvas = Canvas(top, bg='white', width=image_width, height=image_height)  # 绘制画布
bg_image1 = Image.open(r"UI\img\12.png")
bg_image2 = bg_image1.resize((image_width, image_height), Image.ANTIALIAS)
bg_im = ImageTk.PhotoImage(bg_image2)
canvas.create_image(0, 0, anchor='nw', image=bg_im)  # 显示背景
b1 = Button(top, text='打开/关闭摄像头', width=15, height=2, command=button1)
b2 = Button(top, text="拍照", width=15, height=2, command=button2)
b3 = Button(top, text="人脸识别", width=15, height=2, command=lambda: thread_it(button3))
b4 = Button(top, text="建立人脸特征库", width=15, height=2, command=lambda: thread_it(button4))
b5 = Button(top, text="删除所有", width=10, height=1, command=lambda: button5(treeview))
b6 = Button(top, text="口罩检测", width=15, height=2, command=lambda: thread_it(button6))
# 控件位置设置
canvas.place(x=imagepos_x, y=imagepos_y)
b1.place(x=but1pos_x - 40, y=but1pos_y)
b2.place(x=but1pos_x + 110, y=but1pos_y)
b3.place(x=but1pos_x + 260, y=but1pos_y)
b4.place(x=but1pos_x - 40, y=but1pos_y + 70)
b5.place(x=but1pos_x + 877, y=but1pos_y + 190)
b6.place(x=but1pos_x + 110, y=but1pos_y + 70)
# p6.place(x=but1pos_x + 110, y=but1pos_y+70)识别出的照片
'''
frame = Image.open(r"UI\img\12.png")
bg_image = frame.resize((image_width, image_height), Image.ANTIALIAS)
bg_im = ImageTk.PhotoImage(bg_image)
canvas.create_image(but1pos_x + 110, but1pos_y + 70, anchor='nw', image=bg_im)
'''

# ######################签到信息显示######################
columns = ("序号", "姓名", "出入时间")
treeview = ttk.Treeview(top, height=18, show="headings", columns=columns)  # 表格
# y滚动条
vsb = ttk.Scrollbar(top, orient="vertical", command=treeview.yview)
vsb.pack(side='right', fill='y', pady=20)
treeview.configure(yscrollcommand=vsb.set)
treeview.pack(side="right", fill="y")
treeview.place(x=550, y=20, width=450,height=510)

treeview.column("序号", width=70, anchor='center')  # 表示列,不显示
treeview.column("姓名", width=120, anchor='center')
treeview.column("出入时间", width=200, anchor='center')

treeview.heading("序号", text="序号")  # 显示表头
treeview.heading("姓名", text="姓名")
treeview.heading("出入时间", text="出入时间")
# 双击左键删除某一条记录
treeview.bind("<Double-1>", delitrem)


if __name__ == "__main__":
    top.mainloop()
