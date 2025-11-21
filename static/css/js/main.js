// static/js/main.js - CÓDIGO FINAL CONSOLIDADO

document.addEventListener("DOMContentLoaded", function() {
    
    // =============================================
    // 1. HEADER (Menu Mobile, Dropdown Contatos)
    // =============================================
    const menuHamburger = document.getElementById('menu-hamburger');
    const menuLinks = document.getElementById('menu-links');
    const btnContatos = document.getElementById('btn-contatos');
    const boxContatos = document.getElementById('box-contatos');
    
    // Lógica Menu Mobile
    if (menuHamburger && menuLinks) {
        menuHamburger.addEventListener('click', function() {
            menuLinks.classList.toggle('ativo');
        });
    }

    // Lógica Dropdown Contatos
    if (btnContatos && boxContatos) {
        btnContatos.addEventListener('click', function(e) {
            e.preventDefault(); 
            e.stopPropagation();
            boxContatos.classList.toggle('ativo');
        });
        document.addEventListener('click', function(e) {
            if (!boxContatos.contains(e.target) && e.target !== btnContatos) {
                boxContatos.classList.remove('ativo');
            }
        });
    }

    // =============================================
    // 2. HERO SLIDER (Banner Principal)
    // =============================================
    const heroTrack = document.getElementById('hero-track');
    const heroPrev = document.getElementById('hero-prev');
    const heroNext = document.getElementById('hero-next');
    const slides = document.querySelectorAll('.hero-slide');
    let currentSlide = 0;

    function updateHero() {
        if (heroTrack) {
            heroTrack.style.transform = `translateX(-${currentSlide * 100}%)`;
        }
    }

    if (heroTrack && slides.length > 0) {
        heroNext.addEventListener('click', () => {
            currentSlide = (currentSlide + 1) % slides.length;
            updateHero();
        });

        heroPrev.addEventListener('click', () => {
            currentSlide = (currentSlide - 1 + slides.length) % slides.length;
            updateHero();
        });

        // Passar sozinho a cada 5 segundos
        setInterval(() => {
            currentSlide = (currentSlide + 1) % slides.length;
            updateHero();
        }, 5000);
    }
    
    // =============================================
    // 3. CARROSSEL DE MARCAS (Setinhas) - CORRIGIDO
    // =============================================
    const trackMarcas = document.getElementById('track-marcas');
    const btnPrevM = document.getElementById('btn-prev'); 
    const btnNextM = document.getElementById('btn-next');

    if (trackMarcas && btnPrevM && btnNextM) {
        btnNextM.addEventListener('click', () => {
            trackMarcas.scrollBy({ left: 180, behavior: 'smooth' });
        });
        
        // Lógica de voltar corrigida para -180px
        btnPrevM.addEventListener('click', () => {
            trackMarcas.scrollBy({ left: -180, behavior: 'smooth' });
        });
    }

    // =============================================
    // 4. CÁLCULO DE PREÇO (Página de Detalhes)
    // ... (A lógica de cálculo de preço fica aqui embaixo, junto com o resto do código)
    // ... (Eu omiti o bloco de cálculo para não poluir, mas ele deve estar no seu arquivo!)
    
});