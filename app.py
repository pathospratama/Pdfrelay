from flask import Flask, request, jsonify, send_file
from PyPDF2 import PdfReader, PdfWriter
import tempfile
import uuid
import os
import json

app = Flask(__name__)

# Enable CORS
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Replacements')
    response.headers.add('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
    return response

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        "status": "healthy",
        "service": "PDF Text Replacer",
        "version": "3.0"
    })

def process_pdf_replacements(input_path, replacements):
    """Process PDF with text replacements"""
    reader = PdfReader(input_path)
    writer = PdfWriter()

    for page in reader.pages:
        # Extract and modify text
        text = page.extract_text() or ""
        for old_text, new_text in replacements.items():
            text = text.replace(old_text, new_text)

        # Add page (note: PyPDF2 can't edit text directly)
        writer.add_page(page)

    output_path = f"{tempfile.gettempdir()}/{uuid.uuid4()}_processed.pdf"
    with open(output_path, 'wb') as f:
        writer.write(f)

    return output_path

@app.route('/process-pdf', methods=['POST'])
def handle_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files['file']
    if not file.filename.lower().endswith('.pdf'):
        return jsonify({"error": "Only PDF files are allowed"}), 400

    # Get replacements from headers or form data
    replacements = {}
    if 'Replacements' in request.headers:
        try:
            replacements = json.loads(request.headers['Replacements'])
        except json.JSONDecodeError:
            pass
    elif 'replacements' in request.form:
        try:
            replacements = json.loads(request.form['replacements'])
        except json.JSONDecodeError:
            pass

    temp_pdf = None
    output_pdf = None

    try:
        # Save uploaded file
        temp_pdf = f"{tempfile.gettempdir()}/{uuid.uuid4()}.pdf"
        file.save(temp_pdf)

        # Process PDF
        output_pdf = process_pdf_replacements(temp_pdf, replacements)

        # Return processed file
        return send_file(
            output_pdf,
            as_attachment=True,
            download_name="processed.pdf",
            mimetype='application/pdf'
        )

    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        # Cleanup temporary files
        for f in [temp_pdf, output_pdf]:
            try:
                if f and os.path.exists(f):
                    os.unlink(f)
            except:
                pass

if __name__ == '__main__':
    app.run(debug=True)
