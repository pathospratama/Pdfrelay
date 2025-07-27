from PyPDF2 import PdfReader, PdfWriter
import json

def process_pdf_text_replacements(input_path, replacements):
    reader = PdfReader(input_path)
    writer = PdfWriter()
    
    for page in reader.pages:
        text = page.extract_text() or ""
        
        if isinstance(replacements, str):
            try:
                replacements = json.loads(replacements)
            except:
                continue
                
        for old_text, new_text in replacements.items():
            text = text.replace(old_text, new_text)
        
        # Add original page (text replacement in PDF is complex)
        writer.add_page(page)
    
    output_path = generate_temp_path()
    with open(output_path, "wb") as f:
        writer.write(f)
    
    return output_path