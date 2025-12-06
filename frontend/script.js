const API_URL = 'http://localhost:8000';

document.getElementById('uploadBtn').addEventListener('click', async () => {
    const fileInput = document.getElementById('fileInput');
    const files = fileInput.files;
    
    if (files.length === 0) {
        alert('Please select PDF files to upload');
        return;
    }
    
    const loading = document.getElementById('loading');
    const results = document.getElementById('results');
    
    loading.style.display = 'block';
    results.innerHTML = '';
    
    try {
        const formData = new FormData();
        for (let file of files) {
            formData.append('files', file);
        }
        
        const response = await fetch(`${API_URL}/extract-and-validate`, {
            method: 'POST',
            body: formData
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
    } catch (error) {
        results.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    } finally {
        loading.style.display = 'none';
    }
});

function displayResults(qcReport) {
    const results = document.getElementById('results');
    
    // Summary
    const summary = `
        <div class="summary">
            <h2>QC Summary</h2>
            <div class="stat">Total: ${qcReport.total_invoices}</div>
            <div class="stat" style="background: #d4edda;">Valid: ${qcReport.valid_invoices}</div>
            <div class="stat" style="background: #f8d7da;">Invalid: ${qcReport.invalid_invoices}</div>
        </div>
    `;
    
    // Individual results
    let resultsHtml = '';
    for (let result of qcReport.results) {
        const statusClass = result.is_valid ? 'valid' : 'invalid';
        const statusText = result.is_valid ? 'VALID' : 'INVALID';
        
        let errorsHtml = '';
        if (result.errors.length > 0) {
            errorsHtml = `
                <div class="errors">
                    <h4>❌ Errors:</h4>
                    <ul>
                        ${result.errors.map(e => `<li>• ${e}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        let warningsHtml = '';
        if (result.warnings.length > 0) {
            warningsHtml = `
                <div class="warnings">
                    <h4>⚠️ Warnings:</h4>
                    <ul>
                        ${result.warnings.map(w => `<li>• ${w}</li>`).join('')}
                    </ul>
                </div>
            `;
        }
        
        resultsHtml += `
            <div class="invoice-result ${statusClass}">
                <div class="invoice-header">
                    <span class="invoice-number">Invoice: ${result.invoice_number}</span>
                    <span class="status ${statusClass}">${statusText}</span>
                </div>
                ${errorsHtml}
                ${warningsHtml}
            </div>
        `;
    }
    
    results.innerHTML = summary + resultsHtml;
}
