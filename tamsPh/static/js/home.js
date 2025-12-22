document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. GESTION DU SLIDER (Code existant) ---
    const slides = document.querySelectorAll('.slide');
    if (slides.length > 0) {
        let currentSlide = 0;
        const slideInterval = 5000;

        function nextSlide() {
            slides[currentSlide].classList.remove('active');
            currentSlide = (currentSlide + 1) % slides.length;
            slides[currentSlide].classList.add('active');
        }
        setInterval(nextSlide, slideInterval);
    }

    // --- 2. GESTION DE LA BARRE DE RECHERCHE ---
    const searchBtn = document.getElementById('search-btn');
    const searchInput = document.getElementById('search-input');

    if (searchBtn && searchInput) {
        searchBtn.addEventListener('click', () => {
            const query = searchInput.value.trim();
            
            if (query.length > 0) {
                console.log(`Recherche pour : ${query}`);
                // Simulation : On redirige vers la page produit
                // Dans un vrai site, on irait vers une page de résultats avec ?q=...
                window.location.href = `/html/commandeClient.html?search=${encodeURIComponent(query)}`;
            } else {
                alert("Veuillez entrer le nom d'un médicament.");
            }
        });

        // Permettre la recherche avec la touche "Entrée"
        searchInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                searchBtn.click();
            }
        });
    }

    // --- 3. GESTION DE L'ÉTAT DE CONNEXION (PROFILE PIC) ---
    checkLoginState();
});

// Fonction globale pour vérifier si l'utilisateur est connecté
function checkLoginState() {
    const authContainer = document.getElementById('auth-container');
    
    // On vérifie si la variable 'isLoggedIn' existe dans le navigateur
    const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true';
    const userName = localStorage.getItem('userName') || 'Utilisateur';

    if (isLoggedIn && authContainer) {
        // Remplacer les boutons par l'image de profil
        authContainer.innerHTML = `
            <div class="user-profile" id="user-profile-btn" title="Cliquez pour vous déconnecter">
                <span style="font-weight: 600; margin-right:5px;">${userName}</span>
                <img src="https://images.unsplash.com/photo-1633332755192-727a05c4013d?auto=format&fit=crop&w=100&q=80" 
                     alt="Profile" 
                     class="profile-pic">
            </div>
        `;

        // Ajouter l'événement de déconnexion au clic sur l'image
        document.getElementById('user-profile-btn').addEventListener('click', () => {
            const confirmLogout = confirm("Voulez-vous vous déconnecter ?");
            if (confirmLogout) {
                localStorage.removeItem('isLoggedIn');
                localStorage.removeItem('userName');
                window.location.reload(); // Recharger la page pour remettre les boutons
            }
        });
    }
}