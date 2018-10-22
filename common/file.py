import os
import shutil
import uuid

from common.database.models import *


def upload_file(src_filepath):
    size = os.stat(src_filepath).st_size
    path, filename = os.path.split(src_filepath)
    name, ext = os.path.splitext(filename)
    dst_filepath = os.path.join('/data/tmp', str(uuid.uuid4()))
    shutil.copyfile(src_filepath, dst_filepath)
    file_record = File(name=name, ext=ext, size=size, path=dst_filepath)
    return file_record


def upload_data(filename, data):
    filepath = os.path.join('/data/tmp', str(uuid.uuid4()))
    with open(filepath) as f:
        f.write(data)
    size = os.stat(filepath).st_size
    name, ext = os.path.split(filename)
    file_record = File(name=name, ext=ext, size=size, path=filepath)
    return file_record


def download_file(file_record, path=None):
    if not path:
        path = os.getcwd()
    name = file_record.name
    ext = file_record.ext
    src_filepath = file_record.path
    dst_filepath = os.path.join(path, "%s%s" % (name, ext))
    shutil.copyfile(src_filepath, dst_filepath)
    return dst_filepath


def change_extension(filepath, ext):
    path, filename = os.path.split(filepath)
    name, _ = os.path.splitext(filename)
    return os.path.join(path, '%s%s' % (name, ext))


def delete_file(filepath):
    if not filepath:
        return False
    if not os.path.isfile(filepath):
        return False
    os.remove(filepath)
    return True
