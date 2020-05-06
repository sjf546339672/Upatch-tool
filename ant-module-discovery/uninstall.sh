 #!/bin/bash

function _uninstall_fs()
{
    # 通过api删除模块包
    upload_dir=$1
    http_code=`curl -s -w "%{http_code}" -m 3600 -k -o /dev/null -X POST "$BASEURL/ufs/openapi/v2/dir/remove?path=$upload_dir&apikey=e10adc3949ba59abbe56e057f2gg88dd"`
    if [ $http_code -eq 200 ]; then
        echo "delete dir $upload_dir success"
    else
        echo "delete dir $upload_dir failure"
    fi
}

function uninstall_fs()
{
    dirlist=`cat $INSTALL_DIR/ant-module.conf | grep "$MODULE_NAME" | awk -F '=' '{print $2}'`
    for dir in $dirlist
    do
        _upload_dir=`_encode $dir`
        _uninstall_fs $_upload_dir
    done
}


function uninstall_disk()
{
    if [ -d "$INSTALL_DIR" ]; then
        rm -rf $INSTALL_DIR
    fi
}


function _encode()
{
    local _length="${#1}"
    for (( _offset = 0 ; _offset < _length ; _offset++ )); do
        _print_offset="${1:_offset:1}"
        case "${_print_offset}" in
            [a-zA-Z0-9.~_-]) printf "${_print_offset}" ;;
            ' ') printf + ;;
            *) printf '%%%X' "'${_print_offset}" ;;
        esac
    done
}

# INSTALL_DIR="/opt/uyun/ant-module/agent"
INSTALL_DIR=$(cd `dirname $0`; pwd)
MODULE_NAME=$(basename $INSTALL_DIR)
BASEURL=`cat $INSTALL_DIR/.cache |grep -a '^uyun.baseurl='| awk -F '=' '{print $2}'`
BASEURL=$([[ `echo $BASEURL |grep '/$'|wc -l` -gt 0 ]] && echo ${BASEURL%?} || echo $BASEURL)

case $1 in
    store_fs)
        uninstall_fs
        ;;
    disk)
        uninstall_disk
        ;;
    all)
        uninstall_fs
        uninstall_disk
        ;;
esac

sleep 1