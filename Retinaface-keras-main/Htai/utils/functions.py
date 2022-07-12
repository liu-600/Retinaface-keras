import os

import redis
from flask import Flask

from Htai.App.user_views import user_blueprint
from Htai.App.models import db
UPLOAD_FOLDER = r'E:/retinaface-keras-main/face_dataset'  #文件存放路径

def create_app():
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    static_dir = os.path.join(BASE_DIR, 'static')
    templates_dir = os.path.join(BASE_DIR, 'templates')

    app = Flask(__name__,
                static_folder=static_dir,
                template_folder=templates_dir)

    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    #app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

    app.register_blueprint(blueprint=user_blueprint, url_prefix='/user')
    print("连接数据库")
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:1234@127.0.0.1:3306/Htai'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 设置session密钥
    app.config['SECRET_KEY'] = 'secret_key'
    # 设置连接的redis数据库 默认连接到本地6379
    app.config['SESSION_TYPE'] = 'redis'
    # 设置远程
    app.config['SESSION_REDIS'] = redis.Redis(host='127.0.0.1', port=6379)
    print("连接成功")
    db.init_app(app=app)

    return app
