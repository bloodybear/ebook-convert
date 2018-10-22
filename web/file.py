from flask import Blueprint, send_file, abort

from web.auth import login_required
from common.database.models import File

bp = Blueprint('file', __name__, url_prefix='/file')


@bp.route('/<int:file_id>')
@login_required
def download(file_id):
    file_record = File.query.get(file_id)
    if not file_record:
        abort(404)

    filepath = file_record.path
    filename = "%s%s" % (file_record.name, file_record.ext)

    return send_file(filepath, as_attachment=True, attachment_filename=filename)
