document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. CONFIGURATION DU PRODUIT ---
    const productData = {
        id: 113,
        name: "Doliprane 1000mg",
        price: 500,
        image: "https://pharma-guest-new.onrender.com/static/images/doliprane.png", 
        description: "Ce médicament contient du paracétamol. Indiqué en cas de douleur et/ou fièvre.",
        pharmacy: "Pharmacie du soleil"
    };

    // Remplissage des infos produit
    const imgElement = document.getElementById('prod-img');
    if(imgElement) {
        imgElement.src = productData.image;
        imgElement.onerror = function() { this.src = "https://via.placeholder.com/400x400?text=Image+Medicament"; };
    }
    
    if(document.getElementById('prod-name')) document.getElementById('prod-name').textContent = productData.name;
    if(document.getElementById('breadcrumb-name')) document.getElementById('breadcrumb-name').textContent = productData.name;
    if(document.getElementById('prod-price')) document.getElementById('prod-price').textContent = productData.price;
    if(document.getElementById('prod-desc')) document.getElementById('prod-desc').textContent = productData.description;
    if(document.getElementById('pharmacy-name')) document.getElementById('pharmacy-name').textContent = productData.pharmacy;


    // --- 2. GESTION DE LA QUANTITÉ (CORRECTION) ---
    const btnMinus = document.getElementById('btn-minus');
    const btnPlus = document.getElementById('btn-plus');
    const inputQty = document.getElementById('qty-input');
    const totalPriceEl = document.getElementById('total-price');

    // Fonction pour calculer le total
    function updateTotal() {
        // On s'assure que la valeur est un nombre entier, sinon 1 par défaut
        let qty = parseInt(inputQty.value);
        if (isNaN(qty) || qty < 1) {
            qty = 1;
            inputQty.value = 1;
        }
        
        const total = qty * productData.price;
        totalPriceEl.textContent = total;
    }

    // Gestion du bouton PLUS (+)
    if(btnPlus) {
        btnPlus.addEventListener('click', (e) => {
            e.preventDefault(); // Empêche tout comportement par défaut
            let currentQty = parseInt(inputQty.value);
            inputQty.value = currentQty + 1;
            updateTotal();
        });
    }

    // Gestion du bouton MOINS (-)
    if(btnMinus) {
        btnMinus.addEventListener('click', (e) => {
            e.preventDefault(); // Empêche tout comportement par défaut
            let currentQty = parseInt(inputQty.value);
            if (currentQty > 1) {
                inputQty.value = currentQty - 1;
                updateTotal();
            }
        });
    }

    // Initialisation au chargement de la page
    updateTotal();


    // --- 3. GESTION DE LA COMMANDE ---
    const btnOrder = document.getElementById('confirm-order');
    if(btnOrder) {
        btnOrder.addEventListener('click', () => {
            const qty = inputQty.value;
            const total = totalPriceEl.textContent;
            const confirmMessage = `Confirmation :\n\nProduit : ${productData.name}\nQuantité : ${qty}\nTotal : ${total} FCFA`;
            alert(confirmMessage);
        });
    }
});