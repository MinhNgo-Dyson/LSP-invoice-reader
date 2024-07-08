poppler_path = "Support/poppler-24.02.0/Library/bin"
tesseract_path = "Support/Tesseract-OCR/tesseract.exe"

import re

def get_lsp(lines):
    lsp_set = set()
    for line in lines:
        if 'ceva' in line.lower():
            lsp_set.add('ceva')
        if 'dhl' in line.lower():
            lsp_set.add('dhl')
        if 'maersk' in line.lower():
            lsp_set.add('maersk')

    lsp_list = list(lsp_set)
    if len(lsp_list) == 0:
        return None
    if len(lsp_list) > 1:
        return "Unknown: " + str(lsp_list)

    return lsp_list[0]

def extract_invoice_number_ceva(lines):
    for i, line in enumerate(lines):
        if re.search(r'INVOICE NUMBER', line, re.I):
            # Check the next line for the invoice number
            if i + 1 < len(lines):
                invoice_number_line = lines[i + 1]
                invoice_number_list = re.findall(r'\d+', invoice_number_line)
                if invoice_number_list:
                    invoice_number = invoice_number_list[0]
    return invoice_number

def extract_total_amount_ceva(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None
    
    for line in lines:
        match_usd = re.search(r'Total:\D*(\d+\.\d{2})', line, re.I)
        match_rate = re.search(r'EXCHANGERATE:\D*(\d+\.\d+)', line.replace(" ", ""), re.I)
        if match_usd:
            total_amount_usd = float(match_usd.group(1))
        if match_rate and not ex_rate:
            ex_rate = match_rate.group(1)
            ex_rate = float(round(1/float(ex_rate),4) if float(ex_rate) < 1 else round(float(ex_rate),4))
    return total_amount_usd, total_amount_myr, ex_rate


def extract_invoice_number_dhl(lines):
    for line in lines:
        match = re.search(r'INVOICE (W\d+)', line, re.I)
        if match:
            invoice_number =  match.group(1)
    return invoice_number

def extract_total_amount_dhl(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None

    for line in lines:
        match_usd = re.search(r'TOTALUSD\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_myr = re.search(r'MYRSUBTOTAL\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)

        if match_usd and not total_amount_usd:
            total_amount_usd = float(match_usd.group(1))
        if match_myr and not total_amount_myr:
            total_amount_myr = float(match_myr.group(1))
    return total_amount_usd, total_amount_myr, ex_rate


def extract_invoice_number_msk(lines):
    for line in lines:
        match = re.search(r'InvoiceNumber(\d+)', line.replace(" ", ""), re.I)
        if match:
            invoice_number =  match.group(1)
    return invoice_number

def extract_total_amount_msk(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None

    for line in lines:
        match_usd = re.search(r'TotalBaseAmount\W*USD\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_myr = re.search(r'TotalBaseAmount\W*MYR\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_rate = re.search(r'ExchangeRateConversionUSDtoMYR\D*(\d+\.\d+)', line.replace(" ", ""), re.I)
        if match_usd and not total_amount_usd:
            total_amount_usd = float(match_usd.group(1))
        if match_myr and not total_amount_myr:
            total_amount_myr = float(match_myr.group(1))
        if match_rate and not ex_rate:
            ex_rate = match_rate.group(1)
            ex_rate = float(round(1/float(ex_rate),4) if float(ex_rate) < 1 else round(float(ex_rate),4))

    return total_amount_usd, total_amount_myr, ex_rate
