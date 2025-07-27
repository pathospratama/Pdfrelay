import os
import json
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from werkzeug.utils import secure_filename
from ilovepdf import ILovePdf
from docx import Document
from dotenv import load_dotenv

# Load API key
load_dotenv()
ILOVEPDF_PUBLIC_KEY = os.getenv('ILOVEPDF_PUBLIC_KEY')
ilovepdf = ILovePdf(ILOVEPDF_PUBLIC_KEY, verify_ssl=True)

# Flask init
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

@app.route('/')
def index():
    return jsonify({"message": "Server iLovePDF Replacement is running."})

@app.route('/replace-pdf-text', methods=['POST'])
def replace_pdf_text():
    if 'file' not in request.files:
        return jsonify({'error': 'File tidak ditemukan'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'File kosong'}), 400

    filename = secure_filename(file.filename)
    filepath_pdf = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath_pdf)

    # Parse replacements
    try:
        replacements_raw = request.form.get('replacements', '{}')
        replacements = json.loads(replacements_raw)
    except Exception as e:
        return jsonify({'error': 'Format replacement tidak valid'}), 400

    try:
        # 1. Convert PDF to DOCX
        task = ilovepdf.new_task('pdf2word')
        task.add_file(filepath_pdf)
        task.set_output_folder(OUTPUT_FOLDER)
        task.execute()
        task.download()
        task.delete_current_task()

        # 2. Temukan file DOCX hasil convert
        docx_file = None
        for f in os.listdir(OUTPUT_FOLDER):
            if f.endswith('.docx'):
                docx_file = os.path.join(OUTPUT_FOLDER, f)
                break

        if not docx_file:
            return jsonify({'error': 'DOCX hasil konversi tidak ditemukan'}), 500

        # 3. Edit teks DOCX
        edit_docx_text(docx_file, replacements)

        # 4. Convert kembali ke PDF
        task2 = ilovepdf.new_task('officepdf')
        task2.add_file(docx_file)
        task2.set_output_folder(OUTPUT_FOLDER)
        task2.execute()
        task2.download()
        task2.delete_current_task()

        # 5. Kirim file PDF hasil edit
        for f in os.listdir(OUTPUT_FOLDER):
            if f.endswith('.pdf'):
                final_pdf = os.path.join(OUTPUT_FOLDER, f)
                return send_file(final_pdf, as_attachment=True)

        return jsonify({'error': 'Gagal mengubah ke PDF'}), 500

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
