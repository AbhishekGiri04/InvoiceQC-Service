"""Validation rules for invoice QC"""
from typing import List, Tuple
from invoice_qc.schemas import Invoice


def check_completeness(invoice: Invoice) -> List[str]:
    """Check if required fields are present"""
    errors = []
    
    if not invoice.invoice_number or invoice.invoice_number == "UNKNOWN":
        errors.append("Missing invoice_number")
    
    if not invoice.invoice_date:
        errors.append("Missing invoice_date")
    
    if not invoice.seller_name:
        errors.append("Missing seller_name")
    
    if not invoice.buyer_name:
        errors.append("Missing buyer_name")
    
    return errors


def check_format(invoice: Invoice) -> List[str]:
    """Check if fields have correct format"""
    errors = []
    
    if invoice.currency and invoice.currency not in ["INR", "USD", "EUR"]:
        errors.append(f"Invalid currency: {invoice.currency}")
    
    return errors


def check_business_rules(invoice: Invoice) -> Tuple[List[str], List[str]]:
    """Check business logic rules"""
    errors = []
    warnings = []
    
    # Check totals calculation
    if invoice.net_total is not None and invoice.tax_amount is not None and invoice.gross_total is not None:
        calculated = round(invoice.net_total + invoice.tax_amount, 2)
        actual = round(invoice.gross_total, 2)
        if abs(calculated - actual) > 0.1:
            errors.append(f"Total mismatch: net({invoice.net_total}) + tax({invoice.tax_amount}) != gross({invoice.gross_total})")
    
    # Check due date >= invoice date
    if invoice.due_date and invoice.invoice_date:
        if invoice.due_date < invoice.invoice_date:
            errors.append("due_date is before invoice_date")
    
    # Check line items sum
    if invoice.line_items and invoice.net_total is not None:
        line_sum = sum(item.line_total for item in invoice.line_items)
        if abs(line_sum - invoice.net_total) > 0.1:
            warnings.append(f"Line items sum({line_sum}) != net_total({invoice.net_total})")
    
    return errors, warnings


def check_anomalies(invoice: Invoice) -> List[str]:
    """Check for anomalies"""
    errors = []
    
    if invoice.net_total is not None and invoice.net_total < 0:
        errors.append("Negative net_total")
    
    if invoice.tax_amount is not None and invoice.tax_amount < 0:
        errors.append("Negative tax_amount")
    
    if invoice.gross_total is not None and invoice.gross_total < 0:
        errors.append("Negative gross_total")
    
    return errors


def validate_invoice(invoice: Invoice) -> Tuple[bool, List[str], List[str]]:
    """Run all validation rules on an invoice"""
    all_errors = []
    all_warnings = []
    
    all_errors.extend(check_completeness(invoice))
    all_errors.extend(check_format(invoice))
    
    business_errors, business_warnings = check_business_rules(invoice)
    all_errors.extend(business_errors)
    all_warnings.extend(business_warnings)
    
    all_errors.extend(check_anomalies(invoice))
    
    is_valid = len(all_errors) == 0
    
    return is_valid, all_errors, all_warnings
