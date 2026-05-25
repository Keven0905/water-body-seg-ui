import numpy as np
from PIL import Image


def cvtColor(image):
    """Ensure image is RGB. Supports PIL Image and numpy array inputs."""
    if isinstance(image, np.ndarray):
        if len(image.shape) == 3 and image.shape[2] == 3:
            return image
        else:
            return np.array(Image.fromarray(image).convert('RGB'))
    else:
        if image.mode == 'RGB':
            return image
        else:
            return image.convert('RGB')


def resize_image(image, size):
    """Letterbox resize preserving aspect ratio with gray (128,128,128) padding."""
    iw, ih = image.size
    w, h = size
    scale = min(w / iw, h / ih)
    nw = int(iw * scale)
    nh = int(ih * scale)

    image = image.resize((nw, nh), Image.BICUBIC)
    new_image = Image.new('RGB', size, (128, 128, 128))
    new_image.paste(image, ((w - nw) // 2, (h - nh) // 2))
    return new_image, nw, nh


def preprocess_input(image):
    """Scale image pixels from [0,255] to [0,1]."""
    image /= 255.0
    return image
