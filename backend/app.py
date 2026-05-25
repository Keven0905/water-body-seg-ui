import os
import sys

# Ensure backend dir is on path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, send_from_directory
from flask_cors import CORS
from config import Config
from routes.segmentation import bp as seg_bp
from routes.results import bp as results_bp
from routes.model import bp as model_bp
from routes.auth import bp as auth_bp
from routes.history import bp as history_bp
from auth_middleware import init_auth_middleware


def create_app():
    app = Flask(__name__, static_folder=None)
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH_UPPER

    CORS(app, supports_credentials=True)

    init_auth_middleware(app)

    app.register_blueprint(auth_bp)
    app.register_blueprint(seg_bp)
    app.register_blueprint(results_bp)
    app.register_blueprint(model_bp)
    app.register_blueprint(history_bp)

    # Production: serve Vite-built dist/ as SPA
    dist_dir = os.path.join(os.path.dirname(Config.BASE_DIR), 'dist')
    if os.path.isdir(dist_dir):

        @app.route('/')
        def serve_index():
            return send_from_directory(dist_dir, 'index.html')

        @app.route('/assets/<path:filename>')
        def serve_assets(filename):
            return send_from_directory(os.path.join(dist_dir, 'assets'), filename)

        @app.route('/<path:filename>')
        def serve_static(filename):
            path = os.path.join(dist_dir, filename)
            if os.path.isfile(path):
                return send_from_directory(dist_dir, filename)
            # SPA fallback
            return send_from_directory(dist_dir, 'index.html')

    return app


if __name__ == '__main__':
    app = create_app()
    os.makedirs(Config.UPLOAD_DIR, exist_ok=True)
    os.makedirs(Config.RESULTS_DIR, exist_ok=True)
    os.makedirs(Config.MODEL_DIR, exist_ok=True)
    print(f'Backend running at http://localhost:5000')
    print(f'Results dir: {Config.RESULTS_DIR}')
    print(f'Model dir: {Config.MODEL_DIR}')
    app.run(host='0.0.0.0', port=5000, debug=True)
