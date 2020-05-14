#!/bin/bash

umask 027
CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
cd $CURRENT_DIR

if [ -z $UYUN_ROOT_DIR ]; then
    echo "Not environ UYUN_ROOT_DIR"
    exit 1
fi

#disconf基本信息
DISCONF_PORT=8081
DISCONF_VERSION=2_0_0
DISCONF_APP_UYUN=uyun
DISCONF_ENV=local

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
    encryted_text=$(curl -sS "http://127.0.0.1:7550/daemon/api/\v2/encryption/encrypt? \
    type=$1&plain_text=$(urlencode $2)&\algorithm=$(urlencode $3)")
    echo $encryted_text
}

decrypt() {
    REG="^>>>.*<<<$"
    if [[ $1 =~ $REG ]]; then
        plain_text=$(curl -sS "http://127.0.0.1:7550/daemon/api/v2/encryption/decrypt? \
        encrypted_text=$(urlencode $1)")
        echo $plain_text
    else
        echo $1
    fi
}

usage() {
    echo "Usage:"
    echo "    sh install.sh optstring parameters"
    echo "    sh install.sh [options] [--] optstring parameters"
    echo "    sh install.sh [options] -o|--options optstring [options] [--] parameters"
    echo ""
    echo "Options:"
    echo "    --disconf-host                     disconf主机地址, eg: 10.1.241.2"
    echo "    --disconf-port                     disconf端口, default: 8081"
    echo "    --disconf-user                     disconf用户名, eg: admin"
    echo "    --disconf-passwd                   disconf密码, eg: 123456"
    echo "    --install-role                     安装角色, single|master|slave, default: single"
    echo "    --local-ip                         当前节点IP, eg: 10.1.241.23"
    echo "    --remote-ips                       远程节点IP列表, eg: 10.1.241.24,10.1.241.25"
    echo "    --running-user                     运行用户, default: root"
    echo "    --vip                              虚拟IP, eg: 10.1.241.220"
    echo "    --lvs-mode2                        DR(直接路由模式)/TUN(隧道模式)"
    echo "    --port2                            ant-nginx对外提供服务端口，default: 7583"
    echo "    --platform-ant-nginx               platform-ant-nginx地址，eg: 10.1.241.10"
    echo "    -h, --help                         help"
}

ARGS=`getopt -o h:: --long disconf-host:,disconf-port:,disconf-user:,disconf-passwd:,install-role:,local-ip:,remote-ips:,running-user:,vip:,lvs-mode2:,port2:,platform-ant-nginx:,help:: -n 'install.sh' -- "$@"`

if [ $? != 0 ]; then
    usage
    exit 1
fi

# note the quotes around `$ARGS': they are essential!
#set 会重新排列参数的顺序，也就是改变$1,$2...$n的值，这些值在getopt中重新排列过了
eval set -- "$ARGS"

#经过getopt的处理，下面处理具体选项。
while true; do
    case "$1" in
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
        --install-role)
            TYPE=$2
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
        --running-user)
            RUNNING_USER=$2
            shift 2
            ;;
        --vip)
            VIP=$2
            shift 2
            ;;
        --lvs-mode2)
            LVS_MODE=$2
            shift 2
            ;;
        --port2)
            PORT=$2
            shift 2
            ;;
        --platform-ant-nginx)
            PLATFORM_ANT_NGINX=$2
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
            echo "Invalid parameter";
            exit 1
            ;;
    esac
done

check_lvs() {
    if [[ ${VIP} == "" ]]; then
        echo "LVS_VIP can not be null"
        exit 1
    fi
    if [[ ${VIP} == "localhost" ]]; then
        echo "LVS_VIP can not be localhost"
        exit 1
    fi
    if [[ ${LVS_MODE} != "DR" && ${LVS_MODE} != "TUN" ]]; then
        echo "LVS_MODE only choose one of DR/TUN, not ${LVS_MODE}."
        exit 1
    fi
}

check_lvs

if [ $UID -eq 0 ]; then
    sh enable_port.sh $PORT
fi

ROOT_DIR=$(pwd)
INSTALL_DIR=$UYUN_ROOT_DIR/uyun/platform/ant-lvs
LVS_SH=$INSTALL_DIR/bin/lvs.sh

echo "INFO: Prepare to install lvs"

rm -rf ${INSTALL_DIR}
mkdir -p ${INSTALL_DIR}

LOGIN_URL="http://${DISCONF_HOST}:${DISCONF_PORT}/api/account/signin"
DOWNLOAD_URL="http://${DISCONF_HOST}:${DISCONF_PORT}/api/config"
PASSWD=$(decrypt $DISCONF_PASS)

curl -c ./cookie_c.txt -F "name=${DISCONF_USER}" -F "password=$PASSWD" -F "remember=1" $LOGIN_URL
curl -b ./cookie_c.txt  "${DOWNLOAD_URL}/file?app=uyun&env=local&version=2_0_0&key=common.properties" -o common.properties

if [ ! -f common.properties ];then
    echo 'cant not find the baseurl please check'
    exit 1
fi

BASEURL=`cat common.properties |grep -a '^uyun.baseurl='| awk -F '=' '{print $2}'`
BASEURL=$([[ `echo $BASEURL |grep '/$'|wc -l` -gt 0 ]] && echo ${BASEURL%?} || echo $BASEURL)
rm -rf cookie_c.txt

cp -rf bin ${INSTALL_DIR}
cp module.yaml ${INSTALL_DIR}


sed  -i "9i\VIP=${VIP}" $LVS_SH
sed  -i "10i\PLATFORM_ANT_NGINX=${PLATFORM_ANT_NGINX}" $LVS_SH
sed  -i "11i\LVS_MODE=${LVS_MODE}" $LVS_SH

if [ ${PORT} ]; then
    sed  -i "11i\PORT=${PORT}" $LVS_SH
else
    sed  -i "11i\PORT=7583" $LVS_SH
fi


# 若VIP存在,则启动lvs
if [[ ${VIP} != "" && ${VIP} != "localhost" ]]; then
    PLATFORM_ANT_NGINX_LIST=(`echo $PLATFORM_ANT_NGINX | tr ',' ' '`)
    # lvs DR模式
    if [[ ${LVS_MODE} == "DR" ]]; then
        sudo ipvsadm -A -t $VIP:$PORT -s rr
        for i in ${PLATFORM_ANT_NGINX_LIST[@]}
        do
            sudo ipvsadm -a -t $VIP:$PORT -r $i:$PORT -g
        done
    # lvs TUN模式
    else
#        modprobe tun
#        modprobe ipip
        sudo ip addr add ${VIP}/32 broadcast ${VIP} dev tunl0
        sudo ip link set tunl0 up
        # 添加路由
        sudo route add -host ${VIP} tunl0
        #icmp recruit 设置
#        echo "0" >/proc/sys/net/ipv4/ip_forward
#        echo "0" >/proc/sys/net/ipv4/conf/all/send_redirects
#        echo "0" >/proc/sys/net/ipv4/conf/default/send_redirects
        # LVS 设置
        sudo ipvsadm -At $VIP:$PORT -s rr
        for i in ${PLATFORM_ANT_NGINX_LIST[@]}
        do
            sudo ipvsadm -at $VIP:$PORT -r $i:$PORT -i -w 1
        done
    fi
    sudo ipvsadm -L -n
fi

sed -i "s#^uyun.baseurl.pub=.*#uyun.baseurl.pub=http://${VIP}:${PORT}/#" common.properties

get_disconf_appId() {
    app_name=$1
    app_id=$(cat result | ./jq ".page.result[] | select(.name == \"$app_name\") | .id")
    if [ -z "$app_id" ]; then
        curl -b cookies -c cookies -sS $APP_CREATE_URL --data "app=$app_name&desc=$app_name" | grep -v err_no > /dev/null
        curl -b cookies -c cookies -sS $APP_LIST_URL | grep -v err_no > result
        app_id=$(cat result | ./jq ".page.result[] | select(.name == \"$app_name\") | .id")
    fi
    echo $app_id
}

load_common_item() {
    if [ -z "$DISCONF_HOST" ];then
        echo "Please enter disconf"
        exit 1
    fi

    DISCONF_IPS=($(echo $DISCONF_HOST|tr "," "\n"))
    for DISCONF_IP in ${DISCONF_IPS[@]}; do
        if [ -z "$DISCONF_HOSTS" ];then
            DISCONF_HOSTS=$DISCONF_IP:$DISCONF_PORT
        else
            DISCONF_HOSTS=${DISCONF_HOSTS},$DISCONF_IP:$DISCONF_PORT
        fi
    done
    for DISCONF_IP in ${DISCONF_IPS[@]}; do
        DISCONF_SERVER_ADDR=http://$DISCONF_IP:$DISCONF_PORT
        APP_LIST_URL=$DISCONF_SERVER_ADDR/api/app/list
        APP_CREATE_URL=$DISCONF_SERVER_ADDR/api/app
        ENV_LIST_URL=$DISCONF_SERVER_ADDR/api/env/list
        FILE_UPLOAD_URL=$DISCONF_SERVER_ADDR/api/web/config/file
        CONF_LIST_URL=$DISCONF_SERVER_ADDR/api/web/config/simple/list

        curl -c cookies --connect-timeout 30 -sS $LOGIN_URL --data "name=$DISCONF_USER&password=$(decrypt $DISCONF_PASS)&remember=0" -o result
        loginResult=$(cat result | ./jq '.success')
        if [ "$loginResult" == "\"true\"" ]; then
            echo "Disconf login successful"
            login_result=true
            break
        else
            login_result=false
        fi
    done

    if [ "$login_result" == "false" ];then
        echo "Disconf login failed!"
        exit 1
    fi

    # 获取app列表
    curl -b cookies -c cookies -sS $APP_LIST_URL | grep -v err_no > result
    # 获取uyun appId
    UYUN_APP_ID=$(get_disconf_appId $DISCONF_APP_UYUN)

    #获取envId
    curl -b cookies -c cookies -sS $ENV_LIST_URL | grep -v err_no > result
    ENV_ID=$(cat result | ./jq '.page.result[] | select(.name == "local") | .id')
}

# 解析result文件json是否返回true
checkResult() {
    loginResult=$(cat result | ./jq '.success')
    if [ "$loginResult" != "\"true\"" ]; then
        echo "$1"
        exit 1
    else
        echo "$2"
    fi
}

# 上传配置文件到disconf tenant
upload_file() {
    uyun_config_file=$1
    uyun_key=${uyun_config_file##*/}
    curl -b cookies -sS "$CONF_LIST_URL?appId=$UYUN_APP_ID&envId=$ENV_ID&version=$DISCONF_VERSION" | grep -v err_no > result
    CONFIG_ID=$(cat result | ./jq ".page.result[] | select(.key == \"$uyun_key\") | .configId")

    if [ -n "$CONFIG_ID" ]; then
        echo "Replace the disconf old configuration file"
        curl -b cookies -sS -F "myfilerar=@$uyun_config_file" "$FILE_UPLOAD_URL/$CONFIG_ID" &> result
    else
        UPLOAD_URL="$FILE_UPLOAD_URL?appId=$UYUN_APP_ID&envId=$ENV_ID&version=$DISCONF_VERSION"
        curl -b cookies -sS -F "myfilerar=@$uyun_config_file" $UPLOAD_URL &> result
    fi
    checkResult "$uyun_config_file uploaded failed" "$uyun_config_file uploaded successfully"
}

# 修改common.properties
load_common_item
upload_file $CURRENT_DIR/common.properties
cp common.properties ${INSTALL_DIR}

uninstall() {
    echo "Check whether keepalived-ant-lvs has been installed, if there is to uninstall."
    sudo pkill -f keepalived_ant_lvs
}

install() {
    echo "Unpack keepalived package and install....."
    tar -zxf $CURRENT_DIR/keepalived/keepalived-1.3.5.tar.gz -C $UYUN_ROOT_DIR

    mkdir -p $INSTALL_DIR/keepalived
    cp $CURRENT_DIR/keepalived/keepalived_ant_lvs.conf $INSTALL_DIR/keepalived/

    chmod -R 755 $INSTALL_DIR/keepalived
    chmod 644 $INSTALL_DIR/keepalived/keepalived_ant_lvs.conf
}

configure() {
    echo "Configure keepalived_ant_lvs.conf file....."

    router_id=${VIP##*.}
    vip_prefix=${VIP%.*}
    sed -i "s/ROUTER_ID/$router_id/g" $INSTALL_DIR/keepalived/keepalived_ant_lvs.conf
    sed -i 's/"-D"/"-D -d -S 0"/g' $UYUN_ROOT_DIR/keepalived/etc/sysconfig/keepalived

    # NIC list
    nics=$(ls /sys/class/net)
    for nic in $nics
    do
        ip_arr=$(ip addr show $nic | grep $vip_prefix | grep 'inet ' | cut -f2 | awk '{ print $2}' | awk -F "/" '{ print $1}')
        if [[ ${ip_arr[@]} =~ $vip_prefix ]]; then
            subnet=$(ip addr show $nic | grep -w $vip_prefix | grep 'inet ' | cut -f2 | awk 'NR==1{ print $2}' | awk -F "/" '{ print $2}')
            brd=$(ip addr show $nic | grep -w $vip_prefix | grep 'inet ' | cut -f2 | awk 'NR==1{ print $4}')
            scope=$(ip addr show $nic | grep -w $vip_prefix | grep 'inet ' | cut -f2 | awk 'NR==1{ print $6}')

            echo "keepalived vip address: $VIP $subnet $brd dev $nic scope $scope label $nic:$router_id"
            sed -i "s/VIP_ADDR/$VIP\/$subnet brd $brd dev $nic scope $scope label $nic:$router_id/g" $INSTALL_DIR/keepalived/keepalived_ant_lvs.conf
            sed -i "s/NIC/$nic/g" $INSTALL_DIR/keepalived/keepalived_ant_lvs.conf
            break
        fi
    done

    if [ -z "$subnet" ]; then
        echo "VIP($VIP) failed to match the nic"
        exit 1
    fi
}

start() {
    sudo $UYUN_ROOT_DIR/keepalived/sbin/keepalived \
        -f $INSTALL_DIR/keepalived/keepalived_ant_lvs.conf -d -D -S 0 --pid=$INSTALL_DIR/keepalived/keepalived_ant_lvs.pid \
        --vrrp_pid=$INSTALL_DIR/keepalived/vrrp_ant_lvs.pid \
        --checkers_pid=$INSTALL_DIR/keepalived/checkers_ant_lvs.pid

    sleep 5

    if [ "$(ps aux | grep keepalived_ant_lvs | grep -v grep | wc -l)" -ge 3 ]; then
        echo "Start keepalived-ant-lvs success!"
    else
        echo "Start keepalived-ant-lvs failure!"
        exit 1
    fi
}

if [[ "$VIP" != "" && "$VIP" != "localhost" ]]; then
    uninstall
    install
    configure
    start
fi