"""FastAPI main application"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from invoice_qc.api.routes import router

app = FastAPI(
    title="Invoice QC Service",
    description="PDF Invoice Extraction and Validation API",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)


@app.get("/")
def root():
    return {
        "service": "Invoice QC Service",
        "version": "1.0.0",
        "endpoints": ["/health", "/validate-json", "/extract-and-validate"]
    }
