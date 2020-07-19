import subprocess
from threading import Timer


def exec_cmd(cmd, timeout=10):
    code = -100
    p = None
    try:
        def close_task():
            if p:
                p.kill()
        task = Timer(timeout, close_task)
        task.start()
        with subprocess.Popen(['sh', '-c', cmd], shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT) as process:
            p = process
            code = process.wait(timeout)
            result = process.stdout.read()
            p = None
            task.cancel()
        return result.decode('utf-8'), code
    except BaseException:
        return '', code
    finally:
        if p:
            p.kill()
