from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename
from app import app
from app.handler.hd_user import require
from app.handler.tasks import *
from app.utils.legal import allowed_upload_filename
from flask import render_template, request, jsonify

from MagicCube.main_flask import return_data


@app.route('/')
@app.route('/index')
@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/FlaskTutorial', methods=['POST'])
@require('pass')
def success():
    if request.method == 'POST':
        # logAfter.delay(123)
        repeatLogging.delay("success", 5)
        email = request.form['email']
        return render_template('success.html', email=email)
    else:
        pass


@app.route('/task', methods=['POST'])
def newtask():
    task = askForResult.delay()


@app.route('/pic', methods=['POST'])
def pic_upload():
    file = request.files['img']  # type: FileStorage
    if allowed_upload_filename(file.filename):
        # save the pic and excute the recognition (in celery task)

        # {FileStorage} is not JSON serializable
        # task = save_pic_recog_pic.delay(file)
        filename = secure_filename(file.filename)
        fullname = os.path.join(app_path, 'pictures', filename)
        file.save(fullname)

        task = recognize.delay(fullname)
        print(task.result)
        return 'start excuting'
    else:
        return 'illegal filename'


@app.route('/ask', methods=['POST'])
def ask_rubiks():
    return jsonify(return_data())


@app.route('/refresh', methods=['POST'])
def refresh_rubiks():
    task = refresh_cube.delay()
    return "refresh success"