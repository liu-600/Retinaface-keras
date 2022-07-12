import os

from flask import Blueprint, redirect, render_template, request, url_for, session, flash, jsonify
from sqlalchemy import desc
from werkzeug.utils import secure_filename

from Htai.App.models import db, User, Student, Entry

from Htai.utils.ch_login import is_login

ALLOWED_EXTENSIONS = set(['jpg','jpeg']) #限制上传文件格式
user_blueprint = Blueprint('user', __name__)

@user_blueprint.route('/ex', methods=['GET', 'POST'])
def ex():
    return render_template('ex.html')

@user_blueprint.route('/create_db/')
def create_db():
    """
    创建数据
    """
    db.create_all()
    return '创建成功'


@user_blueprint.route('/drop_db/')
def drop_db():
    """
    删除数据库
    """
    db.drop_all()
    return '删除成功'


@user_blueprint.route('/home/', methods=['GET'])
@is_login
def home():
    """
    首页
    """
    if request.method == 'GET':
        user = session.get('username')
        return render_template('index.html', user=user)


@user_blueprint.route('/head/', methods=['GET'])
@is_login
def head():
    """
    页头
    """
    if request.method == 'GET':
        user = session.get('username')
        return render_template('head.html', user=user)


@user_blueprint.route('/left/', methods=['GET'])
def left():
    """左侧栏"""
    if request.method == 'GET':
        # 获取登录的用户信息
        user = session.get('username')
        # 获取用户的权限
        permissions = User.query.filter_by(username=user).first()
        # print("permissions",permissions)
        # return render_template('left.html', permissions=permissions)
        return render_template('left.html')


@user_blueprint.route('/register/', methods=['GET', 'POST'])
def register():
    """
    用户注册页面
    """
    if request.method == 'GET':
        return render_template('register.html')

    if request.method == 'POST':
        # 获取用户填写的信息
        username = request.form.get('username')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')

        # 定义个变量来控制过滤用户填写的信息
        flag = True
        # 判断用户是否信息都填写了.(all()函数可以判断用户填写的字段是否有空)
        if not all([username, pwd1, pwd2]):
            msg, flag = '* 请填写完整信息', False
        # 判断用户名是长度是否大于16
        if len(username) > 16:
            msg, flag = '* 用户名太长', False
        # 判断两次填写的密码是否一致
        if pwd1 != pwd2:
            msg, flag = '* 两次密码不一致', False
        # 如果上面的检查有任意一项没有通过就返回注册页面,并提示响应的信息
        if not flag:
            return render_template('register.html', msg=msg)
        # 核对输入的用户是否已经被注册了
        u = User.query.filter(User.username == username).first()
        # 判断用户名是否已经存在
        if u:
            msg = '用户名已经存在'
            return render_template('register.html', msg=msg)
        # 上面的验证全部通过后就开始创建新用户
        user = User(username=username, password=pwd1)
        # 保存注册的用户
        user.save()
        # 跳转到登录页面
        return redirect(url_for('user.login'))


@user_blueprint.route('/login/', methods=['GET', 'POST'])
def login():
    """
    登录
    """
    if request.method == 'GET':
        return render_template('login.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        # 判断用户名和密码是否填写
        if not all([username, password]):
            msg = '* 请填写好完整的信息'
            return render_template('login.html', msg=msg)
        # 核对用户名和密码是否一致
        user = User.query.filter_by(username=username, password=password).first()
        # 如果用户名和密码一致
        if user:
            # 向session中写入相应的数据
            session['user_id'] = user.u_id
            session['username'] = user.username
            return render_template('index.html')
        # 如果用户名和密码不一致返回登录页面,并给提示信息
        else:
            msg = '* 用户名或者密码不一致'
            return render_template('login.html', msg=msg)


@user_blueprint.route('/logout/', methods=['GET'])
def logout():
    """
    退出登录
    """
    if request.method == 'GET':
        # 清空session
        session.clear()
        # 跳转到登录页面
        return redirect(url_for('user.login'))


#展示界面
@user_blueprint.route('/student/', methods=['GET', 'POST'])
@is_login
def student():
    """学生信息列表"""
    if request.method == 'GET':
        return render_template('student_list.html')


#获得数据
@user_blueprint.route('/get_student_list/', methods=['GET', 'POST'])
@is_login
def student_list():
    """学生信息列表"""
    if request.method == 'GET':
        page = int(request.args.get('page',1))
        page_num = int(request.args.get('page_num',20))
        paginate = Student.query.order_by('s_id').paginate(page,page_num)
        stus = paginate.items

        list=[]
        for item in stus:
            list.append(dict(item))
        print("list",list)
        #return render_template('student_list.html', stus=stus,paginate=paginate)
        data = {"code": 0, "msg": "", "count": page_num, "data":list}
        print("data",data)
        return jsonify(data)

#展示界面
@user_blueprint.route('/entry/', methods=['GET', 'POST'])
@is_login
def entry():
    """学生信息列表"""
    if request.method == 'GET':
        return render_template('entry_list.html')


#获得数据
@user_blueprint.route('/get_entry_list/', methods=['GET', 'POST'])
@is_login
def entry_list():
    """学生信息列表"""
    if request.method == 'GET':
        page = int(request.args.get('page',1))
        page_num = int(request.args.get('page_num',100))
        paginate = Entry.query.order_by(desc('e_id')).paginate(page,page_num)
        stus = paginate.items

        list=[]
        for item in stus:
            list.append(dict(item))
        print("list",list)
        #return render_template('student_list.html', stus=stus,paginate=paginate)
        data = {"code": 0, "msg": "", "count": page_num, "data":list}
        print("data",data)
        return jsonify(data)


@user_blueprint.route('/addstu/', methods=['GET', 'POST'])
@is_login
def add_stu():
    """添加学生"""
    if request.method == 'GET':
        #grades = Grade.query.all()
        return render_template('add_student.html')

    if request.method == 'POST':
        #拿到上一个居民的last_id  ,下一个id递增+1
        stu = Student.query.order_by(desc('s_id')).first()
        last_id = stu.s_id
        s_id = last_id+1
        s_name = request.form.get('s_name')
        s_sex = request.form.get('s_sex')
        s_phone = request.form.get('s_phone')
        s_address = request.form.get('s_address')
        print("form_name",s_name)
        stu = Student.query.filter(Student.s_name == s_name).count()
        if stu:
            msg = '* 居民姓名不能重复'

            print("姓名重复")
            #grades = Grade.query.all()
            return render_template('add_student.html', msg=msg)
        stu = Student(s_id = s_id,s_name=s_name, s_sex=s_sex,s_phone=s_phone,s_address=s_address)
        stu.save()

        return redirect(url_for('user.student'))

@user_blueprint.route('/addentry/', methods=['GET', 'POST'])
@is_login
def add_entry():
    """添加学生"""
    if request.method == 'GET':
        #grades = Grade.query.all()
        return render_template('add_student.html')

    if request.method == 'POST':
        e_name = request.form.get('e_name')
        #e_status = request.form.get('e_status')
        e_date = request.form.get('e_date')
        print("form_name",e_name)
        count = Student.query.filter(Entry.e_name == e_name).count()
        if count %2==0: #偶数，这次是出
            print("出")
            e_status="出"
        else:
            e_status="入"
        stu = Entry(e_name=e_name, e_status=e_status,e_date=e_date)
        stu.save()

        return redirect(url_for('user.entry'))



@user_blueprint.route('/userlist/', methods=['GET', 'POST'])
@is_login
def user_list():
    """用户信息列表"""
    if request.method == 'GET':
        page = int(request.args.get('page',1))
        page_num = int(request.args.get('page_num',5))
        paginate = User.query.order_by('u_id').paginate(page,page_num)
        users = paginate.items
        return render_template('users.html', users=users,paginate=paginate)


@user_blueprint.route('/adduser/', methods=['GET', 'POST'])
@is_login
def add_user():
    """添加用户信息"""
    if request.method == 'GET':
        return render_template('adduser.html')

    if request.method == 'POST':
        username = request.form.get('username')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        flag = True
        if not all([username, password1, password2]):
            msg, flag = '请填写完整信息', False
        if len(username) > 16:
            msg, flag = '用户名太长', False
        if password1 != password2:
            msg, flag = '两次密码不一致', False
        if not flag:
            return render_template('adduser.html', msg=msg)
        user = User(username=username, password=password1)
        user.save()
        return redirect(url_for('user.user_list'))




@user_blueprint.route('/changepwd/', methods=['GET', 'POST'])
@is_login
def change_password():
    """修改用户密码"""
    if request.method == 'GET':
        username = session.get('username')
        user = User.query.filter_by(username=username).first()
        return render_template('changepwd.html', user=user)

    if request.method == 'POST':
        username = session.get('username')
        pwd1 = request.form.get('pwd1')
        pwd2 = request.form.get('pwd2')
        pwd3 = request.form.get('pwd3')

        pwd = User.query.filter(User.password == pwd1, User.username == username).first()
        if not pwd:
            msg = '请输入正确的旧密码'
            username = session.get('username')
            user = User.query.filter_by(username=username).first()
            return render_template('changepwd.html', msg=msg, user=user)
        else:
            if not all([pwd2, pwd3]):
                msg = '密码不能为空'
                username = session.get('username')
                user = User.query.filter_by(username=username).first()
                return render_template('changepwd.html', msg=msg, user=user)
            if pwd2 != pwd3:
                msg = '两次密码不一致,请重新输入'
                username = session.get('username')
                user = User.query.filter_by(username=username).first()
                return render_template('changepwd.html', msg=msg, user=user)
            pwd.password = pwd2
            db.session.commit()
            return redirect(url_for('user.change_pass_sucess'))


@user_blueprint.route('/changepwdsu/', methods=['GET'])
@is_login
def change_pass_sucess():
    """修改密码成功后"""
    if request.method == 'GET':
        return render_template('changepwdsu.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@user_blueprint.route('/upload/', methods=['GET', 'POST'])
@is_login
def upload():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("file",file)
            filename = file.filename
            print("file_name", filename)
            from Htai.manage import app
            print("path", app.config['UPLOAD_FOLDER'])

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return  '{"filename":"%s"}' % filename
    return ''

@user_blueprint.route('/total/', methods=['GET'])
@is_login
def total():
    """修改密码成功后"""
    if request.method == 'GET':
        return render_template('total.html')