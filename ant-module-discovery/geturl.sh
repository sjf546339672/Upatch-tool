#!/bin/bash

CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)

urlencode() {
    STR=$@
    [ "${STR}x" == "x" ] && { STR="$(cat -)"; }

    echo ${STR} | sed -e 's| |%20|g' \
                      -e 's|!|%21|g' \
                      -e 's|#|%23|g' \
                      -e 's|\$|%24|g' \
                      -e 's|%|%25|g' \
                      -e 's|&|%26|g' \
                      -e "s|'|%27|g" \
                      -e 's|(|%28|g' \
                      -e 's|)|%29|g' \
                      -e 's|*|%2A|g' \
                      -e 's|+|%2B|g' \
                      -e 's|,|%2C|g' \
                      -e 's|/|%2F|g' \
                      -e 's|:|%3A|g' \
                      -e 's|;|%3B|g' \
                      -e 's|=|%3D|g' \
                      -e 's|?|%3F|g' \
                      -e 's|@|%40|g' \
                      -e 's|\[|%5B|g' \
                      -e 's|]|%5D|g' \
                      -e 's|>|%3E|g' \
                      -e 's|<|%3C|g'
}

encrypt() {
    sh -c "</dev/tcp/127.0.0.1/7550" > /dev/null 2>&1
    if [ $? -ne 0 ] ; then
        echo "OMP daemon service unavailable."
        exit 1
    fi
    encryted_text=$(curl -sS "http://127.0.0.1:7550/daemon/api/v2/encryption/encrypt?type=$1&plain_text=$(urlencode $2)&algorithm=$(urlencode $3)")
    echo $encryted_text
}

decrypt() {
    sh -c "</dev/tcp/127.0.0.1/7550" > /dev/null 2>&1
    if [ $? -ne 0 ] ; then
        echo "OMP daemon service unavailable."
        exit 1
    fi

    ENCRYPT_REG="^>>>.*<<<$"
    if [[ $1 =~ $ENCRYPT_REG ]] ; then
        plain_text=$(curl -sS "http://127.0.0.1:7550/daemon/api/v2/encryption/decrypt?encrypted_text=$(urlencode $1)")
        echo $plain_text
    else
        echo $1
    fi
}

DISCONF_HOST=$1
DISCONF_PASS=$2
DISCONF_PORT=$3
DISCONF_USER=$4


DISCONF_HOST=$(echo $DISCONF_HOST|cut -d "," -f1)
LOGIN_URL="http://${DISCONF_HOST}:${DISCONF_PORT}/api/account/signin"
DOWNLOAD_URL="http://${DISCONF_HOST}:${DISCONF_PORT}/api/config"
PASSWD=$(decrypt $DISCONF_PASS)

curl -c ./cookie_c.txt -F "name=${DISCONF_USER}" -F "password=$PASSWD" -F "remember=1" $LOGIN_URL
curl -b ./cookie_c.txt  "${DOWNLOAD_URL}/file?app=uyun&env=local&version=2_0_0&key=common.properties" -o $CURRENT_DIR/.cache

if [ ! -f .cache ];then
    echo 'cant not find the baseurl please check'
    exit 1
fi