document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Color Coding for Confidence Badges
    const badges = document.querySelectorAll('.confidence-badge');
    
    badges.forEach(badge => {
        const level = parseInt(badge.getAttribute('data-level'));
        
        if (level >= 80) {
            // High confidence - Green
            badge.style.backgroundColor = 'rgba(0, 184, 148, 0.1)';
            badge.style.color = '#00b894';
        } else if (level >= 50) {
            // Medium - Orange
            badge.style.backgroundColor = 'rgba(253, 203, 110, 0.2)';
            badge.style.color = '#e17055';
        } else {
            // Low - Red/Gray
            badge.style.backgroundColor = '#f1f2f6';
            badge.style.color = '#636e72';
        }
    });

    // 2. Staggered Animation for Cards
    const cards = document.querySelectorAll('.prediction-card');
    cards.forEach((card, index) => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.animation = `fadeInUp 0.5s ease forwards ${index * 0.1}s`;
    });

    // 3. Staggered Animation for Trends
    const trends = document.querySelectorAll('.trend-item');
    trends.forEach((item, index) => {
        item.style.opacity = '0';
        item.style.transform = 'translateX(10px)';
        item.style.animation = `fadeInLeft 0.4s ease forwards ${0.3 + (index * 0.1)}s`;
    });
});

// Inject Keyframes
const styleSheet = document.createElement("style");
styleSheet.innerText = `
@keyframes fadeInUp {
    to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeInLeft {
    to { opacity: 1; transform: translateX(0); }
}`;
document.head.appendChild(styleSheet);