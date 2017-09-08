#!/usr/bin/env python
import subprocess
import sys
import os
import re
import math
import string
import threading
import json
import codecs
import Queue

from subprocess import check_output, CalledProcessError
from flask import Flask, Response, request, redirect, url_for, jsonify
from werkzeug.utils import secure_filename
from time import localtime, strftime
from collections import OrderedDict

host='127.0.0.1'

app = Flask(__name__)

# Global variable to uploads `testing_projects` json file
UPLOAD_TESTING_PROJECT = 'uploads_project_json'
# Global variable to test_result `testing_result`
TESTING_RESULT_PROJECT = 'testing_result'
# Global variable to uploads `testing_projects` apk file
UPLOAD_FOLDER = 'uploads'
APK_FILE_FOLDER = 'apk_file'
APK_TEST_FILE_FOLDER = 'apk_test_file'
ALLOWED_EXTENSIONS_APK = set(['apk'])
ALLOWED_EXTENSIONS_JSON = set(['json'])

# Global variable to uploads `testing_projects` json file
app.config['UPLOAD_TESTING_PROJECT'] = UPLOAD_TESTING_PROJECT
# Global variable to test_result `testing_result`
app.config['TESTING_RESULT_PROJECT'] = TESTING_RESULT_PROJECT
# Global variable to uploads `testing_projects` apk file
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['APK_FILE_FOLDER'] = APK_FILE_FOLDER
app.config['APK_TEST_FILE_FOLDER'] = APK_TEST_FILE_FOLDER

DATA_FORMAT = 'data_format.json'
DEVICES_INFORNATION = 'devices.json'

app.config['DATA_FORMAT'] = DATA_FORMAT
app.config['DEVICES_INFORNATION'] = DEVICES_INFORNATION

devices_information = None

queue = Queue.Queue()
write_JSON_queue = Queue.Queue()

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

def read_JSON(path_filename):
    with open(path_filename) as data_file:
        data = json.load(data_file, object_pairs_hook=OrderedDict)
    return data

def write_JSON(path_filename, data_json):
    with open(path_filename, 'w') as f:
        f.write(json.dumps(data_json))

# Check directory exists
# if is not exists, then can create the <path_dir>
def check_dir_exists(path_dir):
    if not os.path.exists(path_dir):
        os.makedirs(path_dir)

def check_project_exists(path_dir):
    if os.path.exists(path_dir):
        return False
    return True

def check_file_is_file(path_filename):
    if os.path.isfile(path_filename):
        return False
    return True

# Check uploads file format in <ALLOWED_EXTENSIONS_APK>
def allowed_file_apk(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_APK

# Check uploads file format in <ALLOWED_EXTENSIONS_JSON>
def allowed_file_json(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_JSON

# pop not connect device information in devices.json
def remove_device(array_devices_information, devices_serialno):

    array_devices_information.pop(devices_serialno)

    write_JSON(app.config['DEVICES_INFORNATION'], array_devices_information)

# get device data_format devices_info key, return value
def get_device_data(key, devices_serialno, status):
    
    devices_information_data = read_JSON(app.config['DATA_FORMAT'])
    
    if key == "serial_number":
        
        return devices_serialno
    
    elif key == "status":
        
        return status

    if 'offline' in status or 'unauthorized' in status:
        
        return ''
        
    else:

        if key == "display":
            
            # Devices Density
            cmd_adb_get_devices_lcd_density = ['adb']
            cmd_adb_get_devices_lcd_density.extend(['-s' , devices_serialno])
            cmd_adb_get_devices_lcd_density.extend(devices_information_data[key]['command1'])
            cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            try:
                x = float(cmd_adb_get_devices_lcd_density)
            except ValueError:
                cmd_adb_get_devices_lcd_density = ['adb']
                cmd_adb_get_devices_lcd_density.extend(['-s' , devices_serialno])
                cmd_adb_get_devices_lcd_density.extend(devices_information_data[key]['command2'])
                cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            
            return cmd_adb_get_devices_lcd_density
        
        elif key == "size":
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , devices_serialno])
            cmd_adb_get_devices_size.extend(devices_information_data[key]['command'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
            cmd_adb_get_devices_size_split = cmd_adb_get_devices_size.split(': ')
            
            return cmd_adb_get_devices_size_split[1]
        
        elif key == "deviceType":
            
            cmd_adb_get_devices_size = ['adb']
            cmd_adb_get_devices_size.extend(['-s' , devices_serialno])
            cmd_adb_get_devices_size.extend(devices_information_data['size']['command'])
            cmd_adb_get_devices_size = subprocess.check_output(cmd_adb_get_devices_size).strip('\r\n')
            cmd_adb_get_devices_size_split = cmd_adb_get_devices_size.split(': ')
            
            cmd_adb_get_devices_lcd_density = ['adb']
            cmd_adb_get_devices_lcd_density.extend(['-s' , devices_serialno])
            cmd_adb_get_devices_lcd_density.extend(devices_information_data['display']['command1'])
            cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            try:
                x = float(cmd_adb_get_devices_lcd_density)
            except ValueError:
                cmd_adb_get_devices_lcd_density = ['adb']
                cmd_adb_get_devices_lcd_density.extend(['-s' , devices_serialno])
                cmd_adb_get_devices_lcd_density.extend(devices_information_data['display']['command2'])
                cmd_adb_get_devices_lcd_density = subprocess.check_output(cmd_adb_get_devices_lcd_density).strip('\r\n')
            
            devices_size = cmd_adb_get_devices_size_split[1].split('x')
            display_size = math.sqrt(pow(float(devices_size[0])/float(cmd_adb_get_devices_lcd_density),2)+pow(float(devices_size[1])/float(cmd_adb_get_devices_lcd_density),2))
            
            if display_size >= 7:
                return 'Tablet'
            
            else :
                return 'Smartphone'
        else:
            cmd_adb_get_devices_model = ['adb']
            cmd_adb_get_devices_model.extend(['-s' , devices_serialno])
            cmd_adb_get_devices_model.extend(devices_information_data[key]['command'])
            cmd_adb_get_devices_model = subprocess.check_output(cmd_adb_get_devices_model).strip('\r\n')
            
            return cmd_adb_get_devices_model


def get_device_information(array_devices_information, devices_serialno, status):
    
    array_devices_information[devices_serialno] = {}
    
    # read data.json file to get `devices_info` data format
    devices_information_data = read_JSON(app.config['DATA_FORMAT'])
    
    for key in devices_information_data['devices_info']:
        
        array_devices_information[devices_serialno].update({devices_information_data[key]['name'] : get_device_data(key, devices_serialno, status)})

    write_JSON(app.config['DEVICES_INFORNATION'], array_devices_information)


def check_device_information(array_devices_information, devices_serialno, status):
    
    devices_information_data = read_JSON(app.config['DATA_FORMAT'])
    
    if not 'devices' in status:
        get_device_information(array_devices_information, devices_serialno, status)
    else:
        for key in devices_information_data['devices_info']:
            if not array_devices_information[devices_serialno][key] == get_device_data(key, devices_serialno, status):
                get_device_information(array_devices_information, devices_serialno, status)

# Whether to change emulator devices name and information
def check_devices_information(devices_information):
    
    command_adb_devices = split_lines(subprocess.check_output(['adb', 'devices']))
    
    devices_not_in_adbdevice = []
    
    for line in command_adb_devices[1:]:
        if not line.strip():
            continue
        
        if '* daemon not running. starting it now at tcp:5037 *' in line or 'daemon started successfully' in line:
            continue
        
        else:
            info = line.split('\t')
            if info[0] in devices_information:
                # print info[0], True
                if not 'busy' in devices_information[info[0]]['status']:
                    check_device_information(devices_information, info[0], devices_information[info[0]]['status'])
            else:
                # print info[0], False
                get_device_information(devices_information, info[0], info[1])
            
            devices_not_in_adbdevice.extend([info[0]])

    # print devices_information
    for key in devices_information:
        if not key in devices_not_in_adbdevice:
            print key, 'not connect'
            remove_device(devices_information, key)

# This function can check devices.json file isfile and check connect_devices information and status
def check_devices_json_file():
    global devices_information
    if check_file_is_file(app.config['DEVICES_INFORNATION']):
        devices_information = json.loads('{}')
        write_JSON(app.config['DEVICES_INFORNATION'], devices_information)
    devices_information = read_JSON(app.config['DEVICES_INFORNATION'])
    check_devices_information(devices_information)

@app.route('/uploads', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'apk_file' not in request.files:
            
            return redirect(request.url)
        
        if 'apk_test_file' not in request.files:
            
            return redirect(request.url)
        
        test_project_name = request.form.get('test_project_name')
        apk_file = request.files['apk_file']
        apk_test_file = request.files['apk_test_file']
        
        if test_project_name is "" or apk_file.filename == '' or apk_test_file.filename == '':
            return '''
                input 'test_project_name','apk_file','apk_test_file' value.
                '''
        if apk_file and allowed_file_apk(apk_file.filename) and apk_test_file and allowed_file_apk(apk_test_file.filename):
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_FILE_FOLDER> path
            test_project_apk_file_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name, app.config['APK_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_file_folder)
            
            # Get <UPLOAD_FOLDER> / <test_project_name> / <APK_TEST_FILE_FOLDER> path
            test_project_apk_test_file_folder = os.path.join(app.config['UPLOAD_FOLDER'], test_project_name, app.config['APK_TEST_FILE_FOLDER'])
            
            check_dir_exists(test_project_apk_test_file_folder)
            
            # Get upload <apk_file> filename
            apk_file_filename = secure_filename(apk_file.filename)
            # Save upload <apk_file> filename
            apk_file.save(os.path.join(test_project_apk_file_folder, apk_file_filename))
            
            # Get upload <apk_test_file> filename
            apk_test_file_filename = secure_filename(apk_test_file.filename)
            # Save upload <apk_test_file> filename
            apk_test_file.save(os.path.join(test_project_apk_test_file_folder, apk_test_file_filename))
            return '''
                uploads ok!
                '''
    return '''
        input 'test_project_name','apk_file','apk_test_file' value.
        '''

class threadServer(threading.Thread):
    def __init__(self, test_project_name, nowTime, device_name):
        threading.Thread.__init__(self)
        self.pro_name = test_project_name
        self.Time = nowTime
        self.dev_name = device_name
    
    def run(self):
        cmd_get_apk_package_name = ['./testing_project.sh', self.pro_name, self.Time, self.dev_name]
        cmd_testing_output = subprocess.check_output(cmd_get_apk_package_name)
        devices_information[self.dev_name]['status'] = 'device'
        write_JSON_queue.put(thread_change_devices)
        t = thread_change_devices()
        t.start()

class thread_change_devices(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()
    
    def run(self):
        while not write_JSON_queue.empty():
            write_JSON_queue.get()
            write_JSON(app.config['DEVICES_INFORNATION'], devices_information)

class threadArrangement(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.lock = threading.Lock()

    def run(self):
        while not queue.empty():
            project_thread = queue.get()
            devices_serialno = project_thread.dev_name
            if 'device' in devices_information[devices_serialno]['status']:
                devices_information[devices_serialno]['status'] = 'busy'
                project_thread.start()
                write_JSON_queue.put(thread_change_devices)
                t = thread_change_devices()
                t.start()
            else :
                queue.put(project_thread)
                t = thread_change_devices()
                t.start()

# Uploads Json file to testing project
@app.route('/uploads_testing_project', methods=['GET', 'POST'])
def uploads_testing_project():
    if request.method == 'POST':
        count = 0
        # check if the post request has the file part
        if 'testing_project_json' not in request.files:
            return redirect(request.url)
        
        testing_project_json = request.files['testing_project_json']
        
        if testing_project_json.filename == '':
            print testing_project_json.filename
            return '''
                input 'testing_project_json' key and value.
                '''
        if testing_project_json and allowed_file_json(testing_project_json.filename):

            check_dir_exists(app.config['UPLOAD_TESTING_PROJECT'])

            # Get upload <testing_regulation.json> filename
            testing_project_json_filename = secure_filename(testing_project_json.filename)
            
            # Save and <testing_regulation.json> filename to folder <testing_result>
            testing_project_json.save(os.path.join(app.config['UPLOAD_TESTING_PROJECT'], secure_filename(testing_project_json.filename)))
            
            # read <testing_project_json> file
            testing_project_json = read_JSON(os.path.join(app.config['UPLOAD_TESTING_PROJECT'], secure_filename(testing_project_json.filename)))
        
            test_project_name = testing_project_json['project']['project_name']
            
            if check_project_exists(os.path.join(app.config['UPLOAD_FOLDER'], test_project_name)):
                return '''
                    You input project name not exists.
                    '''
            devices_information_format = read_JSON(app.config['DATA_FORMAT'])
            
            check_devices_json_file()
            
            global devices_information
            
            devices_Through_rules = []
            
            for i in devices_information:
                
                # check devices status in devices
                if devices_information[i]['status'] == "offline":
                    continue
                
                check_testing_qualifications = False
                count_testing_qualifications_j = 0
                
                for j in testing_project_json['devices']:
                    for k in xrange(len(testing_project_json['devices'][j])):
                        if testing_project_json['devices'][j][k] == "" or devices_information[i][devices_information_format[j]['name']] == testing_project_json['devices'][j][k]:
                            count_testing_qualifications_j += 1
                            break

                if count_testing_qualifications_j == len(testing_project_json['devices']):
                    check_testing_qualifications = True
                    devices_Through_rules.append(devices_information[i]['serialno'])
            
            # Get current time
            nowTime = strftime('%Y-%m-%d-%H-%M-%S', localtime())
            
            if len(devices_Through_rules) > 0:
                
                for devices_serialno in devices_Through_rules:
                    check_dir_exists(os.path.join(app.config['TESTING_RESULT_PROJECT'], test_project_name, nowTime, devices_serialno))
                    project_thread = threadServer(test_project_name, nowTime, devices_serialno)
                    queue.put(project_thread)

                    count += 1
                t = threadArrangement()
                t.start()

            if count == 0:
                return "Not devices run projects complete."
            #elif count == len(devices_information):
                #return "All projects complete."
            else:
                return "{0} tested. {1} left.".format(count, len(devices_information) - count)

    return '''
        input 'testing_project_json' key and value.
        '''

# get devices status
@app.route('/get_devices_status')
def get_devices_status():
    
    global devices_information
    
    check_devices_json_file()
    
    informations = []
    
    for devices_serialno in devices_information:
        informations.append(devices_serialno)
        informations.append('\t')
        informations.append(devices_information[devices_serialno]['status'])
        informations.append('\n')
                
    ret = ''.join(informations)
    return Response(ret)

# get devices all information
@app.route('/')
def home():
    
    global devices_information
    
    check_devices_json_file()
    
    devices_information_format = read_JSON(app.config['DATA_FORMAT'])

    if len(devices_information) == 0 :
        return '''
            Not connect any devices.
            '''

    response_devices_info = []
    response_devices_info.append("<table>")

    response_devices_info.append("<tr>")
    for data_format in devices_information_format['devices_info']:
        response_devices_info.append("<td>")
        response_devices_info.append(data_format)
        response_devices_info.append("</td>")
    response_devices_info.append("<tr>")
    
    for i in devices_information:
        print i
        response_devices_info.append("<tr>")
        for j in devices_information_format['devices_info']:
            
            response_devices_info.append("<td>")
            response_devices_info.append(devices_information[i][devices_information_format[j]['name']])
            response_devices_info.append("</td>")
        
        response_devices_info.append("</tr>")

    response_devices_info.append("</table>")

    ret = ''.join(response_devices_info)
    return Response(ret)

if __name__ == "__main__":
    app.debug = True
    app.run(host)
