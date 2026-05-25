from flask import Blueprint, request, jsonify
from services.inference import get_metrics
from services.model_manager import allowed_file, save_model_file

bp = Blueprint('model', __name__)


@bp.route('/api/metrics', methods=['GET'])
def metrics():
    return jsonify(get_metrics())


@bp.route('/api/model/upload', methods=['POST'])
def upload_model():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未收到文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    if not allowed_file(file.filename):
        return jsonify({'success': False, 'error': '格式不支持，仅接受 .pth / .onnx / .pt / .h5'}), 400

    try:
        filename = save_model_file(file)
        return jsonify({'success': True, 'filename': filename})
    except Exception as e:
        return jsonify({'success': False, 'error': f'模型保存失败: {str(e)}'}), 500
