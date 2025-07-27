import os
import json
import requests
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from docx import Document
from dotenv import load_dotenv
import uuid

# Load API key dari .env
load_dotenv()
ILOVEPDF_PUBLIC_KEY = os.getenv('ILOVEPDF_PUBLIC_KEY')

# Flask setup
app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = 'uploads'
OUTPUT_FOLDER = 'outputs'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def edit_docx_text(docx_path, replacements):
    doc = Document(docx_path)

    def replace_runs(runs, replacements):
        for run in runs:
            for old, new in replacements.items():
                if old in run.text:
                    run.text = run.text.replace(old, new)

    for para in doc.paragraphs:
        replace_runs(para.runs, replacements)

    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    replace_runs(para.runs, replacements)

    doc.save(docx_path)

def convert_pdf_to_word(input_pdf, output_docx):
    # 1. Start session
    start_url = 'https://api.ilovepdf.com/v1/start/pdf2word'
    res = requests.post(start_url, json={"public_key": ILOVEPDF_PUBLIC_KEY})
    data = res.json()
    server = data['server']
    task = data['task']

    # 2. Upload file
    with open(input_pdf, 'rb') as f:
        upload_url = f'https://{server}/v1/upload'
        files = {'file': (os.path.basename(input_pdf), f)}
        requests.post(upload_url, data={'task': task}, files=files)

    # 3. Process
    process_url = f'https://{server}/v1/process'
    requests.post(process_url, json={'task': task})

    # 4. Download DOCX
    download_url = f'https://{server}/v1/download/{task}'
    response = requests.get(download_url, stream=True)
    with open(output_docx, 'wb') as out_file:
        for chunk in response.iter_content(chunk_size=8192):
            out_file.write(chunk)

def convert_word_to_pdf(input_docx, output_pdf):
    # 1. Start session
    start_url = 'https://api.ilovepdf.com/v1/start/officepdf'
    res = requests.post(start_url, json={"public_key": ILOVEPDF_PUBLIC_KEY})
    data = res.json()
    server = data['server']
    task = data['task']

    # 2. Upload file
    with open(input_docx, 'rb') as f:
        upload_url = f'https://{server}/v1/upload'
        files = {'file': (os.path.basename(input_docx), f)}
        requests.post(upload_url, data={'task': task}, files=files)

    # 3. Process
    process_url = f'https://{server}/v1/process'
    requests.post(process_url, json={'task': task})

    # 4. Download PDF
    download_url = f'https://{server}/v1/download/{task}'
    response = requests.get(download_url, stream=True)
    with open(output_pdf, 'wb') as out_file:
        for chunk in response.iter_content(chunk_size=8192):
            out_file.write(chunk)

@app.route('/')
def index():
    return jsonify({"message": "iLovePDF Replacement API is running."})

@app.route('/replace-pdf-text', methods=['POST'])
def replace_pdf_text():
    if 'file' not in request.files:
        return jsonify({'error': 'File tidak ditemukan'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'File kosong'}), 400

    filename = secure_filename(file.filename)
    filepath_pdf = os.path.join(UPLOAD_FOLDER, f"{uuid.uuid4()}_{filename}")
    file.save(filepath_pdf)

    # Parse replacements
    try:
        replacements_raw = request.form.get('replacements', '{}')
        replacements = json.loads(replacements_raw)
    except Exception:
        return jsonify({'error': 'Format replacement tidak valid'}), 400

    try:
        # Konversi PDF → DOCX
        docx_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.docx")
        convert_pdf_to_word(filepath_pdf, docx_path)

        # Edit teks
        edit_docx_text(docx_path, replacements)

        # Konversi kembali DOCX → PDF
        output_pdf_path = os.path.join(OUTPUT_FOLDER, f"{uuid.uuid4()}.pdf")
        convert_word_to_pdf(docx_path, output_pdf_path)

        # Kirim hasilnya
        return send_file(output_pdf_path, as_attachment=True)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
