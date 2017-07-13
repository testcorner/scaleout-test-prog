#!/bin/bash

test_project_name=$1
apk_file=$2
if [ -z $apk_file ]; then
	apk_file_num=`ls *.apk | wc -l | tr -d ' '`
	if [ $apk_file_num -gt 1 ]; then
		echo "Ambiguous apk_files. Please enter one APK to inspect."
		exit -1
	fi
	apk_file=`ls *.apk`
fi

if [ -z $ANDROID_HOME ]; then
    echo "Error: Please set ANDROID_HOME to environment variable."
    exit -1
fi

# Add aapt to path
for aapt_path in ${ANDROID_HOME}/build-tools/*/; do break; done
export PATH="$PATH:${aapt_path}"

package=`aapt dump badging uploads/$apk_file | grep package | awk '{print $2}' | sed s/name=//g | sed s/\'//g`
versionCode=`aapt dump badging $apk_file | grep versionCode | awk '{print $3}' | sed s/versionCode=//g | sed s/\'//g`
versionName=`aapt dump badging $apk_file | grep versionName | awk '{print $4}' | sed s/versionName=//g | sed s/\'//g`
sdkVersion=`aapt dump badging $apk_file | grep sdkVersion | sed s/sdkVersion://g | sed s/\'//g`
targetSdkVersion=`aapt dump badging $apk_file | grep targetSdkVersion: | sed s/targetSdkVersion://g | sed s/\'//g`

mkdir uploads/$test_project_name
mkdir uploads/$test_project_name/$package
mv uploads/$apk_file uploads/$test_project_name/$package/$apk_file

echo $package

