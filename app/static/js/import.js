document.addEventListener('DOMContentLoaded', function() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('file');
    const selectedFile = document.getElementById('selectedFile');
    const fileName = document.getElementById('fileName');
    const removeFileBtn = document.getElementById('removeFileBtn');
    const submitBtn = document.getElementById('uploadSubmitBtn');
    
    if (uploadArea && fileInput) {
        // Handle clicking to open file dialog
        uploadArea.addEventListener('click', () => {
            fileInput.click();
        });
        
        // Handle drag and drop
        uploadArea.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadArea.classList.add('dragover');
        });
        
        uploadArea.addEventListener('dragleave', () => {
            uploadArea.classList.remove('dragover');
        });
        
        uploadArea.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadArea.classList.remove('dragover');
            
            if (e.dataTransfer.files.length) {
                fileInput.files = e.dataTransfer.files;
                updateFileDisplay();
            }
        });
        
        // Handle file selection
        fileInput.addEventListener('change', updateFileDisplay);
        
        function updateFileDisplay() {
            if (fileInput.files.length > 0) {
                const file = fileInput.files[0];
                fileName.textContent = file.name;
                uploadArea.style.display = 'none';
                selectedFile.style.display = 'flex';
                submitBtn.disabled = false;
            } else {
                uploadArea.style.display = 'block';
                selectedFile.style.display = 'none';
                submitBtn.disabled = true;
            }
        }
        
        // Handle remove file
        if (removeFileBtn) {
            removeFileBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                fileInput.value = '';
                updateFileDisplay();
            });
        }
    }
});
