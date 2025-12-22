// Function to copy password to clipboard
function copyPassword() {
    const passwordText = document.getElementById('newPassword');
    const copyBtn = document.querySelector('.btn-copy');
    
    if (passwordText) {
        // Use modern Clipboard API
        navigator.clipboard.writeText(passwordText.innerText)
            .then(() => {
                // Visual feedback
                const originalIcon = copyBtn.innerHTML;
                
                copyBtn.innerHTML = '<i class="fas fa-check"></i>';
                copyBtn.style.backgroundColor = 'var(--palegreen)';
                copyBtn.style.color = 'white';
                copyBtn.style.borderColor = 'var(--palegreen)';
                
                // Revert after 2 seconds
                setTimeout(() => {
                    copyBtn.innerHTML = '<i class="far fa-copy"></i>';
                    copyBtn.style.backgroundColor = '';
                    copyBtn.style.color = '';
                    copyBtn.style.borderColor = '';
                }, 2000);
            })
            .catch(err => {
                console.error('Erreur lors de la copie :', err);
                alert("Impossible de copier le mot de passe automatiquement.");
            });
    }
}

// Add focus animation for better UX
document.addEventListener('DOMContentLoaded', () => {
    const inputs = document.querySelectorAll('input');
    inputs.forEach(input => {
        input.addEventListener('focus', () => {
            input.parentElement.querySelector('.input-icon').style.color = 'var(--palegreen)';
        });
        input.addEventListener('blur', () => {
            input.parentElement.querySelector('.input-icon').style.color = '#b2bec3';
        });
    });
});