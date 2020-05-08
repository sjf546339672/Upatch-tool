#!/bin/bash

umask 027
source ~/.bash_profile
CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
RUNNING_USER=root

if [ -z $UYUN_ROOT_DIR ]; then
    echo "Not environ UYUN_ROOT_DIR"
    exit 1
fi

usage() {
    echo "usage:"
    echo "    sh install.sh optstring parameters"
    echo "    sh install.sh [options] [--] optstring parameters"
    echo "    sh install.sh [options] -o|--options optstring [options] [--] parameters"
    echo ""
    echo "Options:"
    echo "    --security-level                   security level(medium | high)"
    echo "    --disconf-host                     disconf ip list, e.g: 10.1.241.2"
    echo "    --disconf-port                     disconf port, default: 8081"
    echo "    --disconf-user                     disconf user, default: admin"
    echo "    --disconf-passwd                   disconf passwd, default: admin"
    echo "    --local-ip                         local node ip, e.g: 10.1.241.3"
    echo "    --remote-ips                       remote node ip list, e.g: 10.1.241.4,10.1.241.5"
    echo "    --install-role                     install role: single, master, slave, default: single"
    echo "    -h, --help                         help"
}

ARGS=`getopt -o h:: --long security-level:,disconf-host:,disconf-port:,disconf-user:,disconf-passwd:,local-ip:,remote-ips:,install-role:,running-user:,help:: -n 'install.sh' -- "$@"`

if [ $? != 0 ]; then
    usage
    exit 1
fi

# note the quotes around `$ARGS': they are essential!
#set 会重新排列参数的顺序，也就是改变$1,$2...$n的值，这些值在getopt中重新排列过了
eval set -- "$ARGS"

#经过getopt的处理，下面处理具体选项。
while true ; do
    case "$1" in
        --security-level)
            SECURITY_LEVEL=$2
            shift 2
            ;;
        --disconf-host)
            DISCONF_HOST=`echo $2 | awk -F ',' '{print $1}'`
            shift 2
            ;;
        --disconf-port)
            DISCONF_PORT=$2
            shift 2
            ;;
        --disconf-user)
            DISCONF_USER=$2
            shift 2
            ;;
        --disconf-passwd)
            DISCONF_PASS=$2
            shift 2
            ;;
        --local-ip)
            LOCAL_IP=$2
            shift 2
            ;;
        --remote-ips)
            REMOTE_IPS=$2
            shift 2
            ;;
        --install-role)
            INSTALL_ROLE=$2
            shift 2
            ;;
        --running-user)
            RUNNING_USER=$2
            shift 2
            ;;
        -h|--help)
            usage
            exit 1
            ;;
        --)
            break
            ;;
        *)
            echo "internal error!" ;
            exit 1
            ;;
    esac
done

if [ -z "$DISCONF_HOST" ];then
    echo "Please enter disconf"
    exit 1
fi

if [  "$RUNNING_USER" = "" ];
then
    RUNNING_USER=root
fi

function upload()
{
    filename=$1
    upload_dir=$2
    UPLOAD_DIR=$3
    # 通过API上传文件
    http_code=`curl -s -w "%{http_code}" -m 3600 -k -o /tmp/.http_code_cache -F "file=@$filename" -H "Content-Type: multipart/form-data" -X POST "$BASEURL/ufs/openapi/v2/file/upload?path=$upload_dir&file_type=sys&apikey=e10adc3949ba59abbe56e057f2gg88dd"`
    if [ $http_code -eq 200 ]; then
        echo "upload $filename to $UPLOAD_DIR succeed"
        cat /tmp/.http_code_cache
    else
        echo "http_code: $http_code upload $filename to $UPLOAD_DIR failure"
        cat /tmp/.http_code_cache
        rm -rf /tmp/.http_code_cache
        echo "will be delete $UPLOAD_DIR in the ufs"
        sh $INSTALL_DIR/uninstall.sh store_fs  ######
        exit 1
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

echo "*** Current Dir $CURRENT_DIR ***"
MODULE_NAME=$(basename $CURRENT_DIR | awk -F '-' '{print $NF}')
INSTALL_DIR="$UYUN_ROOT_DIR/uyun/ant-module/$MODULE_NAME"
mkdir -p $INSTALL_DIR
\cp -r $CURRENT_DIR/uninstall.sh $INSTALL_DIR
\cp -r $CURRENT_DIR/ant-module.conf $INSTALL_DIR

chown -R $RUNNING_USER:$RUNNING_USER $INSTALL_DIR
chmod +x $INSTALL_DIR/uninstall.sh

sh $CURRENT_DIR/geturl.sh $DISCONF_HOST $DISCONF_PASS $DISCONF_PORT $DISCONF_USER
BASEURL=`cat $CURRENT_DIR/.cache |grep -a '^uyun.baseurl='| awk -F '=' '{print $2}'`
BASEURL=$([[ `echo $BASEURL |grep '/$'|wc -l` -gt 0 ]] && echo ${BASEURL%?} || echo $BASEURL)

mv $CURRENT_DIR/.cache $INSTALL_DIR
pkglist=`cat $INSTALL_DIR/ant-module.conf | grep "$MODULE_NAME" | grep -v '#' | awk -F '=' '{print $1}'`
for pkg in $pkglist
do
    pkg_dir=${pkg#*_}
    cd $CURRENT_DIR/${pkg_dir}
    UPLOAD_DIR=`cat $CURRENT_DIR/ant-module.conf | grep "$pkg" | awk -F "=" '{print $2}'`
    upload_dir=`_encode $UPLOAD_DIR`
    for file in $(\ls)
    do
        upload $file $upload_dir $UPLOAD_DIR
    done
done
