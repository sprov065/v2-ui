import os
import shutil
import zipfile
from typing import List


def mkdirs(dirname):
    if not os.path.exists(dirname):
        os.makedirs(dirname)


def touch(filename):
    mkdirs(os.path.dirname(filename))
    if not os.path.exists(filename):
        with open(filename, 'w') as f:
            f.write('')


def is_file(filename):
    return os.path.isfile(filename)


def is_dir(dirname):
    return os.path.isdir(dirname)


def read_file(file: str) -> str:
    with open(file, encoding='utf-8') as f:
        return f.read()


def write_file(file: str, content: str):
    with open(file, 'w', encoding='utf-8') as f:
        f.write(content)


def list_files(path: str) -> List[str]:
    return os.listdir(path)


def del_file(path: str):
    try:
        if is_file(path):
            os.remove(path)
    except Exception as e:
        pass


def del_dir(path: str):
    try:
        if is_dir(path):
            shutil.rmtree(path)
    except Exception as e:
        pass


def unzip_file(filename: str, dest_dir: str):
    if zipfile.is_zipfile(filename):
        fz = None
        try:
            fz = zipfile.ZipFile(filename, 'r')
            fz.extractall(dest_dir)
            # for file in fz.namelist():
            #     fz.extract(file, dest_dir)
        finally:
            if fz:
                fz.close()
    else:
        raise Exception(f'{filename} is not zip file')


def mv_file(src: str, dest: str):
    os.rename(src, dest)
