import json
import os
import uuid

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from flask.json import jsonify
from werkzeug.exceptions import abort

import common.database.code as db_code
import backend.tasks as tasks
from web import db, rds
from web.auth import login_required
from common.database.models import (
    File, Task
)

bp = Blueprint('convert', __name__, url_prefix='/convert')


@bp.route('/', methods=['GET', 'POST'])
@login_required
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']
        ext = request.form['ext']

        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        fild_id = save_file(file)

        task = Task(owner_id=g.user.id, src_file_id=fild_id, dst_ext=ext, status=db_code.TASK_STATUS_QUEUED)
        db.session.add(task)
        db.session.commit()
        task_status = {'status': task.status}
        rds.setex(task.id, 60 * 60 * 24, json.dumps(task_status))

        tasks.run.delay(task.id)

        return redirect(url_for('convert.download', task_id=task.id))

    return render_template('convert/index.html')


@bp.route('/<int:task_id>', methods=['GET'])
@login_required
def download(task_id):
    task = Task.query.get(task_id)
    if not task:
        abort(400)
    if task.owner_id != g.user.id:
        abort(403)

    task_status = rds.get(task_id)
    if not task_status:
        abort(400)

    return render_template('convert/download.html', task_id=task_id)


@bp.route('/status', methods=['POST'])
@login_required
def status():
    result = {}
    rq = request.json
    task_id = rq['task_id']

    task_status = rds.get(task_id)
    if not task_status:
        abort(400)
    task_status = json.loads(task_status)

    result['status'] = task_status['status']
    if task_status['status'] == db_code.TASK_STATUS_COMPLETED:
        task = Task.query.get(task_id)
        if not task:
            abort(400)
        file_record = File.query.get(task.dst_file_id)
        if not file_record:
            abort(500)
        result['url'] = url_for('file.download', file_id=task.dst_file_id)
        result['filename'] = "%s%s" % (file_record.name, file_record.ext)

    return jsonify(result)


@bp.route('/status_old', methods=['POST'])
@login_required
def status_old():
    result = {}
    rq = request.json
    task_id = rq['task_id']
    task = Task.query.get(task_id)
    if not task:
        abort(400)

    result['status'] = task.status
    if task.status == db_code.TASK_STATUS_COMPLETED:
        file_record = File.query.get(task.dst_file_id)
        if not file_record:
            abort(500)
        result['url'] = url_for('file.download', file_id=task.dst_file_id)
        result['filename'] = "%s%s" % (file_record.name, file_record.ext)

    return jsonify(result)


def save_file(file):
    filename = str(uuid.uuid4())
    path = os.path.join('/data/tmp', filename)
    file.save(path)
    size = os.stat(path).st_size
    name, ext = os.path.splitext(file.filename)

    file_record = File(name=name, ext=ext, size=size, path=path)
    db.session.add(file_record)
    db.session.flush()
    db.session.refresh(file_record)
    return file_record.id
