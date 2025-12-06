"""API routes for invoice QC operations"""
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException
from invoice_qc.schemas import Invoice, QCReport
from invoice_qc.validator import validate_invoices
from invoice_qc.extractor import extract_invoice_from_pdf
import tempfile
import os

router = APIRouter()


@router.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "invoice-qc-service"}


@router.post("/validate-json", response_model=QCReport)
def validate_json(invoices: List[Invoice]):
    """Validate invoices from JSON payload"""
    try:
        qc_report = validate_invoices(invoices)
        return qc_report
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/extract-and-validate", response_model=QCReport)
async def extract_and_validate_pdfs(files: List[UploadFile] = File(...)):
    """Extract and validate invoices from uploaded PDF files"""
    try:
        invoices = []
        
        for file in files:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                content = await file.read()
                tmp.write(content)
                tmp_path = tmp.name
            
            try:
                # Extract invoice
                invoice = extract_invoice_from_pdf(tmp_path)
                invoices.append(invoice)
            finally:
                # Clean up temp file
                os.unlink(tmp_path)
        
        # Validate all invoices
        qc_report = validate_invoices(invoices)
        return qc_report
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
