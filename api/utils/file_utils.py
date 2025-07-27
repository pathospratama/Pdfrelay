import os
import uuid

def allowed_file(filename):
    return '.' in filename and filename.lower().endswith('.pdf')

def generate_temp_path(extension='.pdf'):
    return f"/tmp/{uuid.uuid4()}{extension}"

def cleanup_files(*file_paths):
    for path in file_paths:
        try:
            if path and os.path.exists(path):
                os.unlink(path)
        except:
            pass