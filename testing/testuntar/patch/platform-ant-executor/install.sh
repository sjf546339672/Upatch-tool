#!/usr/bin/env bash
# 22222222222
umask 027
source ~/.bash_profile
CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)

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

INSTALL_DIR=${UYUN_ROOT_DIR}/uyun/platform/ant-executor


mkdir -p ${INSTALL_DIR}

\cp -r ./agent/* ${INSTALL_DIR}
\cp ./module.yaml ${INSTALL_DIR}
\cp ./uninstall.sh ${INSTALL_DIR}
\cp ./geturl.sh ${INSTALL_DIR}

sh geturl.sh ${DISCONF_HOST} ${DISCONF_PASS} ${DISCONF_PORT} ${DISCONF_USER}
BASEURL=`cat $CURRENT_DIR/.cache |grep -a '^uyun.baseurl='| awk -F '=' '{print $2}'`
BASEURL=$([[ `echo $BASEURL |grep '/$'|wc -l` -gt 0 ]] && echo ${BASEURL%?} || echo $BASEURL)


cd ${INSTALL_DIR}
./embedded/bin/python -m framework.bootstrap --tenant "e10adc3949ba59abbe56e057f20f88dd" --network-domain 'defaultZone' --upstream ${BASEURL}  --transporter

ln -s ${INSTALL_DIR}/var/logs ${INSTALL_DIR}/logs

# 启动
sh ${INSTALL_DIR}'/bin/ant' start
