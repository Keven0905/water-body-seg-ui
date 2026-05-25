import os
from flask import Blueprint, jsonify, send_file, abort
from config import Config
from services.history import get_records, delete_record, get_record_by_id

bp = Blueprint('history', __name__)


@bp.route('/api/history', methods=['GET'])
def list_history():
    return jsonify(get_records())


@bp.route('/api/history/<int:record_id>', methods=['DELETE'])
def remove_record(record_id):
    if delete_record(record_id):
        return jsonify({'success': True})
    return jsonify({'success': False, 'error': '记录不存在'}), 404


@bp.route('/api/history/<int:record_id>/download', methods=['GET'])
def download_result(record_id):
    record = get_record_by_id(record_id)
    if not record:
        abort(404)
    fname = record.get('composite_filename') or record['result_filename']
    path = os.path.join(Config.RESULTS_DIR, fname)
    if not os.path.isfile(path):
        abort(404)
    download_name = f"water_seg_{record['original_name'].rsplit('.', 1)[0]}.png"
    return send_file(path, mimetype='image/png', as_attachment=True, download_name=download_name)
