import re


def get_lsp(lines):
    lsp_set = set()
    for line in lines:
        if 'ceva freight' in line.lower():
            lsp_set.add('ceva')
        if 'dhl global' in line.lower():
            lsp_set.add('dhl')
        if 'maersk malaysia' in line.lower():
            lsp_set.add('maersk')

    lsp_list = list(lsp_set)
    if len(lsp_list) == 0:
        return "Unknown"
    if len(lsp_list) > 1:
        return "Unknown: " + str(lsp_list)

    return lsp_list[0]


def extract_invoice_number_ceva(lines):
    invoice_number = "Unknown"
    for i, line in enumerate(lines):
        if re.search(r'INVOICE NUMBER', line, re.I):
            # Check the next line for the invoice number
            if i + 1 < len(lines):
                invoice_number_line = lines[i + 1]
                invoice_number_list = re.findall(r'\d+', invoice_number_line)
                if invoice_number_list:
                    invoice_number = invoice_number_list[0]
                    return invoice_number
    return None


def extract_total_amount_ceva(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None

    for i, line in enumerate(lines):
        match_myr = re.search(r'(\d+\.\d{2})MYR', line.replace(" ", ""), re.I)
        match_usd = re.search(r'(\d+\.\d{2})USD', line.replace(" ", ""), re.I)
        match_rate_temp = re.search(
            r'(?<!Tax)EXCHANGERATE', line.replace(" ", ""), re.I)
        if match_myr:
            total_amount_myr = float(match_myr.group(1))
        if match_usd:
            total_amount_usd = float(match_usd.group(1))

        if match_rate_temp and not ex_rate:
            if i + 1 < len(lines):
                next_line = lines[i+1]
                match_usd_rate = re.search(
                    r'(\d+\.\d{2})USDx(\d+\.\d{6})', next_line.replace(" ", ""), re.I)
                if match_usd_rate:
                    total_amount_usd = float(match_usd_rate.group(1))
                    ex_rate = float(match_usd_rate.group(2))

    return total_amount_usd, total_amount_myr, ex_rate


def extract_invoice_number_dhl(lines):
    invoice_number = "Unknown"
    for line in lines:
        match = re.search(r'INVOICE (W\d+)', line, re.I)
        if match:
            invoice_number = match.group(1)

    return invoice_number


def extract_total_amount_dhl(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None

    for line in lines:
        match_usd = re.search(
            r'TOTALUSD\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_myr = re.search(
            r'(?:MYRSUBTOTAL|TOTALMYR)\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_rate = re.search(
            r'USD\d+\.\d{2}@(\d+\.\d{6})', line.replace(" ", ""), re.I)

        if match_usd and not total_amount_usd:
            total_amount_usd = float(match_usd.group(1))
        if match_myr and not total_amount_myr:
            total_amount_myr = float(match_myr.group(1))
        if match_rate and not ex_rate:
            ex_rate = float(match_rate.group(1))
    return total_amount_usd, total_amount_myr, ex_rate


def extract_invoice_number_msk(lines):
    invoice_number = "Unknown"
    for line in lines:
        match = re.search(r'InvoiceNumber(\d+)', line.replace(" ", ""), re.I)
        if match:
            invoice_number = match.group(1)
    return invoice_number


def extract_total_amount_msk(lines):
    total_amount_usd = None
    total_amount_myr = None
    ex_rate = None

    for line in lines:
        match_usd = re.search(
            r'TotalBaseAmount\W*USD\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_myr = re.search(
            r'TotalBaseAmount\W*MYR\D*(\d+\.\d{2})', line.replace(" ", ""), re.I)
        match_rate = re.search(
            r'ExchangeRateConversionUSDtoMYR\D*(\d+\.\d+)', line.replace(" ", ""), re.I)
        if match_usd and not total_amount_usd:
            total_amount_usd = float(match_usd.group(1))
        if match_myr and not total_amount_myr:
            total_amount_myr = float(match_myr.group(1))
        if match_rate and not ex_rate:
            ex_rate = match_rate.group(1)
            ex_rate = float(round(1/float(ex_rate), 4)
                            if float(ex_rate) < 1 else round(float(ex_rate), 4))

    return total_amount_usd, total_amount_myr, ex_rate
