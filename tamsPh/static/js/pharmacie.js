document.addEventListener('DOMContentLoaded', () => {
    const registrationForm = document.getElementById('registrationForm');

    registrationForm.addEventListener('submit', (e) => {
        e.preventDefault();

        // Récupération des données
        const data = {
            name: document.getElementById('fullname').value,
            email: document.getElementById('email').value,
            role: document.getElementById('role').value
        };

        console.log("Tentative d'inscription :", data);

        // Simulation d'une réponse serveur
        alert(`Merci ${data.name} ! Votre compte en tant que ${data.role} a été créé avec succès.`);
        
        // Redirection vers l'accueil
        window.location.href = "/html/index.html";
    });
});