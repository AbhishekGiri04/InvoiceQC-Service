"""CLI tool for invoice extraction and validation"""
import json
from pathlib import Path
import typer
from invoice_qc.extractor import extract_from_directory, extract_invoice_from_pdf
from invoice_qc.validator import validate_invoices
from invoice_qc.schemas import Invoice

app = typer.Typer()


@app.command()
def extract(
    pdf_dir: str = typer.Option(..., help="Directory containing PDF files"),
    output: str = typer.Option(..., help="Output JSON file path")
):
    """Extract invoices from PDFs to JSON"""
    typer.echo(f"Extracting invoices from {pdf_dir}...")
    
    invoices = extract_from_directory(pdf_dir)
    
    # Convert to dict
    invoices_dict = [inv.model_dump(mode='json') for inv in invoices]
    
    # Save to file
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output, 'w') as f:
        json.dump(invoices_dict, f, indent=2)
    
    typer.echo(f"✓ Extracted {len(invoices)} invoices to {output}")


@app.command()
def validate(
    input: str = typer.Option(..., help="Input JSON file with invoices"),
    report: str = typer.Option(..., help="Output QC report JSON file")
):
    """Validate invoices from JSON and generate QC report"""
    typer.echo(f"Validating invoices from {input}...")
    
    # Load invoices
    with open(input, 'r') as f:
        invoices_data = json.load(f)
    
    invoices = [Invoice(**inv) for inv in invoices_data]
    
    # Validate
    qc_report = validate_invoices(invoices)
    
    # Save report
    report_path = Path(report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report, 'w') as f:
        json.dump(qc_report.model_dump(mode='json'), f, indent=2)
    
    typer.echo(f"✓ Validation complete:")
    typer.echo(f"  Total: {qc_report.total_invoices}")
    typer.echo(f"  Valid: {qc_report.valid_invoices}")
    typer.echo(f"  Invalid: {qc_report.invalid_invoices}")
    typer.echo(f"  Report saved to {report}")


@app.command()
def full_run(
    pdf_dir: str = typer.Option(..., help="Directory containing PDF files"),
    report: str = typer.Option(..., help="Output QC report JSON file")
):
    """Extract PDFs and validate in one step"""
    typer.echo(f"Running full pipeline on {pdf_dir}...")
    
    # Extract
    invoices = extract_from_directory(pdf_dir)
    typer.echo(f"✓ Extracted {len(invoices)} invoices")
    
    # Validate
    qc_report = validate_invoices(invoices)
    
    # Save report
    report_path = Path(report)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(report, 'w') as f:
        json.dump(qc_report.model_dump(mode='json'), f, indent=2)
    
    typer.echo(f"✓ Validation complete:")
    typer.echo(f"  Total: {qc_report.total_invoices}")
    typer.echo(f"  Valid: {qc_report.valid_invoices}")
    typer.echo(f"  Invalid: {qc_report.invalid_invoices}")
    typer.echo(f"  Report saved to {report}")


if __name__ == "__main__":
    app()
