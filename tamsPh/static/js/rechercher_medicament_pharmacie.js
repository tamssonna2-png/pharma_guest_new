document.addEventListener('DOMContentLoaded', () => {
    
    // 1. Staggered Animation for Results
    const cards = document.querySelectorAll('.stock-card');
    
    if (cards.length > 0) {
        cards.forEach((card, index) => {
            // Set initial state
            card.style.opacity = '0';
            card.style.transform = 'translateY(20px)';
            
            // Trigger animation with delay
            setTimeout(() => {
                card.style.transition = 'all 0.5s ease-out';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, index * 50); // Fast cascade (50ms)
        });
    }

    // 2. Quick Highlight for Search Terms (Optional Polish)
    // If we wanted to highlight the text that matches the search query
    const searchInput = document.querySelector('input[name="q"]');
    if (searchInput && searchInput.value) {
        // Logic to highlight text could go here
        // But for now, we just ensure focus is clear
        searchInput.parentElement.style.boxShadow = '0 0 0 3px rgba(0, 184, 148, 0.1)';
        searchInput.style.borderColor = 'var(--palegreen)';
    }
});