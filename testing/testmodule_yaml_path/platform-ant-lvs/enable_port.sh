#!/bin/bash

CURRENT_DIR=$(cd "$(dirname "$0")"; pwd)
cd $CURRENT_DIR

source ~/.bash_profile

FIREWALL_CNF=/etc/sysconfig/SuSEfirewall2

get_os_name() {
    name=`cat /etc/*-release | grep -wi 'id' | awk -F '=' '{print $2}' | sed 's/\"//g' | tr 'A-Z' 'a-z'`
    echo "OS name is ${name}"
}

OS_NAME=$(get_os_name)

function enable_port() {
    local list_port=$(echo $1 | tr "," "\n")

    if [ "$(firewall-cmd --state &> /dev/null && echo Running || echo Not running)" == "Not running" ]; then
        if [ ! -f /etc/firewalld/zones/public.xml ]; then
            echo "The host firewall is either not installed"
            return
        fi

        for port in ${list_port[@]}; do
            if [ "$(echo "$port" | [ -n "`sed -n '/^[0-9][0-9]*$/p'`" ] && echo yes || echo no)" == "no" ]; then
                echo "$port is not a valid port"
                continue
            fi

            if [ -n "$(grep \"$port\" /etc/firewalld/zones/public.xml)" ]; then
                continue
            fi

            echo "enable tcp/udp port $port"
            sed -i "/<\/zone>/i  <port protocol=\"tcp\" port=\"$port\"\/>" /etc/firewalld/zones/public.xml
            sed -i "/<\/zone>/i  <port protocol=\"udp\" port=\"$port\"\/>" /etc/firewalld/zones/public.xml
        done
        return
    else
        for port in ${list_port[@]}
        do
            if [ "$(echo "$port" | [ -n "`sed -n '/^[0-9][0-9]*$/p'`" ] && echo yes || echo no)" == "no" ]; then
                echo "$port is not a valid port"
                continue
            fi

            if [ "$(firewall-cmd --query-port=${port}/tcp | grep 'no')" != "" ]; then
                echo "enable tcp port(${port}) $(firewall-cmd --add-port=${port}/tcp --permanent)"
            fi

            if [ "$(firewall-cmd --query-port=${port}/udp | grep 'no')" != "" ]; then
                echo "enable udp port(${port}) $(firewall-cmd --add-port=${port}/udp --permanent)"
            fi
        done
    fi

    echo "firewall reload $(firewall-cmd --reload)"
}

function list_enabled_port() {
    if [ "$(firewall-cmd --state &> /dev/null && echo Running || echo Not running)" == "Not running" ]; then
        echo "The host firewall is either not installed or not running"
        return
    fi

    echo "list on enabled port: $(firewall-cmd --list-port)"
}

function enable_suse_port() {
    local ports=$(echo $1 | tr "," " ")

    TCP_PORTS=(`sed '/^'FW_SERVICES_EXT_TCP'=/!d;s/'FW_SERVICES_EXT_TCP'=//' $FIREWALL_CNF | sed 's/\"//g'`)
    UDP_PORTS=(`sed '/^'FW_SERVICES_EXT_UDP'=/!d;s/'FW_SERVICES_EXT_UDP'=//' $FIREWALL_CNF | sed 's/\"//g'`)

    TCP_PORTS=(`echo ${TCP_PORTS[*]}" ssh "$ports | sed 's/ /\n/g' | sort -n | uniq`)
    UDP_PORTS=(`echo ${UDP_PORTS[*]}" ssh "$ports | sed 's/ /\n/g' | sort -n | uniq`)

    sed -i "s/^FW_SERVICES_EXT_TCP=.*/FW_SERVICES_EXT_TCP=\"${TCP_PORTS[*]}\"/g" $FIREWALL_CNF
    sed -i "s/^FW_SERVICES_EXT_UDP=.*/FW_SERVICES_EXT_UDP=\"${UDP_PORTS[*]}\"/g" $FIREWALL_CNF

    if [ "$(SuSEfirewall2 status &> /dev/null && echo Running || echo Not running)" == "Running" ]; then
        SuSEfirewall2 stop
        SuSEfirewall2 start
    fi
}

function list_enabled_suse_port() {
    TCP_PORTS=(`sed '/^'FW_SERVICES_EXT_TCP'=/!d;s/'FW_SERVICES_EXT_TCP'=//' $FIREWALL_CNF | sed 's/\"//g' | sed 's/ /\n/g' | sort -n | uniq`)
    echo "list on enabled services and ports: ${TCP_PORTS[*]}"
}

if [ $# -gt 0 ]; then
    echo Prepare enable port list "$1"
    if [ "$OS_NAME" == "sles" ]; then
        enable_suse_port $1
        list_enabled_suse_port
    else
        enable_port $1
        list_enabled_port
    fi
fi