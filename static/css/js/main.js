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

    // 3. CARROSSEL DE MARCAS (Arrastar com o mouse)
// =============================================
const trackMarcas = document.querySelector('.marcas-track');

if (trackMarcas) {
    let isDown = false;
    let startX;
    let scrollLeft;

    trackMarcas.addEventListener('mousedown', (e) => {
        isDown = true;
        trackMarcas.classList.add('active');
        startX = e.pageX - trackMarcas.offsetLeft;
        scrollLeft = trackMarcas.scrollLeft;
    });

    trackMarcas.addEventListener('mouseleave', () => {
        isDown = false;
        trackMarcas.classList.remove('active');
    });

    trackMarcas.addEventListener('mouseup', () => {
        isDown = false;
        trackMarcas.classList.remove('active');
    });

    trackMarcas.addEventListener('mousemove', (e) => {
        if (!isDown) return;
        e.preventDefault();
        const x = e.pageX - trackMarcas.offsetLeft;
        const walk = (x - startX) * 1.5; 
        trackMarcas.scrollLeft = scrollLeft - walk;
    });

    // Suporte para touch (celular)
    trackMarcas.addEventListener('touchstart', (e) => {
        startX = e.touches[0].pageX;
        scrollLeft = trackMarcas.scrollLeft;
    });

    trackMarcas.addEventListener('touchmove', (e) => {
        const x = e.touches[0].pageX;
        const walk = (x - startX) * 1.2;
        trackMarcas.scrollLeft = scrollLeft - walk;
    });
}


    // =============================================
    // 4. CÁLCULO DE PREÇO (Página de Detalhes)
    // ... (A lógica de cálculo de preço fica aqui embaixo, junto com o resto do código)
    // ... (Eu omiti o bloco de cálculo para não poluir, mas ele deve estar no seu arquivo!)
    
});