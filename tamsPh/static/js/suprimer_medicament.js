document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('deleteForm');
    const deleteBtn = document.querySelector('.btn-delete');

    if (form && deleteBtn) {
        form.addEventListener('submit', (e) => {
            // Visual feedback immediately upon click
            const confirmAction = confirm("Confirmer la suppression définitive de ce médicament ?");
            
            if (confirmAction) {
                deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Suppression...';
                deleteBtn.style.opacity = '0.8';
                deleteBtn.style.pointerEvents = 'none'; // Prevent double click
            } else {
                e.preventDefault(); // Stop submission if user cancels the browser alert
            }
        });
    }
});