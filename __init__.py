import subprocess
import sys
import os
import re

from subprocess import check_output, CalledProcessError
from flask import Flask, Response, request, redirect, url_for
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = set(['apk'])

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def split_lines(s):
    """Splits lines in a way that works even on Windows and old devices.
    Windows will see \r\n instead of \n, old devices do the same, old devices
    on Windows will see \r\r\n.
    """
    # rstrip is used here to workaround a difference between splineslines and
    # re.split:
    # >>> 'foo\n'.splitlines()
    # ['foo']
    # >>> re.split(r'\n', 'foo\n')
    # ['foo', '']
    return re.split(r'[\r\n]+', s.rstrip())

@app.route("/")
def hello():
    out = split_lines(subprocess.check_output(['adb', 'devices']))

    devices = []
    devices.append("<table>")
    devices.append("<tr>")
    
    devices.append("<td>")
    devices.append("serialno")
    devices.append("</td>")
    
    devices.append("<td>")
    devices.append("model name")
    devices.append("</td>")

    devices.append("<td>")
    devices.append("cpu")
    devices.append("</td>")

    devices.append("<td>")
    devices.append("density")
    devices.append("</td>")

    devices.append("<td>")
    devices.append("size")
    devices.append("</td>")

    devices.append("<td>")
    devices.append("release")
    devices.append("</td>")

    devices.append("<td>")
    devices.append("sdk")
    devices.append("</td>")

    devices.append("</tr>")
    for line in out[1:]:
        devices.append("<tr>")
        if not line.strip():
            continue
        if 'offline' in line:
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        else:
            devices.append("<td>")
            devices.append(line)
            devices.append("</td>")
        
        devices.append("</tr>")
	adb_cmd = ['adb']
    devices.append("<table>")
    ret = ''.join(devices) 
    return Response(ret)

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # if user does not select file, browser also
        # submit a empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            # after uploads file to change url
            return redirect(url_for('foo'))
    return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <p><input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''

@app.route('/foo')
def foo():
    return 'Hello Foo!'

if __name__ == "__main__":
    app.debug = True
    app.run(host="127.0.0.1")
