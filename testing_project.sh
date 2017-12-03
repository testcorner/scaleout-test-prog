#!/bin/bash

test_project_name=$1

test_classname=$2

test_data=$3

test_device_serial_number=$4

# Add aapt to path
for aapt_path in ${ANDROID_HOME}/build-tools/*/; do break; done
export PATH="$PATH:${aapt_path}"

if [ -d "uploads/$test_project_name" ]; then

    #echo "Directory $test_project_name exists."

    app_file=`ls uploads/$test_project_name/apk_file`

    apk_package=`aapt dump badging uploads/$test_project_name/apk_file/$app_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    apk_test_file=`ls uploads/$test_project_name/apk_test_file`

    apk_test_package=`aapt dump badging uploads/$test_project_name/apk_test_file/$apk_test_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`

    # 因為在此無法立即回應，所以我們先將我們的結果放置在設定好的文件當中

    adb -s $test_device_serial_number shell am instrument -w -r -e class $test_classname $apk_test_package/android.support.test.runner.AndroidJUnitRunner >> testing_result/$test_project_name/$test_data/$test_device_serial_number/$test_classname.log

else

    echo "not have '$test_project_name' project_name."

fi


