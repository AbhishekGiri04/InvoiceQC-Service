"""PDF extraction module - converts PDF invoices to JSON"""
import re
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any
import pdfplumber
from invoice_qc.schemas import Invoice, LineItem


def parse_date(date_str: str) -> str:
    """Parse date from various formats"""
    if not date_str:
        return None
    
    formats = ["%d.%m.%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y"]
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt).date().isoformat()
        except:
            continue
    return None


def parse_number(num_str: str) -> float:
    """Parse European and US number formats"""
    # Remove spaces
    num_str = num_str.replace(" ", "")
    # Check if European format (1.080,00)
    if "." in num_str and "," in num_str:
        # European: remove dots, replace comma with dot
        num_str = num_str.replace(".", "").replace(",", ".")
    else:
        # US format or simple: just replace comma with dot
        num_str = num_str.replace(",", ".")
    return float(num_str)


def extract_invoice_from_pdf(pdf_path: str) -> Invoice:
    """Extract invoice data from a single PDF file"""
    with pdfplumber.open(pdf_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ""
        
        # Extract invoice number
        invoice_number = None
        patterns = [
            r"Bestellung\s+([A-Z0-9]+)",
            r"Invoice\s*#?\s*:?\s*([A-Z0-9-]+)",
            r"Rechnung\s*#?\s*:?\s*([A-Z0-9-]+)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                invoice_number = match.group(1)
                break
        
        # Extract dates
        invoice_date = None
        date_match = re.search(r"vom\s+(\d{2}\.\d{2}\.\d{4})", text)
        if date_match:
            invoice_date = parse_date(date_match.group(1))
        
        # Extract seller info
        seller_name = None
        seller_match = re.search(r"^([A-Za-z\s]+(?:Corporation|GmbH|Ltd|Inc))", text, re.MULTILINE)
        if seller_match:
            seller_name = seller_match.group(1).strip()
        
        # Extract buyer info
        buyer_name = None
        buyer_match = re.search(r"Kundenanschrift\s+([^\n]+)", text)
        if buyer_match:
            buyer_name = buyer_match.group(1).strip()
        
        # Extract currency
        currency = None
        if "EUR" in text:
            currency = "EUR"
        elif "USD" in text or "$" in text:
            currency = "USD"
        elif "INR" in text or "₹" in text:
            currency = "INR"
        
        # Extract totals
        net_total = None
        tax_amount = None
        gross_total = None
        
        try:
            total_match = re.search(r"Gesamtwert\s+EUR\s+([\d]+[\.,][\d]+[\.,]?[\d]*)", text)
            if total_match:
                net_total = parse_number(total_match.group(1))
        except Exception as e:
            print(f"Error parsing net_total: {e}")
        
        try:
            tax_match = re.search(r"MwSt\.\s+[\d,]+%\s+EUR\s+([\d]+[\.,][\d]+[\.,]?[\d]*)", text)
            if tax_match:
                tax_amount = parse_number(tax_match.group(1))
        except Exception as e:
            print(f"Error parsing tax_amount: {e}")
        
        try:
            gross_match = re.search(r"Gesamtwert inkl\. MwSt\.\s+EUR\s+([\d]+[\.,][\d]+[\.,]?[\d]*)", text)
            if gross_match:
                gross_total = parse_number(gross_match.group(1))
        except Exception as e:
            print(f"Error parsing gross_total: {e}")
        
        # Extract line items from table
        line_items = []
        try:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row and len(row) >= 4:
                            try:
                                # Try to parse quantity and price
                                qty_str = str(row[2]) if len(row) > 2 else ""
                                price_str = str(row[3]) if len(row) > 3 else ""
                                total_str = str(row[-1]) if row else ""
                                
                                # Skip if any value is None or empty
                                if not qty_str or qty_str == 'None' or not price_str or price_str == 'None' or not total_str or total_str == 'None':
                                    continue
                                
                                # Clean and check if numeric
                                qty_clean = re.sub(r"[^\d,\.\s]", "", qty_str).strip()
                                price_clean = re.sub(r"[^\d,\.\s]", "", price_str).strip()
                                total_clean = re.sub(r"[^\d,\.\s]", "", total_str).strip()
                                
                                if qty_clean and price_clean and total_clean:
                                    qty = parse_number(qty_clean)
                                    price = parse_number(price_clean)
                                    total = parse_number(total_clean)
                                    
                                    line_items.append(LineItem(
                                        description=str(row[1]) if len(row) > 1 else "",
                                        quantity=qty,
                                        unit_price=price,
                                        line_total=total
                                    ))
                            except Exception as e:
                                print(f"Error parsing line item: {e}")
                                continue
        except Exception as e:
            print(f"Error extracting tables: {e}")
            pass
        
        return Invoice(
            invoice_number=invoice_number or "UNKNOWN",
            invoice_date=invoice_date,
            due_date=None,
            seller_name=seller_name,
            seller_address=None,
            seller_tax_id=None,
            buyer_name=buyer_name,
            buyer_address=None,
            buyer_tax_id=None,
            currency=currency,
            net_total=net_total,
            tax_amount=tax_amount,
            gross_total=gross_total,
            line_items=line_items
        )


def extract_from_directory(pdf_dir: str) -> List[Invoice]:
    """Extract invoices from all PDFs in a directory"""
    pdf_path = Path(pdf_dir)
    invoices = []
    
    for pdf_file in pdf_path.glob("*.pdf"):
        try:
            invoice = extract_invoice_from_pdf(str(pdf_file))
            invoices.append(invoice)
        except Exception as e:
            print(f"Error extracting {pdf_file}: {e}")
    
    return invoices
