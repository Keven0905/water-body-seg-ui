import os
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.utils import secure_filename
from config import Config
from services.inference import segment
from services.history import add_record

bp = Blueprint('segmentation', __name__)


@bp.route('/api/segment', methods=['POST'])
def segment_image():
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': '未收到文件'}), 400

    file = request.files['file']
    if not file.filename:
        return jsonify({'success': False, 'error': '文件名为空'}), 400

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ('.jpg', '.jpeg'):
        return jsonify({'success': False, 'error': f'格式不支持: {ext}，仅接受 .jpg / .jpeg'}), 400

    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    temp_name = f'{uuid.uuid4().hex}{ext}'
    temp_path = os.path.join(Config.UPLOAD_DIR, temp_name)
    file.save(temp_path)

    try:
        result = segment(temp_path)
        add_record(
            original_name=file.filename,
            result_filename=result['filename'],
            composite_filename=result['composite_filename'],
            water_ratio=result['water_ratio'],
            water_pixels=result['water_pixels'],
            total_pixels=result['total_pixels'],
        )
        return jsonify({'success': True, **result})
    except Exception as e:
        return jsonify({'success': False, 'error': f'分割推理失败: {str(e)}'}), 500
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
