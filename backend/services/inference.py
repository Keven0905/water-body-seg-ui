import os
import uuid
import numpy as np
from PIL import Image
import torch
import torch.nn.functional as F

from config import Config
from services.preprocess import cvtColor, resize_image, preprocess_input

_device = None
_model = None


def _get_device():
    global _device
    if _device is None:
        _device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    return _device


def _get_model():
    global _model
    if _model is None:
        from models.nets.unet import Unet

        _model = Unet(num_classes=Config.NUM_CLASSES, backbone=Config.BACKBONE)
        device = _get_device()

        if os.path.exists(Config.MODEL_WEIGHTS_PATH):
            state = torch.load(Config.MODEL_WEIGHTS_PATH, map_location=device)
            _model.load_state_dict(state)
        else:
            raise FileNotFoundError(f'Model weights not found: {Config.MODEL_WEIGHTS_PATH}')

        _model.to(device)
        _model.eval()
    return _model


def reload_model():
    global _model, _device
    from models.nets.unet import Unet

    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    new_model = Unet(num_classes=Config.NUM_CLASSES, backbone=Config.BACKBONE)

    if os.path.exists(Config.MODEL_WEIGHTS_PATH):
        state = torch.load(Config.MODEL_WEIGHTS_PATH, map_location=device)
        new_model.load_state_dict(state)
    else:
        raise FileNotFoundError(f'Model weights not found: {Config.MODEL_WEIGHTS_PATH}')

    new_model.to(device)
    new_model.eval()

    # Swap only after successful load — old model stays alive on failure
    _model = new_model
    _device = device
    return _model


def _cleanup_old_results():
    try:
        import time
        cutoff = time.time() - 24 * 3600
        results_dir = Config.RESULTS_DIR
        if not os.path.isdir(results_dir):
            return
        for fname in os.listdir(results_dir):
            if fname.lower().endswith('.png'):
                fpath = os.path.join(results_dir, fname)
                if os.path.getmtime(fpath) < cutoff:
                    try:
                        os.remove(fpath)
                    except OSError:
                        pass
    except Exception:
        pass


def segment(image_path: str) -> dict:
    _cleanup_old_results()

    model = _get_model()
    device = _get_device()

    # --- Preprocessing (matching user's detect_image pipeline) ---
    img = Image.open(image_path)
    img = cvtColor(img)
    original_w, original_h = img.size

    img_resized, nw, nh = resize_image(img, (Config.INPUT_SHAPE[1], Config.INPUT_SHAPE[0]))

    img_data = np.array(img_resized, dtype=np.float32)
    img_data = preprocess_input(img_data)
    img_data = np.transpose(img_data, (2, 0, 1))
    img_data = np.expand_dims(img_data, 0)

    # --- Forward pass ---
    with torch.no_grad():
        images = torch.from_numpy(img_data).to(device)
        pr = model(images)[0]
        pr = F.softmax(pr.permute(1, 2, 0), dim=-1).cpu().numpy()

    # --- Postprocessing ---
    pr = pr[int((Config.INPUT_SHAPE[0] - nh) // 2): int((Config.INPUT_SHAPE[0] - nh) // 2 + nh),
           int((Config.INPUT_SHAPE[1] - nw) // 2): int((Config.INPUT_SHAPE[1] - nw) // 2 + nw)]

    import cv2
    pr = cv2.resize(pr, (original_w, original_h), interpolation=cv2.INTER_LINEAR)
    water_prob = pr[:, :, 1]  # class-1 (water body) probability
    is_water = water_prob > 0.5

    total_pixels = int(original_w * original_h)
    water_pixels = int(is_water.sum())

    # Build RGBA overlay: water = semi-transparent blue, non-water = transparent
    rgba = np.zeros((original_h, original_w, 4), dtype=np.uint8)
    rgba[is_water, 0] = 0       # R
    rgba[is_water, 1] = 140     # G
    rgba[is_water, 2] = 255     # B
    rgba[is_water, 3] = 160     # A

    overlay_img = Image.fromarray(rgba, mode='RGBA')
    overlay_filename = _save_result(overlay_img)

    # Composited image: original + water overlay blended
    composite = img.copy().convert('RGBA')
    composite = Image.alpha_composite(composite, overlay_img)
    composite_filename = _save_result(composite)

    return {
        'filename': overlay_filename,
        'composite_filename': composite_filename,
        'water_pixels': water_pixels,
        'total_pixels': total_pixels,
        'water_ratio': round(water_pixels / total_pixels * 100, 2),
    }


def _save_result(img):
    filename = f'{uuid.uuid4().hex}.png'
    save_path = os.path.join(Config.RESULTS_DIR, filename)
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)
    img.save(save_path, 'PNG')
    return filename


def get_metrics():
    return {
        'accuracy': 96.93,
        'f1_score': 94.90,
        'miou': 90.61,
        'mpa': 94.62,
        'mprecision': 95.57,
    }
