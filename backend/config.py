import os


class Config:
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    UPLOAD_DIR = os.path.join(BASE_DIR, 'uploads')
    RESULTS_DIR = os.path.join(UPLOAD_DIR, 'results')
    MODEL_DIR = os.path.join(BASE_DIR, 'saved_models')

    # Model parameters (matching user's best_epoch_weights.pth)
    NUM_CLASSES = 2
    BACKBONE = 'resnet50'
    INPUT_SHAPE = (512, 512)

    # Path to user-trained weights
    MODEL_WEIGHTS_PATH = os.path.join(BASE_DIR, 'saved_models', 'best_epoch_weights.pth')

    MAX_CONTENT_LENGTH_UPPER = 32 * 1024 * 1024  # 32MB
    SECRET_KEY = 'water-body-seg-secret-key-2026'
