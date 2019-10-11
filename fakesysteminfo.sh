#!/bin/bash
#This is intended to be a FAKE systemctl for v2ray.
#DO NOT USE THIS IF THERE ARE ANY OTHER OPTION.
if [ "${1}" == "start" ]
then
    if [ -f /var/tmp/v2ray.pid ]
    then
        if ps -p $(cat /var/tmp/v2ray.pid)
        then
            return 0
        else
            nohup v2ray -config /etc/v2ray/config.json &
            echo $! >/var/tmp/v2ray.pid
        fi
    else
        nohup v2ray -config /etc/v2ray/config.json &
        echo $! >/var/tmp/v2ray.pid
    fi
elif [ "${1}" == "is-active" ]
then
    if [ -f /var/tmp/v2ray.pid ]
    then
        if ps -p $(cat /var/tmp/v2ray.pid)
        then
            echo "active"
        else
            echo "inactive"
        fi
    else
        echo "inactive"
    fi
elif [ "${1}" == "restart" ]
then
    if [ -f /var/tmp/v2ray.pid ]
    then
        if ps -p $(cat /var/tmp/v2ray.pid)
        then
            kill -9 $(cat /var/tmp/v2ray.pid)
        fi
    fi
    nohup v2ray -config /etc/v2ray/config.json &
    echo $! >/var/tmp/v2ray.pid
    return 0
elif [ "${1}" == "stop" ]
    if [ -f /var/tmp/v2ray.pid ]
    then
        if ps -p $(cat /var/tmp/v2ray.pid)
        then
            kill -9 $(cat /var/tmp/v2ray.pid)
        fi
    fi
    return 0
elif