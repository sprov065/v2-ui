import logging
import time

import psutil

from util import cmd_util, v2_util
from util.schedule_util import schedule_job

__status = {}
__last_access = time.time()
__last_get = time.time()
__access_interval = 0
__get_interval = 0
__last_ct = psutil.cpu_times()


def get_status():
    global __last_access
    __last_access = time.time()
    return __status


def refresh_status():
    global __access_interval
    try:
        now = time.time()
        __access_interval = now - __last_access
        if __access_interval <= 60:
            global __get_interval, __last_get
            __get_interval = now - __last_get
            __last_get = now
            v2_status()
            uptime()
            cpu()
            memory()
            swap()
            disk()
            loads()
            net()
    except Exception as e:
        logging.warning('Failed to get system status information: ' + str(e))


def v2_status():
    # result, code = cmd_util.exec_cmd('systemctl is-active v2ray')
    # results = result.split('\n')
    # has_result = False
    # for result in results:
    #     if result.startswith('active'):
    #         code = 0
    #         has_result = True
    #         break
    #     elif result.startswith('inactive'):
    #         code = 1
    #         has_result = True
    #         break
    #
    # if not has_result:
    #     code = 2
    code = v2_util.__get_stat_code()
    version = v2_util.get_v2ray_version()
    msg = v2_util.get_v2ray_error_msg()
    __status['v2'] = {
        'code': code,
        'version': version,
        'error_msg': msg,
    }


def uptime():
    __status['uptime'] = time.time() - psutil.boot_time()


def cpu():
    global __last_ct
    cur_ct = psutil.cpu_times()

    last_total = sum(__last_ct)
    cur_total = sum(cur_ct)

    total = cur_total - last_total
    idle = cur_ct.idle - __last_ct.idle

    if total <= 0:
        percent = 0
    else:
        percent = (total - idle) / total * 100
    __last_ct = cur_ct
    __status['cpu'] = {
        'percent': percent
    }


def memory():
    mem = psutil.virtual_memory()
    __status['memory'] = {
        'used': mem.used,
        'total': mem.total
    }


def swap():
    swap_mem = psutil.swap_memory()
    __status['swap'] = {
        'used': swap_mem.used,
        'total': swap_mem.total
    }


def disk():
    d = psutil.disk_usage('/')
    __status['disk'] = {
        'total': d.total,
        'used': d.used
    }


def loads():
    __status['loads'] = psutil.getloadavg()


__last_net_io = psutil.net_io_counters()


def __get_net_tcp_udp_count():
    conns = psutil.net_connections()
    tcp_count = 0
    udp_count = 0
    for conn in conns:
        if conn.type == 1:
            tcp_count += 1
        elif conn.type == 2:
            udp_count += 1
    return tcp_count, udp_count


def net():
    global __last_net_io
    cur_net_io = psutil.net_io_counters()
    sent = cur_net_io.bytes_sent
    recv = cur_net_io.bytes_recv
    up = (sent - __last_net_io.bytes_sent) / __get_interval
    down = (recv - __last_net_io.bytes_recv) / __get_interval
    tcp_count, udp_count = __get_net_tcp_udp_count()
    __status['net_io'] = {
        'up': up,
        'down': down
    }
    __status['net_traffic'] = {
        'sent': sent,
        'recv': recv
    }
    __status['tcp_count'] = tcp_count
    __status['udp_count'] = udp_count
    __last_net_io = cur_net_io


schedule_job(refresh_status, 2)
