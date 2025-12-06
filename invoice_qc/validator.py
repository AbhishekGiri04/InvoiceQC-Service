"""Validation engine - applies rules to invoices"""
from typing import List
from invoice_qc.schemas import Invoice, ValidationResult, QCReport
from invoice_qc.rules import validate_invoice


def validate_invoices(invoices: List[Invoice]) -> QCReport:
    """Validate a list of invoices and generate QC report"""
    results = []
    
    for invoice in invoices:
        is_valid, errors, warnings = validate_invoice(invoice)
        
        result = ValidationResult(
            invoice_number=invoice.invoice_number,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings
        )
        results.append(result)
    
    valid_count = sum(1 for r in results if r.is_valid)
    
    return QCReport(
        total_invoices=len(invoices),
        valid_invoices=valid_count,
        invalid_invoices=len(invoices) - valid_count,
        results=results
    )
