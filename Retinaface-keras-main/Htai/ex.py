from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import os
from flask import send_from_directory
# from werkzeug import SharedDataMiddleware

UPLOAD_FOLDER = '/uploads'  #文件存放路径
ALLOWED_EXTENSIONS = set(['jpeg']) #限制上传文件格式

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/hi', methods=['GET', 'POST'])
def hi():
    return render_template('hi.html')
@app.route('/ex', methods=['GET', 'POST'])
def ex():
    return render_template('ex.html')

@app.route('/test', methods=['GET', 'POST'])
def test():
	f = request.files.get("file")	#获取前端传来的文件
	f.save('./{}'.format(f.filename))	# 将文件保存下来
	return {'flag': True}


@app.route('/upload', methods=['GET', 'POST'])
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
            filename = secure_filename(file.filename)
            print("file_name",filename)
            print("path",app.config['UPLOAD_FOLDER'])
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return  '{"filename":"%s"}' % filename
    return ''

if __name__ == '__main__':
    app.run()