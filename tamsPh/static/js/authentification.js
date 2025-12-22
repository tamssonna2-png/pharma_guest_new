document.addEventListener('DOMContentLoaded', () => {
    const loginForm = document.getElementById('loginForm');
    const emailInput = document.getElementById('loginEmail');
    const passwordInput = document.getElementById('loginPassword');

    // --- 1. CONFIGURATION : UTILISATEUR DE TEST ---
    // Dans un vrai site, ces données viendraient d'une base de données sécurisée.
    const MOCK_USER = {
        email: "test@medonline.com",
        password: "Password123",
        name: "Jean Dupont", // Ce nom s'affichera à côté de la photo
        avatar: "https://images.unsplash.com/photo-1633332755192-727a05c4013d?auto=format&fit=crop&w=100&q=80"
    };

    // --- 2. FONCTIONNALITÉ : AFFICHER/MASQUER LE MOT DE PASSE ---
    // On cherche l'élément wrapper ou on ajoute l'icône dynamiquement si elle n'existe pas
    const passwordWrapper = passwordInput.parentElement;
    
    // Création de l'icône "Oeil" si elle n'est pas déjà dans le HTML
    if (!passwordWrapper.querySelector('.toggle-password')) {
        const toggleBtn = document.createElement('span');
        toggleBtn.textContent = ""; // Vous pouvez mettre une icône FontAwesome ici
        toggleBtn.className = "toggle-password";
        toggleBtn.style.position = "absolute";
        toggleBtn.style.right = "10px";
        toggleBtn.style.cursor = "pointer";
        toggleBtn.style.top = "50%";
        toggleBtn.style.transform = "translateY(-50%)";
        
        // Assurez-vous que le parent a position: relative
        passwordWrapper.style.position = "relative";
        passwordWrapper.appendChild(toggleBtn);

        toggleBtn.addEventListener('click', () => {
            // Basculer entre 'password' et 'text'
            const type = passwordInput.getAttribute('type') === 'password' ? 'text' : 'password';
            passwordInput.setAttribute('type', type);
            toggleBtn.textContent = type === 'password' ? "👁️" : "🙈";
        });
    }

    // --- 3. GESTION DE LA SOUMISSION DU FORMULAIRE ---
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            e.preventDefault(); // Empêche le rechargement de la page

            const enteredEmail = emailInput.value.trim();
            const enteredPassword = passwordInput.value;

            // Vérification simple (Email et Mot de passe)
            if (enteredEmail === MOCK_USER.email && enteredPassword === MOCK_USER.password) {
                
                // SUCCÈS : On enregistre les infos dans le navigateur
                // C'est ce qui permet à home.js de savoir qu'on est connecté
                localStorage.setItem('isLoggedIn', 'true');
                localStorage.setItem('userName', MOCK_USER.name);
                
                // Feedback utilisateur
                alert(`Connexion réussie ! Bienvenue ${MOCK_USER.name}.`);

                // Redirection vers la page d'accueil
                window.location.href = "/html/index.html";

            } else {
                // ÉCHEC
                alert("Email ou mot de passe incorrect.\n(Essayez: test@medonline.com / Password123)");
                passwordInput.value = ""; // On efface le mot de passe pour réessayer
                passwordInput.focus();
            }
        });
    }
});