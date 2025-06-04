// AITON-RAG Upload Functionality
// Handles file uploads, drag & drop, and UI interactions

document.addEventListener('DOMContentLoaded', function() {
    // Initialize upload functionality
    initializeFileUpload();
    initializeDragAndDrop();
    initializeFormValidation();
});

function initializeFileUpload() {
    const uploadForm = document.getElementById('uploadForm');
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('file');
    
    if (!uploadForm || !uploadBtn || !fileInput) return;
    
    // Handle form submission
    uploadForm.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const file = fileInput.files[0];
        if (!file) {
            showAlert('Please select a file to upload', 'warning');
            return;
        }
        
        // Validate file
        if (!validateFile(file)) {
            return;
        }
        
        // Show loading state
        setUploadState(true);
        
        // Create FormData and submit
        const formData = new FormData();
        formData.append('file', file);
        
        fetch('/api/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                showAlert(`File uploaded successfully: ${data.filename}`, 'success');
                uploadForm.reset();
                
                // Update stats if available
                setTimeout(() => {
                    updateStats();
                }, 2000);
            } else {
                showAlert(`Upload failed: ${data.error}`, 'danger');
            }
        })
        .catch(error => {
            console.error('Upload error:', error);
            showAlert('Upload failed. Please try again.', 'danger');
        })
        .finally(() => {
            setUploadState(false);
        });
    });
}

function initializeDragAndDrop() {
    const dropZone = document.getElementById('dropZone');
    const dropZoneInput = document.getElementById('dropZoneInput');
    
    if (!dropZone || !dropZoneInput) return;
    
    // Prevent default drag behaviors
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
        document.body.addEventListener(eventName, preventDefaults, false);
    });
    
    // Highlight drop zone when item is dragged over it
    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });
    
    // Handle dropped files
    dropZone.addEventListener('drop', handleDrop, false);
    
    // Handle click to select files
    dropZone.addEventListener('click', () => {
        dropZoneInput.click();
    });
    
    // Handle file selection via click
    dropZoneInput.addEventListener('change', function(e) {
        if (e.target.files.length > 0) {
            handleFiles(e.target.files);
        }
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    function highlight() {
        dropZone.classList.add('drag-over');
    }
    
    function unhighlight() {
        dropZone.classList.remove('drag-over');
    }
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles(files);
    }
}

function handleFiles(files) {
    Array.from(files).forEach(file => {
        if (validateFile(file)) {
            uploadFile(file);
        }
    });
}

function uploadFile(file) {
    const formData = new FormData();
    formData.append('file', file);
    
    // Create progress indicator
    const progressContainer = createProgressIndicator(file.name);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            updateProgressIndicator(progressContainer, 'success', `Uploaded: ${data.filename}`);
            setTimeout(() => {
                updateStats();
            }, 2000);
        } else {
            updateProgressIndicator(progressContainer, 'error', `Error: ${data.error}`);
        }
    })
    .catch(error => {
        console.error('Upload error:', error);
        updateProgressIndicator(progressContainer, 'error', 'Upload failed');
    });
}

function validateFile(file) {
    const maxSize = 10 * 1024 * 1024; // 10MB
    const allowedTypes = [
        'application/pdf',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'text/plain',
        'text/html',
        'text/markdown'
    ];
    
    const allowedExtensions = ['.pdf', '.docx', '.txt', '.html', '.md', '.htm'];
    
    // Check file size
    if (file.size > maxSize) {
        showAlert(`File too large: ${file.name}. Maximum size is 10MB.`, 'warning');
        return false;
    }
    
    // Check file extension
    const fileExtension = '.' + file.name.split('.').pop().toLowerCase();
    if (!allowedExtensions.includes(fileExtension)) {
        showAlert(`Unsupported file type: ${fileExtension}. Supported types: ${allowedExtensions.join(', ')}`, 'warning');
        return false;
    }
    
    return true;
}

function createProgressIndicator(filename) {
    const container = document.createElement('div');
    container.className = 'alert alert-info mt-2 fade-in';
    container.innerHTML = `
        <div class="d-flex align-items-center">
            <div class="loading-spinner me-3"></div>
            <div>
                <strong>Uploading:</strong> ${filename}
                <div class="small text-muted">Processing...</div>
            </div>
        </div>
    `;
    
    // Add to page
    const alertContainer = document.querySelector('.container .mt-4') || document.body;
    alertContainer.appendChild(container);
    
    return container;
}

function updateProgressIndicator(container, status, message) {
    const iconClass = status === 'success' ? 'fas fa-check-circle text-success' : 'fas fa-exclamation-triangle text-danger';
    const alertClass = status === 'success' ? 'alert-success' : 'alert-danger';
    
    container.className = `alert ${alertClass} mt-2`;
    container.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="${iconClass} me-3"></i>
            <div>${message}</div>
        </div>
    `;
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        container.remove();
    }, 5000);
}

function setUploadState(isUploading) {
    const uploadBtn = document.getElementById('uploadBtn');
    const fileInput = document.getElementById('file');
    
    if (!uploadBtn || !fileInput) return;
    
    if (isUploading) {
        uploadBtn.disabled = true;
        uploadBtn.innerHTML = `
            <span class="loading-spinner me-2"></span>
            Uploading...
        `;
        fileInput.disabled = true;
    } else {
        uploadBtn.disabled = false;
        uploadBtn.innerHTML = `
            <i class="fas fa-upload me-2"></i>
            Upload & Process
        `;
        fileInput.disabled = false;
    }
}

function initializeFormValidation() {
    const forms = document.querySelectorAll('.needs-validation');
    
    Array.from(forms).forEach(form => {
        form.addEventListener('submit', event => {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });
}

function showAlert(message, type = 'info') {
    // Remove existing alerts
    const existingAlerts = document.querySelectorAll('.alert.auto-alert');
    existingAlerts.forEach(alert => alert.remove());
    
    // Create new alert
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show auto-alert slide-up`;
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // Add to page
    const container = document.querySelector('.container');
    if (container) {
        container.insertBefore(alertDiv, container.firstChild);
    }
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (alertDiv.parentNode) {
            alertDiv.remove();
        }
    }, 5000);
}

function updateStats() {
    // Fetch updated stats and update the UI
    fetch('/api/v1/health')
        .then(response => response.json())
        .then(data => {
            if (data.success && data.stats) {
                // Update file count
                const fileCountElements = document.querySelectorAll('[data-stat="total_files"]');
                fileCountElements.forEach(el => {
                    el.textContent = data.stats.total_processed_files || 0;
                });
                
                // Update category count
                const categoryCountElements = document.querySelectorAll('[data-stat="total_categories"]');
                categoryCountElements.forEach(el => {
                    el.textContent = data.stats.knowledge_base_categories || 0;
                });
            }
        })
        .catch(error => {
            console.error('Error updating stats:', error);
        });
}

// Utility functions
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString() + ' ' + date.toLocaleTimeString();
}

// Export functions for global use
window.AITONRAG = {
    uploadFile,
    validateFile,
    showAlert,
    updateStats,
    formatFileSize,
    formatDate
};
