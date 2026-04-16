document.addEventListener('DOMContentLoaded', () => {
    const apiToken = 'mypassword'; // In a real app, this would be handled via session or a safer way
    const tappeContainer = document.getElementById('tappe-container');
    const countdownElement = document.getElementById("countdown");
    const eventDate = new Date("2025-04-26T13:45:00");

    // Popup Logic
    const imagePopup = document.getElementById('image-popup');
    if (imagePopup) {
        imagePopup.style.display = 'flex';
        setTimeout(() => {
            imagePopup.style.opacity = '0';
            setTimeout(() => {
                imagePopup.style.display = 'none';
            }, 500);
        }, 3000);
    }

    // Countdown Logic
    const updateCountdown = () => {
        const now = new Date();
        const diff = eventDate - now;

        if (diff <= 0) {
            countdownElement.classList.add('status-live');
            countdownElement.innerHTML = `
                <span><span class="pulse"></span>L'evento è iniziato!</span>
                <a href="https://umap.osm.ch/it/map/gusta30_9243" target="_blank" style="font-size: 0.9rem; margin-top: 5px;">
                    Vai alla mappa Gusta30
                </a>`;
            return;
        }

        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        const hours = Math.floor((diff / (1000 * 60 * 60)) % 24);
        const minutes = Math.floor((diff / (1000 * 60)) % 60);
        const seconds = Math.floor((diff / 1000) % 60);

        countdownElement.textContent = `${days}d ${hours}h ${minutes}m ${seconds}s`;
    };

    if (countdownElement) {
        updateCountdown();
        setInterval(updateCountdown, 1000);
    }

    // Load Stages
    const loadStages = async () => {
        try {
            const response = await fetch('/api/tappe', {
                headers: { 'X-API-TOKEN': apiToken }
            });
            
            if (!response.ok) throw new Error("Failed to fetch data");
            
            const data = await response.json();
            tappeContainer.innerHTML = '';

            Object.keys(data).forEach(id => {
                const stage = data[id];
                const card = document.createElement('div');
                card.className = `card ${stage.unlocked ? '' : 'locked'}`;
                
                let content = `
                    <h3>Tappa ${id}</h3>
                    <p><strong>Orario:</strong> ${stage.start} - ${stage.end}</p>
                `;

                if (stage.unlocked) {
                    content += `<p><strong>Luogo:</strong> ${stage.luogo}</p>`;
                    if (stage.cibo && stage.cibo.length > 0) {
                        content += `
                            <p><strong>Cibo:</strong></p>
                            <ul>${stage.cibo.map(item => `<li>${item}</li>`).join('')}</ul>
                        `;
                    }
                    if (stage.bevande && stage.bevande.length > 0) {
                        content += `
                            <p><strong>Bevande:</strong></p>
                            <ul>${stage.bevande.map(item => `<li>${item}</li>`).join('')}</ul>
                        `;
                    }
                    if (stage.hosts && stage.hosts.length > 0) {
                        content += `<p><strong>Hosts:</strong> ${stage.hosts.join(" · ")}</p>`;
                    }
                } else {
                    content += `<p><em>Dettagli oscurati fino all'orario di inizio.</em></p>`;
                }

                card.innerHTML = content;
                tappeContainer.appendChild(card);
            });
        } catch (error) {
            console.error("Error loading stages:", error);
            tappeContainer.innerHTML = '<p class="error">Errore nel caricamento dei dati. Riprova più tardi.</p>';
        }
    };

    if (tappeContainer) {
        loadStages();
    }
});
