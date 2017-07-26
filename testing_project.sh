#!/bin/bash

test_project_name=$1

test_data=$2

test_device_serial_number=$3

# Add aapt to path
for aapt_path in ${ANDROID_HOME}/build-tools/*/; do break; done
export PATH="$PATH:${aapt_path}"

if [ ! -d "testing_result/$test_project_name" ]; then

    mkdir testing_result/$test_project_name

fi

if [ ! -d "testing_result/$test_project_name/$test_data" ]; then

    mkdir testing_result/$test_project_name/$test_data

fi

if [ ! -d "testing_result/$test_project_name/$test_data/$test_device_serial_number" ]; then

    mkdir testing_result/$test_project_name/$test_data/$test_device_serial_number

fi

if [ -d "uploads/$test_project_name" ]; then

    #echo "Directory $test_project_name exists."

    app_file=`ls uploads/$test_project_name/apk_file`

    apk_package=`aapt dump badging uploads/$test_project_name/apk_file/$app_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    apk_test_file=`ls uploads/$test_project_name/apk_test_file`

    apk_test_package=`aapt dump badging uploads/$test_project_name/apk_test_file/$apk_test_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    # 因為在此無法立即回應，所以我們先將我們的結果放置在設定好的文件當中
    echo `adb -s $test_device_serial_number push uploads/$test_project_name/apk_file/$app_file data/local/tmp/$apk_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/apk_push

    echo `adb -s $test_device_serial_number shell pm install -r "/data/local/tmp/$apk_package"` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/apk_install

    echo `adb -s $test_device_serial_number push uploads/$test_project_name/apk_test_file/$apk_test_file data/local/tmp/$apk_test_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/test_apk_push

    echo `adb -s $test_device_serial_number shell pm install -r "/data/local/tmp/$apk_test_package"` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/test_apk_install

    echo `adb -s $test_device_serial_number shell am instrument -w $apk_test_package/android.support.test.runner.AndroidJUnitRunner` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/report

    echo `adb -s $test_device_serial_number shell pm uninstall $apk_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/apk_uninstall

    echo `adb -s $test_device_serial_number shell pm uninstall $apk_test_package` >> testing_result/$test_project_name/$test_data/$test_device_serial_number/test_apk_uninstall


    echo `cat testing_result/$test_project_name/$test_data/$test_device_serial_number/report`

else

    echo "not have '$test_project_name' project_name."

fi


