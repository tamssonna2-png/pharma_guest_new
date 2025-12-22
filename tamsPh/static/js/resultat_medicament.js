// Function exposed to global scope for the button click
function localiserEtRechercherPharmacies() {
    const nomMedicament = document.getElementById('medicInput').value;
    const statusElement = document.getElementById('statut_recherche');
    const form = document.getElementById('searchForm');

    // Reset status classes
    statusElement.className = 'status-message';
    statusElement.classList.remove('hidden');

    // 1. Validation
    if (!nomMedicament.trim()) {
        statusElement.innerHTML = '<i class="fas fa-times-circle"></i> Veuillez entrer le nom d\'un médicament.';
        statusElement.classList.add('status-error');
        return;
    }

    // 2. Geolocation Logic
    if (navigator.geolocation) {
        statusElement.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Localisation en cours...';
        statusElement.classList.add('status-loading');

        navigator.geolocation.getCurrentPosition(
            // Success
            function(position) {
                const lat = position.coords.latitude;
                const lon = position.coords.longitude;

                document.getElementById('latField').value = lat;
                document.getElementById('lonField').value = lon;

                statusElement.innerHTML = '<i class="fas fa-check-circle"></i> Position trouvée. Recherche...';
                statusElement.classList.replace('status-loading', 'status-success');

                setTimeout(() => form.submit(), 800);
            },
            // Error
            function(error) {
                let msg = "Erreur de géolocalisation. ";
                if (error.code === error.PERMISSION_DENIED) msg = "Accès localisation refusé. ";
                
                statusElement.innerHTML = `<i class="fas fa-exclamation-triangle"></i> ${msg} Recherche globale...`;
                statusElement.classList.replace('status-loading', 'status-error');

                // Clear coords to force global search
                document.getElementById('latField').value = '';
                document.getElementById('lonField').value = '';

                setTimeout(() => form.submit(), 1500);
            },
            { enableHighAccuracy: true, timeout: 8000 }
        );
    } else {
        // Fallback for old browsers
        statusElement.innerHTML = "Géolocalisation non supportée. Recherche globale...";
        statusElement.classList.add('status-error');
        setTimeout(() => form.submit(), 1000);
    }
}

// Add Enter key support
document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('medicInput');
    if(input) {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                e.preventDefault();
                localiserEtRechercherPharmacies();
            }
        });
    }

    // Staggered Animation for Results
    const cards = document.querySelectorAll('.med-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `slideUp 0.5s ease forwards ${index * 0.1}s`;
    });
});

// Add Keyframes for JS animation
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes slideUp {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}`;
document.head.appendChild(styleSheet);