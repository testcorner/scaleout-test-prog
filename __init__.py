import subprocess
import sys
import os
import re
import math
import string

from subprocess import check_output, CalledProcessError
from flask import Flask, Response, request, redirect, url_for
from werkzeug.utils import secure_filename

from ftplib import FTP

host='127.0.0.1'

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
def home():
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
    devices.append("API Level")
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
            info = line.split('\t')
            devices.append(info[0])
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_model = ['adb']
            cmd_adb_get_devices_model.extend(['-s' , info[0]])
            cmd_adb_get_devices_model.extend(['shell' , 'getprop ro.product.model'])
            cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model)
            devices.append(cmd_adb_get_devices_model)
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_cpu = ['adb']
            cmd_adb_get_devices_cpu.extend(['-s' , info[0]])
            cmd_adb_get_devices_cpu.extend(['shell' , 'getprop ro.product.cpu.abi'])
            cmd_adb_get_devices_cpu = subprocess.check_output(cmd_adb_get_devices_cpu)
            devices.append(cmd_adb_get_devices_cpu)
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_lcd_density = ['adb']
            cmd_adb_get_devices_lcd_density.extend(['-s' , info[0]])
            cmd_adb_get_devices_lcd_density.extend(['shell' , 'getprop ro.sf.lcd_density'])
            cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density)
            devices.append(cmd_adb_get_devices_lcd_density)
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , info[0]])
            cmd_adb_get_devices_size.extend(['shell' , 'wm size'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size)
            devices_split = cmd_adb_get_devices_size.split(':')
            devices.append(devices_split[1])
            devices.append("</td>")
            
            devices.append("<td>")
            devices_size = devices_split[1].split('x')
            display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
            if display_size >= 7:
                devices.append('Tablet')
            else :
                devices.append('SmartPhone')
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_version_release = ['adb']
            cmd_adb_get_devices_version_release.extend(['-s' , info[0]])
            cmd_adb_get_devices_version_release.extend(['shell' , 'getprop ro.build.version.release'])
            cmd_adb_get_devices_version_release = subprocess.check_output(cmd_adb_get_devices_version_release)
            devices.append("Android ")
            devices.append(cmd_adb_get_devices_version_release)
            devices.append("</td>")
            
            devices.append("<td>")
            cmd_adb_get_devices_api_level = ['adb']
            cmd_adb_get_devices_api_level.extend(['-s' , info[0]])
            cmd_adb_get_devices_api_level.extend(['shell' , 'getprop ro.build.version.sdk'])
            cmd_adb_get_devices_api_level = subprocess.check_output(cmd_adb_get_devices_api_level)
            devices.append("API ")
            devices.append(cmd_adb_get_devices_api_level)
            devices.append("</td>")
        
        devices.append("</tr>")

    devices.append("<table>")
    ret = ''.join(devices) 
    return Response(ret)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    ftp = FTP(host)
    ftp.login('kuo','12345')
    
    if request.method == 'GET':
        test_project_name = request.args.get('test_project_name', '')
        apk_file = request.args.get('apk_file', '')
        apk_test_file = request.args.get('apk_test_file', '')
        
        if (test_project_name is "" or apk_file is "" or apk_test_file is ""):
            return '''
                input 'test_project_name','apk_file','apk_test_file' value.
                '''
        else:
            apk_file_name_array = apk_file.split("/")
            apk_file_name = apk_file_name_array[len(apk_file_name_array)-1]
        
            apk_test_file_array = apk_test_file.split("/")
            apk_test_file_name = apk_test_file_array[len(apk_test_file_array)-1]

            ftp.storbinary("STOR /Users/kuo/Documents/GitHub/yzu/scaleout-test-prog/uploads/" + apk_file_name, open(apk_file, 'rb'))
            ftp.storbinary("STOR /Users/kuo/Documents/GitHub/yzu/scaleout-test-prog/uploads/" + apk_test_file_name, open(apk_test_file, 'rb'))
            ftp.quit()
            get_apk_package_name(test_project_name)
            return '''
                uploads ok!
                '''

def get_apk_package_name(test_project_name):
    cmd_get_apk_file_name = split_lines(subprocess.check_output(['ls' , 'uploads']))
    
    apk_file_name = []
    
    for line in cmd_get_apk_file_name[0:] :
        
        cmd_get_apk_package_name = ['./apk_package.sh', test_project_name, line]
        cmd_aapt_output = subprocess.check_output(cmd_get_apk_package_name)
        apk_file_name.append(cmd_aapt_output)
        apk_file_name.append('<br>')

    ret = ''.join(apk_file_name)

@app.route('/testing_project', methods=['GET', 'POST'])
def testing_project():
    if request.method == 'POST':
        test_project_name = request.form.get('test_project_name')
        cmd_get_apk_package_name = ['./testing_project.sh', test_project_name]
        cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
        return cmd_testing_output

    return '''
        Please re-enter the command
        '''



if __name__ == "__main__":
    app.debug = True
    app.run(host)
