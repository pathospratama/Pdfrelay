from http.server import BaseHTTPRequestHandler
from io import BytesIO
import json
import os
import uuid
from PyPDF2 import PdfReader, PdfWriter

class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if '?health=1' in self.path:
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({
                "status": "healthy",
                "version": "2.1"
            }).encode())
            return

        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({
            "error": "Not found",
            "available_endpoints": {
                "POST /api/process-pdf": "Process PDF file",
                "GET /health": "Health check"
            }
        }).encode())

    def do_POST(self):
        if self.path != '/api/process-pdf':
            self.send_response(404)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": "Endpoint not found"}).encode())
            return

        try:
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            
            # Simpan file sementara
            temp_pdf = f"/tmp/{uuid.uuid4()}.pdf"
            with open(temp_pdf, 'wb') as f:
                f.write(post_data)
            
            # Proses PDF (contoh: reverse halaman)
            reader = PdfReader(temp_pdf)
            writer = PdfWriter()
            
            for page in reader.pages:
                writer.add_page(page)
            
            output = BytesIO()
            writer.write(output)
            pdf_data = output.getvalue()
            
            # Hapus file temp
            os.unlink(temp_pdf)
            
            # Kirim response
            self.send_response(200)
            self.send_header('Content-type', 'application/pdf')
            self.send_header('Content-Disposition', 'attachment; filename="processed.pdf"')
            self.end_headers()
            self.wfile.write(pdf_data)
            
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

# Catatan: Untuk Vercel, handler class harus bernama 'handler'
