import os
import uuid
from werkzeug.utils import secure_filename
from .constants import ALLOWED_EXTENSIONS, TEMP_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def generate_temp_path(extension):
    """Generate secure temporary file path"""
    filename = f"{uuid.uuid4()}{extension}"
    return os.path.join(TEMP_FOLDER, filename)

def cleanup_files(*files):
    """Safely remove temporary files"""
    for filepath in files:
        try:
            if filepath and os.path.exists(filepath):
                os.unlink(filepath)
        except Exception as e:
            print(f"Error removing file {filepath}: {e}")