document.addEventListener('DOMContentLoaded', () => {

    // --- 1. SECURITY CHECK ---
    // If user is NOT logged in, kick them back to login page
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (isLoggedIn !== 'true') {
        alert("Veuillez vous connecter pour accéder à cette page.");
        window.location.href = "/html/connexion.html";
        return; // Stop script execution
    }


    const DB_CATEGORIES = [
        { id: 'pain', label: 'Douleurs & Fièvre' },
        { id: 'cold', label: 'Rhume & Grippe' },
        { id: 'digestion', label: 'Digestion' },
        { id: 'baby', label: 'Bébé & Maman' },
        { id: 'firstaid', label: 'Premiers Secours' },
        { id: 'beauty', label: 'Beauté & Hygiène' },
        { id: 'vitamins', label: 'Vitamines & Énergie' }
    ];

    function loadCategories() {
        const selectElement = document.getElementById('drug-category');
        
        // Vérification de sécurité (au cas où l'élément n'existe pas sur la page)
        if (!selectElement) return;

        // 1. On remet l'option par défaut "Toutes"
        selectElement.innerHTML = '<option value="">Catégories</option>';

        // 2. On boucle sur notre base de données pour créer les options
        DB_CATEGORIES.forEach(category => {
            // Création d'une balise <option>
            const option = document.createElement('option');
            option.value = category.id;       // Ce qui est envoyé au code (ex: 'pain')
            option.textContent = category.label; // Ce que l'utilisateur voit (ex: 'Douleurs...')
            
            // Ajout au menu déroulant
            selectElement.appendChild(option);
        });
    }

    // --- C. APPEL DE LA FONCTION ---
    // On lance la fonction dès que la page charge
    loadCategories();

    // --- 2. PERSONALIZATION ---
    // Get name from storage or default to "Utilisateur"
    const userName = localStorage.getItem('userName') || "Utilisateur";
    const displayNameEl = document.getElementById('display-name');
    if (displayNameEl) {
        displayNameEl.textContent = userName;
    }

    // --- 3. TAB SWITCHING LOGIC ---
    const tabButtons = document.querySelectorAll('.tab-btn');
    const searchPanels = document.querySelectorAll('.search-panel');

    tabButtons.forEach(button => {
        button.addEventListener('click', () => {
            // 1. Remove active class from all buttons
            tabButtons.forEach(btn => btn.classList.remove('active'));
            // 2. Add active class to clicked button
            button.classList.add('active');

            // 3. Hide all panels
            searchPanels.forEach(panel => panel.classList.remove('active'));
            
            // 4. Show the target panel
            const targetId = button.getAttribute('data-target');
            document.getElementById(targetId).classList.add('active');
        });
    });

    // --- 4. SIMULATE SEARCH ACTION ---
    const searchButtons = document.querySelectorAll('.btn-search');
    searchButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            // Here you would normally fetch data from a backend
            // For now, we simulate a redirection to results
            alert("Recherche lancée ! (Simulation)");
            
            // Example: Redirect to map or list based on tab
            // window.location.href = "/html/resultats.html";
        });
    });
});