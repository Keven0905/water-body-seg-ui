import os
from flask import Blueprint, send_file, abort
from config import Config

bp = Blueprint('results', __name__)


@bp.route('/results/<filename>')
def serve_result(filename):
    if '..' in filename or '/' in filename:
        abort(404)

    path = os.path.join(Config.RESULTS_DIR, filename)
    if not os.path.isfile(path):
        abort(404)

    return send_file(path, mimetype='image/png')
