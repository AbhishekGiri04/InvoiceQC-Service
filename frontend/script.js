// Environment-aware API URL
const API_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:8000'  // Local development
    : 'https://invqc-dev.onrender.com';  // Production

let selectedFiles = [];

// DOM Elements
const fileInput = document.getElementById('fileInput');
const uploadArea = document.getElementById('uploadArea');
const uploadBtn = document.getElementById('uploadBtn');
const fileList = document.getElementById('fileList');
const loading = document.getElementById('loading');
const results = document.getElementById('results');

// File Input Change
fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleFiles(e.target.files);
    }
    // Always clear input to allow same file selection
    e.target.value = '';
});

// Drag and Drop
uploadArea.addEventListener('dragover', (e) => {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
});

uploadArea.addEventListener('dragleave', () => {
    uploadArea.classList.remove('drag-over');
});

uploadArea.addEventListener('drop', (e) => {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    handleFiles(e.dataTransfer.files);
});

// Click to upload - only on upload area, not file list
uploadArea.addEventListener('click', (e) => {
    // Only trigger if clicking directly on upload area elements, not file list
    if (e.target.closest('.file-list') || e.target.closest('.file-item')) return;
    fileInput.click();
});

// Handle Files
function handleFiles(files) {
    const pdfFiles = Array.from(files).filter(file => file.type === 'application/pdf');
    
    if (pdfFiles.length === 0) {
        alert('Please select PDF files only');
        return;
    }
    
    // Prevent duplicates
    const newFiles = pdfFiles.filter(newFile => 
        !selectedFiles.some(existingFile => existingFile.name === newFile.name)
    );
    
    selectedFiles = [...selectedFiles, ...newFiles];
    displayFileList();
    uploadBtn.disabled = selectedFiles.length === 0;
}

// Display File List
function displayFileList() {
    if (selectedFiles.length === 0) {
        fileList.innerHTML = '';
        uploadBtn.disabled = true;
        return;
    }
    
    fileList.innerHTML = selectedFiles.map((file, index) => `
        <div class="file-item">
            <div class="file-icon">
                <i class="fas fa-file-pdf"></i>
            </div>
            <div class="file-details">
                <div class="file-name">${file.name}</div>
                <div class="file-size">${(file.size / 1024 / 1024).toFixed(2)} MB</div>
            </div>
            <div class="file-status">
                <span class="ready-badge">Ready</span>
            </div>
            <button class="remove-file" data-index="${index}" title="Remove file">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `).join('');
    
    // Add event listeners to remove buttons
    document.querySelectorAll('.remove-file').forEach((btn, idx) => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const index = parseInt(btn.dataset.index);
            removeFile(index);
        });
    });
}

// Remove File
function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFileList();
    uploadBtn.disabled = selectedFiles.length === 0;
}

// Upload Button Click
uploadBtn.addEventListener('click', async () => {
    if (selectedFiles.length === 0) {
        alert('Please select PDF files to upload');
        return;
    }
    
    if (selectedFiles.length > 4) {
        alert('Please upload maximum 4 PDFs at a time for better performance');
        return;
    }
    
    loading.style.display = 'block';
    results.innerHTML = '';
    uploadBtn.disabled = true;
    
    try {
        const formData = new FormData();
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });
        
        const response = await fetch(`${API_URL}/extract-and-validate`, {
            method: 'POST',
            body: formData,
            signal: AbortSignal.timeout(60000) // 60 second timeout
        });
        
        if (!response.ok) {
            throw new Error('Upload failed');
        }
        
        const data = await response.json();
        displayResults(data);
        
        // Clear files after successful upload
        selectedFiles = [];
        fileInput.value = '';
        displayFileList();
        
    } catch (error) {
        console.error('Upload error:', error);
        results.innerHTML = `
            <div class="container">
                <div class="summary" style="background: #fee2e2; color: #991b1b;">
                    <h2><i class="fas fa-exclamation-triangle"></i> Error</h2>
                    <p>${error.message}</p>
                    <p style="margin-top: 1rem;">Make sure the API server is running on ${API_URL}</p>
                    <p style="margin-top: 0.5rem; font-size: 0.9rem;">Check browser console for details (F12)</p>
                </div>
            </div>
        `;
    } finally {
        loading.style.display = 'none';
        uploadBtn.disabled = false;
    }
});

// Display Results
function displayResults(qcReport) {
    const container = document.createElement('div');
    container.className = 'container';
    
    // Summary
    const summary = `
        <div class="summary">
            <div class="summary-header">
                <h2><i class="fas fa-chart-bar"></i> Validation Summary</h2>
                <div class="summary-badge">${qcReport.total_invoices} Invoice${qcReport.total_invoices > 1 ? 's' : ''} Processed</div>
            </div>
            <div class="summary-stats">
                <div class="summary-stat total">
                    <div class="stat-icon"><i class="fas fa-file-invoice"></i></div>
                    <div class="stat-content">
                        <div class="value">${qcReport.total_invoices}</div>
                        <div class="label">Total</div>
                    </div>
                </div>
                <div class="summary-stat valid">
                    <div class="stat-icon"><i class="fas fa-check-circle"></i></div>
                    <div class="stat-content">
                        <div class="value">${qcReport.valid_invoices}</div>
                        <div class="label">Valid</div>
                    </div>
                </div>
                <div class="summary-stat invalid">
                    <div class="stat-icon"><i class="fas fa-times-circle"></i></div>
                    <div class="stat-content">
                        <div class="value">${qcReport.invalid_invoices}</div>
                        <div class="label">Invalid</div>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    // Individual Results
    let resultsHtml = '';
    for (let result of qcReport.results) {
        const statusClass = result.is_valid ? 'valid' : 'invalid';
        const statusText = result.is_valid ? 'VALID' : 'INVALID';
        const statusIcon = result.is_valid ? 'fa-check-circle' : 'fa-times-circle';
        
        let errorsHtml = '';
        if (result.errors && result.errors.length > 0) {
            errorsHtml = `
                <div class="errors">
                    <div class="section-header error-header">
                        <i class="fas fa-times-circle"></i>
                        <span>Errors</span>
                        <div class="count-badge error">${result.errors.length}</div>
                    </div>
                    <div class="issues-list">
                        ${result.errors.map(e => `
                            <div class="issue-item error">
                                <i class="fas fa-times-circle"></i>
                                <span>${e}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        let warningsHtml = '';
        if (result.warnings && result.warnings.length > 0) {
            warningsHtml = `
                <div class="warnings">
                    <div class="section-header warning-header">
                        <i class="fas fa-exclamation-triangle"></i>
                        <span>Warnings</span>
                        <div class="count-badge warning">${result.warnings.length}</div>
                    </div>
                    <div class="issues-list">
                        ${result.warnings.map(w => `
                            <div class="issue-item warning">
                                <i class="fas fa-exclamation-triangle"></i>
                                <span>${w}</span>
                            </div>
                        `).join('')}
                    </div>
                </div>
            `;
        }
        
        resultsHtml += `
            <div class="invoice-result ${statusClass}">
                <div class="invoice-header">
                    <div class="invoice-info">
                        <div class="invoice-number">
                            <i class="fas fa-receipt"></i> ${result.invoice_number}
                        </div>
                        <div class="invoice-meta"><i class="fas fa-info-circle"></i> Invoice Analysis Report</div>
                    </div>
                    <div class="status-badge ${statusClass}">
                        <i class="fas ${statusIcon}"></i> ${statusText}
                    </div>
                </div>
                <div class="invoice-content">
                    ${errorsHtml}
                    ${warningsHtml}
                    ${!errorsHtml && !warningsHtml ? '<div class="no-issues"><i class="fas fa-check"></i> No issues found - Invoice passed all validation checks</div>' : ''}
                </div>
            </div>
        `;
    }
    
    container.innerHTML = summary + resultsHtml;
    results.innerHTML = '';
    results.appendChild(container);
    
    // Scroll to results
    results.scrollIntoView({ behavior: 'smooth' });
}

// Smooth Scroll for Navigation
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({ behavior: 'smooth' });
        }
    });
});
