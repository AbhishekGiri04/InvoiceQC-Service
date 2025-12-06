"""Sample tests for validation engine"""
import pytest
from invoice_qc.schemas import Invoice, LineItem
from invoice_qc.rules import validate_invoice


def test_valid_invoice():
    """Test validation of a valid invoice"""
    invoice = Invoice(
        invoice_number="TEST001",
        invoice_date="2024-05-22",
        seller_name="Test Seller",
        buyer_name="Test Buyer",
        currency="EUR",
        net_total=100.0,
        tax_amount=19.0,
        gross_total=119.0,
        line_items=[]
    )
    
    is_valid, errors, warnings = validate_invoice(invoice)
    
    assert is_valid is True
    assert len(errors) == 0


def test_missing_required_fields():
    """Test validation fails when required fields are missing"""
    invoice = Invoice(
        invoice_number="",
        invoice_date=None,
        seller_name=None,
        buyer_name=None,
        currency="EUR",
        net_total=100.0,
        tax_amount=19.0,
        gross_total=119.0,
        line_items=[]
    )
    
    is_valid, errors, warnings = validate_invoice(invoice)
    
    assert is_valid is False
    assert len(errors) > 0


def test_invalid_currency():
    """Test validation fails for invalid currency"""
    invoice = Invoice(
        invoice_number="TEST001",
        invoice_date="2024-05-22",
        seller_name="Test Seller",
        buyer_name="Test Buyer",
        currency="XYZ",  # Invalid currency
        net_total=100.0,
        tax_amount=19.0,
        gross_total=119.0,
        line_items=[]
    )
    
    is_valid, errors, warnings = validate_invoice(invoice)
    
    assert is_valid is False
    assert any("currency" in error.lower() for error in errors)


def test_total_mismatch():
    """Test validation fails when totals don't match"""
    invoice = Invoice(
        invoice_number="TEST001",
        invoice_date="2024-05-22",
        seller_name="Test Seller",
        buyer_name="Test Buyer",
        currency="EUR",
        net_total=100.0,
        tax_amount=19.0,
        gross_total=200.0,  # Wrong total
        line_items=[]
    )
    
    is_valid, errors, warnings = validate_invoice(invoice)
    
    assert is_valid is False
    assert any("mismatch" in error.lower() for error in errors)


def test_negative_amounts():
    """Test validation fails for negative amounts"""
    invoice = Invoice(
        invoice_number="TEST001",
        invoice_date="2024-05-22",
        seller_name="Test Seller",
        buyer_name="Test Buyer",
        currency="EUR",
        net_total=-100.0,  # Negative
        tax_amount=19.0,
        gross_total=-81.0,
        line_items=[]
    )
    
    is_valid, errors, warnings = validate_invoice(invoice)
    
    assert is_valid is False
    assert any("negative" in error.lower() for error in errors)
