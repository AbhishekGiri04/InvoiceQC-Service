"""Pydantic schemas for invoice data"""
from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field


class LineItem(BaseModel):
    """Line item in an invoice"""
    description: str
    quantity: float
    unit_price: float
    line_total: float


class Invoice(BaseModel):
    """Complete invoice schema"""
    invoice_number: str
    invoice_date: Optional[date] = None
    due_date: Optional[date] = None
    seller_name: Optional[str] = None
    seller_address: Optional[str] = None
    seller_tax_id: Optional[str] = None
    buyer_name: Optional[str] = None
    buyer_address: Optional[str] = None
    buyer_tax_id: Optional[str] = None
    currency: Optional[str] = None
    net_total: Optional[float] = None
    tax_amount: Optional[float] = None
    gross_total: Optional[float] = None
    line_items: List[LineItem] = Field(default_factory=list)


class ValidationResult(BaseModel):
    """Result of validation for a single invoice"""
    invoice_number: str
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)


class QCReport(BaseModel):
    """Complete QC report for multiple invoices"""
    total_invoices: int
    valid_invoices: int
    invalid_invoices: int
    results: List[ValidationResult]
