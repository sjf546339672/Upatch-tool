#!/usr/bin/env bash

INSTALL_DIR=${UYUN_ROOT_DIR}/uyun/platform/ant-executor

cd ${INSTALL_DIR}

# 停止agent及upgrade
sh bin/stop.sh
sh bin/stop_upgrade.sh

rm -rf ${INSTALL_DIR}

