import os
import shutil
from werkzeug.utils import secure_filename
from config import Config
from services.inference import reload_model


ALLOWED_EXTENSIONS = {'.pth', '.onnx', '.pt', '.h5'}


def allowed_file(filename: str) -> bool:
    ext = os.path.splitext(filename)[1].lower()
    return ext in ALLOWED_EXTENSIONS


def save_model_file(file_storage) -> str:
    filename = secure_filename(file_storage.filename)
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    save_path = os.path.join(Config.MODEL_DIR, filename)
    file_storage.save(save_path)

    if filename.lower().endswith('.pth'):
        default_path = Config.MODEL_WEIGHTS_PATH
        shutil.copy(save_path, default_path)
        reload_model()

    return filename
