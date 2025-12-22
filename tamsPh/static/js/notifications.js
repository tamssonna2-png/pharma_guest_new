// Function to handle the first click (Show Confirmation UI)
function confirmerCommande(id, btn) {
    const actionArea = document.getElementById(`action-area-${id}`);
    
    // Save original button html if needed to revert
    // Replace with confirmation box
    actionArea.innerHTML = `
        <div class="confirmation-box">
            <span class="warning-text"><i class="fas fa-exclamation-triangle"></i> Confirmer la disponibilité ?</span>
            <div class="btn-group">
                <button class="btn-yes" onclick="confirmerDefinitivement(${id})">Oui, valider</button>
                <button class="btn-no" onclick="annulerConfirmation(${id}, '${btn.outerHTML.replace(/"/g, '&quot;')}')">Annuler</button>
            </div>
        </div>
    `;
}

// Revert to original state
function annulerConfirmation(id, originalBtnHtml) {
    // If we passed the HTML string properly, we can restore it. 
    // Simplified restoration:
    const actionArea = document.getElementById(`action-area-${id}`);
    actionArea.innerHTML = `
        <button class="btn-confirm" onclick="confirmerCommande(${id}, this)">
            <i class="fas fa-check"></i> Traiter la commande
        </button>
    `;
}

// Function to actually send the request
async function confirmerDefinitivement(commandeId) {
    const actionArea = document.getElementById(`action-area-${commandeId}`);
    const messageElement = document.getElementById(`message-${commandeId}`);
    
    // Show loading state
    actionArea.innerHTML = '<span style="color:var(--palegreen);"><i class="fas fa-spinner fa-spin"></i> Traitement en cours...</span>';

    try {
        const response = await fetch(`/confirmer-commande/${commandeId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': getCookie('csrftoken'),
                'Content-Type': 'application/json'
            }
        });

        const result = await response.json();

        if (result.success) {
            // Success UI
            actionArea.style.display = 'none';
            messageElement.style.display = 'block';
            messageElement.className = 'feedback-message feedback-success';
            messageElement.innerHTML = `<i class="fas fa-check-circle"></i> Commande confirmée avec succès.`;

            // Change card visual style to "Done"
            const card = document.getElementById(`commande-${commandeId}`);
            card.style.opacity = '0.7';
            card.querySelector('.status-stripe').style.backgroundColor = 'var(--green)';
            
            // Optional: Remove after delay
            setTimeout(() => {
                card.style.transition = 'all 0.5s';
                card.style.transform = 'translateX(100px)';
                card.style.opacity = '0';
                setTimeout(() => card.remove(), 500);
            }, 2000);

        } else {
            throw new Error(result.error || "Erreur inconnue");
        }

    } catch (error) {
        console.error('Erreur:', error);
        actionArea.style.display = 'block'; // Show action area again
        messageElement.style.display = 'block';
        messageElement.className = 'feedback-message feedback-error';
        messageElement.innerHTML = `<i class="fas fa-times-circle"></i> Échec : ${error.message}`;
        
        // Restore button after delay
        setTimeout(() => {
             actionArea.innerHTML = `
                <button class="btn-confirm" onclick="confirmerCommande(${commandeId}, this)">
                    <i class="fas fa-redo"></i> Réessayer
                </button>
            `;
        }, 3000);
    }
}

// Helper for CSRF Token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Load animations
document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.notification-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.animation = `slideIn 0.5s ease forwards ${index * 0.1}s`;
    });
});

// Add Keyframe dynamically
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes slideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}`;
document.head.appendChild(styleSheet);