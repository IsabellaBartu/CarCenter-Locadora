// static/js/main.js

// Espera o site carregar todo antes de rodar o script
document.addEventListener("DOMContentLoaded", function() {
    const menuHamburger = document.getElementById('menu-hamburger');
    const menuLinks = document.getElementById('menu-links');

    if (menuHamburger && menuLinks) {
        menuHamburger.addEventListener('click', function() {
            menuLinks.classList.toggle('ativo');
        });
    }

    // =============================================
    // 2. CARROSSEL DE MARCAS (Setinhas)
    // =============================================
    const trackMarcas = document.getElementById('track-marcas');
    const btnPrev = document.getElementById('btn-prev');
    const btnNext = document.getElementById('btn-next');

    if (trackMarcas && btnPrev && btnNext) {
        
        // Botão Direita (Avançar)
        btnNext.addEventListener('click', () => {
            trackMarcas.scrollBy({ left: 200, behavior: 'smooth' });
        });

        // Botão Esquerda (Voltar)
        btnPrev.addEventListener('click', () => {
            trackMarcas.scrollBy({ left: -200, behavior: 'smooth' });
        });
    }

    // =============================================
    // 3. CÁLCULO DE PREÇO (Página de Detalhes)
    // =============================================
    const areaCalculo = document.getElementById('area-calculo');

    if (areaCalculo) {
        const dataInicioInput = document.getElementById('data_inicio');
        const dataFimInput = document.getElementById('data_fim');
        const precoTotalSpan = document.getElementById('preco-total');
        
        // Pega o preço do atributo data-preco-diaria (e garante que é número)
        const precoDiaria = parseFloat(areaCalculo.dataset.precoDiaria);

        function calcularTotal() {
            // Só calcula se as duas datas estiverem preenchidas
            if (!dataInicioInput.value || !dataFimInput.value) return;

            const dataInicio = new Date(dataInicioInput.value);
            const dataFim = new Date(dataFimInput.value);

            // Garante que a data de fim é maior que a de início
            if (dataFim > dataInicio) {
                const diffTime = Math.abs(dataFim - dataInicio);
                const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)); 
                
                if (diffDays > 0) {
                    const total = diffDays * precoDiaria;
                    precoTotalSpan.textContent = total.toLocaleString('pt-BR', {
                        style: 'currency',
                        currency: 'BRL'
                    });
                } else {
                     precoTotalSpan.textContent = 'R$ 0,00';
                }
            } else {
                precoTotalSpan.textContent = 'Data Inválida';
            }
        }

        // Escuta mudanças nos inputs
        if (dataInicioInput && dataFimInput) {
            dataInicioInput.addEventListener('change', calcularTotal);
            dataFimInput.addEventListener('change', calcularTotal);
        }
    }

});
// 4. DROPDOWN DE CONTATOS
    // =============================================
    const btnContatos = document.getElementById('btn-contatos');
    const boxContatos = document.getElementById('box-contatos');

    if (btnContatos && boxContatos) {
        // Ao clicar no botão
        btnContatos.addEventListener('click', function(e) {
            e.preventDefault(); // Não deixa o link pular a página
            boxContatos.classList.toggle('ativo'); // Mostra/Esconde
        });

        // Fechar se clicar fora da caixa
        document.addEventListener('click', function(e) {
            if (!btnContatos.contains(e.target) && !boxContatos.contains(e.target)) {
                boxContatos.classList.remove('ativo');
            }
        });
    }