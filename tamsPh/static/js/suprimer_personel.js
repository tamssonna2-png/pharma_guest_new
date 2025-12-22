document.addEventListener('DOMContentLoaded', () => {
    
    // Select the form and the delete button
    const deleteForm = document.querySelector('form');
    const deleteBtn = document.querySelector('.btn-delete');

    if (deleteForm && deleteBtn) {
        
        deleteForm.addEventListener('submit', (e) => {
            // 1. Final browser confirmation (Safety Net)
            const isConfirmed = confirm("⚠️ Attention : Cette action est irréversible.\nVoulez-vous vraiment supprimer ce membre du personnel ?");

            if (!isConfirmed) {
                e.preventDefault(); // Stop if user clicks Cancel
                return;
            }

            // 2. Visual Feedback (Loading State)
            // Change button text and add spinner icon
            const originalText = deleteBtn.innerHTML;
            deleteBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Suppression en cours...';
            
            // Disable button to prevent double submission
            deleteBtn.style.opacity = '0.7';
            deleteBtn.style.pointerEvents = 'none';
        });
    }
});