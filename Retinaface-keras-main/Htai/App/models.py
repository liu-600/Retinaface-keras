from datetime import datetime
# 导入SQLAlchemy模块
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# class Grade(db.Model):
#     g_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
#     g_name = db.Column(db.String(20), unique=True)
#     g_create_time = db.Column(db.DateTime, default=datetime.now)
#     students = db.relationship('Student',backref= 'grade')
#
#     __tablename__ = 'grade'
#
#     def __init__(self, name):
#         self.g_name = name
#
#     def save(self):
#         db.session.add(self)
#         db.session.commit()


class Student(db.Model):
    s_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    s_name = db.Column(db.String(16), unique=True)
    s_sex = db.Column(db.String(16))
    s_phone = db.Column(db.String(16))
    s_address = db.Column(db.String(16))
    #grade_id = db.Column(db.Integer, db.ForeignKey('grade.g_id'), nullable=True)

    __tablename__ = 'student'

    def __init__(self, s_id,s_name, s_sex,s_phone,s_address):
        self.s_id = s_id
        self.s_name = s_name
        self.s_sex = s_sex
        self.s_phone= s_phone
        self.s_address = s_address

    def save(self):
        db.session.add(self)
        db.session.commit()
    def keys(self):
        return ('s_id','s_name','s_sex','s_phone','s_address')
    def __getitem__(self, item):
        return getattr(self,item)


class User(db.Model):
    u_id = db.Column(db.Integer, autoincrement=True, primary_key=True) #默认自增
    username = db.Column(db.String(16), unique=True)
    password = db.Column(db.String(250))
    #u_create_time = db.Column(db.DateTime, default=datetime.now)
    #表关系 外键用来关联到另外一张表
    #role_id = db.Column(db.Integer, db.ForeignKey('role.r_id'))

    __tablename__ = 'user'

    def __init__(self,username,password):
        self.username = username
        self.password = password

    def save(self):
        db.session.add(self)
        db.session.commit()


class Entry(db.Model):
    e_id = db.Column(db.Integer, autoincrement=True, primary_key=True) #默认自增
    e_name = db.Column(db.String(16), unique=True)
    e_status= db.Column(db.String(250))
    e_date=db.Column(db.String(250))
    e_time = db.Column(db.String(250))
    e_day = db.Column(db.Integer)
    __tablename__ = 'entry'

    def __init__(self,e_id,e_name,e_status,e_date,e_time,e_day):
        self.e_id = e_id
        self.e_name = e_name
        self.e_status =e_status
        self.e_date = e_date
        self.e_time = e_time
        self.e_day = e_day

    def save(self):
        db.session.add(self)
        db.session.commit()
    def keys(self):
        return ('e_id','e_name','e_status','e_date','e_time','e_day')
    def __getitem__(self, item):
        return getattr(self,item)
