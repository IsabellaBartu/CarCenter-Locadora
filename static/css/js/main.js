document.addEventListener("DOMContentLoaded", function() {
    
    // =============================================
    // 1. HEADER (Menu Mobile, Dropdown Contatos)
    // =============================================
    const menuHamburger = document.getElementById('menu-hamburger');
    const menuLinks = document.getElementById('menu-links');
    const btnContatos = document.getElementById('btn-contatos');
    const boxContatos = document.getElementById('box-contatos');
    
    if (menuHamburger && menuLinks) {
        menuHamburger.addEventListener('click', function() {
            menuLinks.classList.toggle('ativo');
        });
    }

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
    // 3. CARROSSEL DE MARCAS
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
    // 4. CÁLCULO DE PREÇO
    // =============================================
    const areaCalculo = document.getElementById("area-calculo");
    if (areaCalculo) {
        const precoDiaria = parseFloat(areaCalculo.dataset.precoDiaria);
        const inputInicio = document.getElementById("data_inicio");
        const inputFim = document.getElementById("data_fim");
        const campoTotal = document.getElementById("preco-total");

        function atualizarTotal() {
            if (!inputInicio.value || !inputFim.value) {
                campoTotal.textContent = "R$ 0,00";
                return;
            }

            const inicio = new Date(inputInicio.value);
            const fim = new Date(inputFim.value);

            if (fim > inicio) {
                const diffDias = Math.ceil((fim - inicio) / (1000 * 60 * 60 * 24));
                const total = diffDias * precoDiaria;
                campoTotal.textContent = "R$ " + total.toFixed(2).replace(".", ",");
            } else {
                campoTotal.textContent = "R$ 0,00";
            }
        }

        inputInicio.addEventListener("change", atualizarTotal);
        inputFim.addEventListener("change", atualizarTotal);

        atualizarTotal();
    }
});
