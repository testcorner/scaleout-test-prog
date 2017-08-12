import subprocess
import sys
import os
import re

from subprocess import check_output, CalledProcessError

def application(env, start_response):
    start_response('200 OK', [('Content-Type', 'text/html')])
    out = split_lines(subprocess.check_output(['adb', 'devices']))
    adb_cmd = ['adb']
    
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
	
	devices.append("<td>")
	info = line.split('\t')
	devices.append(info[0])
	devices.append("</td>")

	devices.append("<td>")
	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'getprop ro.product.model'])
	adb_output = subprocess.check_output(adb_cmd)
	devices.append(adb_output)
	devices.append("</td>")
	
	devices.append("<td>")
	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'getprop ro.product.cpu.abi'])
	adb_output = subprocess.check_output(adb_cmd)
	devices.append(adb_output)
	devices.append("</td>")
	
	devices.append("<td>")
	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'getprop ro.sf.lcd_density'])
	adb_output = subprocess.check_output(adb_cmd)
    	devices.append(adb_output)
	devices.append("</td>")

	devices.append("<td>")
	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'wm size'])
	adb_output = subprocess.check_output(adb_cmd)
    	devices.append(adb_output)
	devices.append("</td>")
	
	devices.append("<td>")
	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'getprop ro.build.version.release'])
	adb_output = subprocess.check_output(adb_cmd)
	devices.append("Android ")
    	devices.append(adb_output)
	devices.append("</td>")
	
	devices.append("<td>")	
 	adb_cmd = ['adb']
	adb_cmd.extend(['-s' , info[0]])
	adb_cmd.extend(['shell' , 'getprop ro.build.version.sdk'])
	adb_output = subprocess.check_output(adb_cmd)
	devices.append("API ")
    	devices.append(adb_output)
	devices.append("</td>")
	
	devices.append("</tr>")
	adb_cmd = ['adb']
    devices.append("<table>")
    ret = ''.join(devices)
    return[ret]

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
  
