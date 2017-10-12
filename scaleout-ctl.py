#!/usr/bin/env python
import argparse
import os
import subprocess
import json

ALLOWED_EXTENSIONS_APK = set(['apk'])
CONDITIONS_NAME = ['os', 'API Level', 'deviceType', 'display', 'arch']

# check if the apk_file and apk_test_file are in format
def allowed_file_apk(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS_APK

def check_file_exists(path_filename):
    if os.path.isfile(path_filename):
        return False
    return True

def create_json(data, object, key, value):
    if value:
        data[object].update({key: value})
    return data

def main():
    parser = argparse.ArgumentParser(prog='scaleout-ctl.py', usage='python %(prog)s [options] [args]')
    
    # internet address
    parser.add_argument('-addr', '--address', default='127.0.0.1:5000', type=str, help="Host IP address")
    
    # test_project_name
    parser.add_argument('-p', '--project', type=str, help="Test project name")
    
    # apk_file / apke_test_file
    parser.add_argument('-a', '--apk', type=str, help="Application APK")
    parser.add_argument('-t', '--test-apk', type=str, help="Test application APK")
    
    # test_size
    size_group = parser.add_mutually_exclusive_group()
    size_group.add_argument('--small', action='store_true', help="Small test project size")
    size_group.add_argument('--medium', action='store_true', help="Medium test project size")
    size_group.add_argument('--large', action='store_true', help="Large test project size")
    
    # conditions
    parser.add_argument('-os', nargs='+', help="Android release")
    parser.add_argument('-api', nargs='+', help="API Level")
    parser.add_argument('-devicetype', nargs='+', help="Board Specifications")
    parser.add_argument('-display', nargs='+', help="Density")
    parser.add_argument('-arch', nargs='+', help="CPU")
    
    # optional arguments
    parser.add_argument('-s', '--status', action='store_true', help="Show devices status")
    
    args = parser.parse_args()
    
    if args.project:
        CONDITIONS = [args.os, args.api, args.devicetype, args.display, args.arch]
        
        # if apk and test_apk exist then upload
        if args.apk and args.test_apk:
            # check file format
            if not allowed_file_apk(args.apk) or not allowed_file_apk(args.test_apk):
                print "Please make sure the files are in .apk format"
                return
            
            # check file exist
            if check_file_exists(args.apk) or check_file_exists(args.test_apk):
                print "No apk or test_apk file in current folder"
                return
            
            # uploads
            subprocess.call(['curl', '-F', 'test_project_name=' + args.project, '-F', 'apk_file=@' + args.apk, '-F', 'apk_test_file=@' + args.test_apk, '-X', 'POST', args.address + '/uploads'])
            print "APK: " + args.apk, args.test_apk
    
        size = 'default'
    
        data = {}
        data['project'] = {}
        data['devices'] = {}
        
        data = create_json(data, 'project', 'project_name', args.project)
        
        if args.small:
            data = create_json(data, 'project', 'test_size', 'SmallTest')
            size = 'SmallTest'
        
        elif args.medium:
            data = create_json(data, 'project', 'test_size', 'MediumTest')
            size = 'MediumTest'
        
        elif args.large:
            data = create_json(data, 'project', 'test_size', 'LargeTest')
            size = 'LargeTest'
                
        else:
            data = create_json(data, 'project', 'test_size', 'ClassNames')
            size = 'AllTest'
        
        for i in xrange(len(CONDITIONS_NAME)):
            data = create_json(data, 'devices', CONDITIONS_NAME[i], CONDITIONS[i])

        # create testing project json
        with open("testing_project.json", 'w') as outfile:
            json.dump(data, outfile, indent=4)

        conditions = ""

        for key in data['devices']:
            conditions += key + ": " + str(data['devices'][key]) + "\n"
                
        print "Project: " + args.project
        print "Test_size: " + size
        print conditions

        # test
        subprocess.call(['curl', '-F', 'testing_project_json=@testing_project.json', '-X', 'POST', args.address + '/uploads_testing_project'])

        # remove testing project json
        subprocess.call(['rm', 'testing_project.json'])
    
    elif args.status:
        # get sevices status
        subprocess.call(['curl', args.address + '/get_devices_status'])
    
    else:
        # home
        subprocess.call(['curl', args.address])

if __name__ == '__main__':
    main()
