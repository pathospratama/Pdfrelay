from flask import request, jsonify, send_file
from .utils.file_utils import allowed_file, generate_temp_path, cleanup_files
from .utils.pdf_utils import process_pdf_text_replacements
import os

def handler(request):
    if request.method != 'POST':
        return jsonify({"error": "Method not allowed"}), 405
    
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    
    file = request.files['file']
    if not file or not allowed_file(file.filename):
        return jsonify({"error": "Invalid PDF file"}), 400
    
    temp_pdf = None
    output_pdf = None
    
    try:
        # Save uploaded file
        temp_pdf = generate_temp_path()
        file.save(temp_pdf)
        
        # Process PDF
        replacements = request.form.get('replacements', {})
        output_pdf = process_pdf_text_replacements(temp_pdf, replacements)
        
        # Return processed file
        return send_file(
            output_pdf,
            as_attachment=True,
            download_name=f"processed_{file.filename}",
            mimetype='application/pdf'
        )
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        cleanup_files(temp_pdf, output_pdf)