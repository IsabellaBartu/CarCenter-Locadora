// static/js/main.js

// "Quando o documento HTML estiver pronto..."
document.addEventListener("DOMContentLoaded", function() {

    // 1. Encontre o botão hambúrguer pelo 'id'
    const menuHamburger = document.getElementById('menu-hamburger');

    // 2. Encontre a lista de links pelo 'id'
    const menuLinks = document.getElementById('menu-links');

    // 3. "Quando alguém CLICAR no botão hambúrguer..."
    menuHamburger.addEventListener('click', function() {

        // 4. "...adicione ou remova a classe 'ativo' da lista de links."
        //    (Isso faz o CSS mostrar/esconder o menu)
        menuLinks.classList.toggle('ativo');
    });

});
const areaCalculo = document.getElementById('area-calculo');

if (areaCalculo) {
    const dataInicioInput = document.getElementById('data_inicio');
    const dataFimInput = document.getElementById('data_fim');
    const precoTotalSpan = document.getElementById('preco-total');
    const precoDiaria = parseFloat(areaCalculo.dataset.precoDiaria);

    function calcularTotal() {
        const dataInicio = new Date(dataInicioInput.value);
        const dataFim = new Date(dataFimInput.value);

        if (dataInicioInput.value && dataFimInput.value && dataFim > dataInicio) {
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
            precoTotalSpan.textContent = 'R$ 0,00';
        }
    }

    dataInicioInput.addEventListener('change', calcularTotal);
    dataFimInput.addEventListener('change', calcularTotal);
}