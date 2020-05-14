#!/bin/sh
source ~/.bash_profile
umask 077

BIN_DIR=$(cd "$(dirname "$0")"; pwd)
WORK_HOME=$(dirname $BIN_DIR)
COMMAND=$1
APP_NAME="ant-lvs"



if [ -z $UYUN_ROOT_DIR ]; then
    echo "Not environ UYUN_ROOT_DIR"
    exit 1
fi

# 以服务模式启动
start() {
    # 根据实际情况重写启动命令，切记不可生成 nohup.out 文件
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
#            modprobe tun
#            modprobe ipip
            sudo ip addr add ${VIP}/32 broadcast ${VIP} dev tunl0
            sudo ip link set tunl0 up
            # 添加路由
            sudo route add -host ${VIP} tunl0
            #icmp recruit 设置
#            echo "0" >/proc/sys/net/ipv4/ip_forward
#            echo "0" >/proc/sys/net/ipv4/conf/all/send_redirects
#            echo "0" >/proc/sys/net/ipv4/conf/default/send_redirects
            # LVS 设置
            sudo ipvsadm -At $VIP:$PORT -s rr
            for i in ${PLATFORM_ANT_NGINX_LIST[@]}
            do
                sudo ipvsadm -at $VIP:$PORT -r $i:$PORT -i -w 1
            done
        fi
        sudo ipvsadm -L -n
        # start keepalived
        sudo $UYUN_ROOT_DIR/keepalived/sbin/keepalived \
            -f $WORK_HOME/keepalived/keepalived_ant_lvs.conf -d -D -S 0 --pid=$WORK_HOME/keepalived/keepalived_ant_lvs.pid \
            --vrrp_pid=$WORK_HOME/keepalived/vrrp_ant_lvs.pid \
            --checkers_pid=$WORK_HOME/keepalived/checkers_ant_lvs.pid
    fi
}

handle_lvs_stop() {
    sudo ipvsadm -C
    if [[ ${LVS_MODE} == "TUN" ]]; then
        sudo ip -f inet addr delete ${VIP}/32 dev tunl0
    fi
}

stop() {
    handle_lvs_stop
    # stop keepalived
    if [[ -n "$(ps aux | grep keepalived_ant_lvs | grep -v grep)" ]]; then
        sudo pkill -f keepalived_ant_lvs
    fi
}

uninstall() {
    handle_lvs_stop
    if [[ -n "$(ps aux | grep keepalived_ant_lvs | grep -v grep)" ]]; then
        sudo pkill -f keepalived_ant_lvs
    fi
    rm -rf $WORK_HOME
}

# 远程debug
debug() {
   echo -n "$APP_NAME don't support debug mode."
}

# 服务状态（0：可用，1：不可用）
status() {
    if [[ "$VIP" != "" && "$VIP" != "localhost" ]]; then
        if [ "$(ps aux | grep keepalived_ant_lvs | grep -v grep | wc -l)" -eq 0 ]; then
            echo "ERROR: keepalived-ant-lvs service unavailable!"
            exit 1
        else
            echo "INFO: keepalived-ant-lvs service available!"
            exit 0
        fi
    fi
    echo "INFO: ant-lvs service available!"
    exit 0
}

case "$COMMAND" in
    'start')
        start
        ;;
    'stop')
        stop
        ;;
    'uninstall')
        uninstall
        ;;
    'restart')
        stop
        sleep 3
        start
        ;;
    'debug')
        debug
        ;;
    'status')
        status
        ;;
    *)
        echo "not find COMMAND=$COMMAND"
        exit 1
esac