import json
import time

import redis
from celery import Celery
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

import common.database.code as db_code
import common.file
from backend.conv import convert
from common.database.models import *

app = Celery('converter',
             broker='amqp://guest@localhost//',
             include=['backend.tasks'])

engine = create_engine('mysql+pymysql://root:pass@localhost:3306/ebook', echo=True)
Session = sessionmaker(bind=engine)

rcp = redis.ConnectionPool(host='localhost', port=6379, db=0)
rds = redis.StrictRedis(connection_pool=rcp)


@app.task()
def run(task_id):
    session = Session()

    task = session.query(Task).filter(Task.id == task_id).one()
    if task.status != db_code.TASK_STATUS_QUEUED:
        raise Exception('error task status is not QUEUED. task: %d' % task_id)

    src_filepath = None
    dst_filepath = None
    try:
        # start
        task.status = db_code.TASK_STATUS_STARTED
        task.started = datetime.utcnow()
        session.commit()
        task_status = {'status': task.status}
        rds.setex(task.id, 60 * 60 * 24, json.dumps(task_status))
        print("started task: %d" % task.id)

        # convert
        file_record = session.query(File).filter(File.id == task.src_file_id).one()
        src_filepath = common.file.download_file(file_record)
        dst_filepath = common.file.change_extension(src_filepath, task.dst_ext)
        t = time.perf_counter()
        convert(src_filepath, dst_filepath)
        t = time.perf_counter() - t
        print("converted task: %d" % task_id)

        # completed
        file_record = common.file.upload_file(dst_filepath)
        session.add(file_record)
        session.flush()
        session.refresh(file_record)
        task.status = db_code.TASK_STATUS_COMPLETED
        task.ended = datetime.utcnow()
        task.dst_file_id = file_record.id
        task.elapsed_time = int(t * 1000)
        print("completed task: %d" % task_id)
    except Exception as e:
        task.status = db_code.TASK_STATUS_FAILED
        print("failed task: %d" % task_id)
        print(e.message, e.args)
    finally:
        session.commit()
        task_status = {'status': task.status}
        rds.setex(task_id, 60 * 60 * 24, json.dumps(task_status))
        common.file.delete_file(src_filepath)
        common.file.delete_file(dst_filepath)

    return task_id


@app.task()
def test(key):
    status = rds.get(key).decode('utf-8')
    print(status)
    for i in range(100):
        time.sleep(1)
        v = "%s-%d" % (status, i)
        rds.set(key, v)
        print(v)
    return key


if __name__ == '__main__':
    app.start()
