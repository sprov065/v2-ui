import logging
import platform
import subprocess
from threading import Timer
from typing import Tuple

__is_windows = platform.system() == 'Windows'


def exec_cmd(cmd, timeout=10) -> Tuple[str, int]:
    code = -100
    p = None
    try:
        def close_task():
            if p:
                p.terminate()
        task = Timer(timeout, close_task)
        task.start()
        encoding = 'gbk' if __is_windows else 'utf-8'
        process = subprocess.Popen(['sh', '-c', cmd], shell=False, stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT, encoding=encoding)
        p = process
        code = process.wait(timeout)
        lines = []
        p = None
        task.cancel()
        if code == 0:
            while True:
                line = process.stdout.readline()
                if not line:
                    break
                lines.append(line)
        return ''.join(lines), code
    except Exception as e:
        if not __is_windows:
            logging.warning(f'execute \"{cmd}\" failed: {e}')
        return '', code
    finally:
        if p:
            p.terminate()
