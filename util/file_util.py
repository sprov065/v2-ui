import os


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
