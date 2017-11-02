#!/bin/bash

test_project_name=$1

test_data=$2

test_device_serial_number=$3

# Add aapt to path
for aapt_path in ${ANDROID_HOME}/build-tools/*/; do break; done
export PATH="$PATH:${aapt_path}"

if [ -d "uploads/$test_project_name" ]; then

    #echo "Directory $test_project_name exists."

    app_file=`ls uploads/$test_project_name/apk_file`

    apk_package=`aapt dump badging uploads/$test_project_name/apk_file/$app_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    apk_test_file=`ls uploads/$test_project_name/apk_test_file`

    apk_test_package=`aapt dump badging uploads/$test_project_name/apk_test_file/$apk_test_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    echo `adb -s $test_device_serial_number shell pm uninstall $apk_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/apk_uninstall.log

    echo `adb -s $test_device_serial_number shell pm uninstall $apk_test_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/test_apk_uninstall.log

else

    echo "not have '$test_project_name' project_name."

fi



