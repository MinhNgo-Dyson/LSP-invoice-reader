import os
from datetime import datetime
import time

import pandas as pd
from pdf2image import convert_from_path
import pytesseract

from invoice_extract import extract_invoice_number_ceva, extract_total_amount_ceva, extract_invoice_number_dhl, extract_total_amount_dhl, extract_invoice_number_msk, extract_total_amount_msk, get_lsp

POPPLER_PATH = "./Support/poppler-24.02.0/Library/bin"
TESSERACT_PATH = "./Support/Tesseract-OCR/tesseract.exe"

def pdf_to_images(pdf_path, max_pages=3, poppler_path=None):
    if poppler_path:
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages, poppler_path=poppler_path)
    else:
        images = convert_from_path(pdf_path, first_page=1, last_page=max_pages)
    return images

def ocr_image(image, tesseract_path=None):
    if tesseract_path:
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    text = pytesseract.image_to_string(image)
    return text

def preprocess_text(text):
    lines = text.split('\n')
    lines = [line.strip() for line in lines if line.strip() != '']
    lines = [line.replace(",","") for line in lines]
    return lines

def process_invoice(pdf_path, poppler_path=None, tesseract_path=None):
    images = pdf_to_images(pdf_path, 3, poppler_path)
    text = ''.join([ocr_image(image, tesseract_path) for image in images])
    lines = preprocess_text(text)
    lsp = get_lsp(lines)

    if lsp == "ceva":
        invoice_number = extract_invoice_number_ceva(lines)
        total_amount_usd, total_amount_myr, exchange_rate = extract_total_amount_ceva(lines)
    elif lsp == "dhl":
        invoice_number = extract_invoice_number_dhl(lines)
        total_amount_usd, total_amount_myr, exchange_rate = extract_total_amount_dhl(lines)
    elif lsp == "maersk":
        invoice_number = extract_invoice_number_msk(lines)
        total_amount_usd, total_amount_myr, exchange_rate = extract_total_amount_msk(lines)
    
    return {
        'lsp': lsp,
        'invoice_number': invoice_number,
        'total_amount_usd': total_amount_usd,
        'total_amount_myr': total_amount_myr,
        'exchange_rate': exchange_rate
    }

def process_invoices_in_folder(folder_path, poppler_path=None, tesseract_path=None):
    results = []
    for root, _, files in os.walk(folder_path):
        for filename in files:
            if filename.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, filename)
                result = process_invoice(pdf_path, poppler_path, tesseract_path)
                result['file'] = pdf_path
                results.append(result)
    return results

def export_to_excel(results, output_folder_path):
    df = pd.DataFrame(results)

    # Create output path based on current timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_excel = output_folder_path + f"\invoices_{timestamp}.xlsx"

    df.to_excel(output_excel, index=False)
    return None

if __name__ == "__main__":
    try:
        folder_path = input("What is the invoice folder?").replace("\"", "").replace("\'", "")
        # Start the timer
        start_time = time.time()
        print("Processing invoices ...")
        results = process_invoices_in_folder(folder_path, POPPLER_PATH, TESSERACT_PATH)
        # End the timer
        end_time = time.time()

        elapsed_time = end_time - start_time
        print(f"The code took {elapsed_time:.4f} seconds to run.")
        
        output_folder_path = input("What is the export folder?").replace("\"", "").replace("\'", "")
        export_to_excel(results, output_folder_path)
        print("Exporting invoices ...")
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        input("Press Enter to exit...")
        