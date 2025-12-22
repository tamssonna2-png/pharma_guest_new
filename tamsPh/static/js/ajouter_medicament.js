document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Image Upload Preview & Drag-n-Drop ---
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('id_image');
    const fileNameDisplay = document.getElementById('file-name');
    const imagePreview = document.getElementById('imagePreview');

    // Trigger file input when clicking the zone
    dropZone.addEventListener('click', () => fileInput.click());

    // Handle file selection
    fileInput.addEventListener('change', (e) => handleFile(e.target.files[0]));

    // Drag and Drop Visuals
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--palegreen)';
        dropZone.style.background = 'rgba(0, 184, 148, 0.05)';
    });

    dropZone.addEventListener('dragleave', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--gray-border)';
        dropZone.style.background = '#fafafa';
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.style.borderColor = 'var(--gray-border)';
        dropZone.style.background = '#fafafa';
        
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files; // Assign to input
            handleFile(e.dataTransfer.files[0]);
        }
    });

    function handleFile(file) {
        if (file) {
            fileNameDisplay.textContent = file.name;
            
            // Show image preview
            if (file.type.startsWith('image/')) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    imagePreview.innerHTML = `<img src="${e.target.result}" alt="Preview">`;
                    imagePreview.style.display = 'block';
                };
                reader.readAsDataURL(file);
            }
        }
    }

    // --- 2. Character Counter for Description ---
    const descInput = document.getElementById('id_description');
    const countDisplay = document.getElementById('descriptionCount');
    const maxChars = 500;

    if (descInput) {
        descInput.addEventListener('input', () => {
            const currentLength = descInput.value.length;
            countDisplay.textContent = `${currentLength}/${maxChars}`;
            
            if (currentLength >= maxChars) {
                countDisplay.style.color = 'red';
            } else {
                countDisplay.style.color = '#b2bec3';
            }
        });
    }

    // --- 3. Form Submission Animation ---
    const form = document.getElementById('medicamentForm');
    form.addEventListener('submit', (e) => {
        // Optional: Simple validation check
        const price = document.getElementById('id_prix').value;
        const qty = document.getElementById('id_quantite').value;

        if (price < 0 || qty < 0) {
            e.preventDefault();
            alert("Le prix et la quantité ne peuvent pas être négatifs.");
        } else {
            // Add loading state to button
            const btn = document.querySelector('.btn-submit');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Enregistrement...';
            btn.style.opacity = '0.8';
        }
    });
});