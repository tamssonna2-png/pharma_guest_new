document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Staggered Animation for Cards ---
    const cards = document.querySelectorAll('.stat-card, .card');
    
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'all 0.5s ease-out';
        
        setTimeout(() => {
            card.style.opacity = '1';
            card.style.transform = 'translateY(0)';
        }, index * 100); // 100ms delay between each card
    });

    // --- 2. Interactive Recommendation Cards ---
    // If recommendation cards contain links or expandable details
    const recoCards = document.querySelectorAll('.reco-card');
    
    recoCards.forEach(card => {
        card.addEventListener('click', () => {
            // Visual feedback on click
            card.style.backgroundColor = '#f0f4f8';
            setTimeout(() => {
                card.style.backgroundColor = '#ffffff';
            }, 200);
            
            // Logic to expand details or redirect could go here
            console.log("Recommendation clicked");
        });
    });

    // --- 3. Critical Alert Pulse Effect ---
    // Instead of CSS keyframes injection, we manage it via class toggling if needed
    // or rely on CSS animations.
    const criticalBadges = document.querySelectorAll('.alert-card.critical .badge');
    
    criticalBadges.forEach(badge => {
        setInterval(() => {
            badge.style.opacity = (badge.style.opacity === '0.6') ? '1' : '0.6';
        }, 1000);
    });
});