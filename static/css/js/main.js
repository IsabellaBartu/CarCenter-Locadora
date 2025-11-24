 document.addEventListener("DOMContentLoaded", function () {

    let fontSize = parseInt(localStorage.getItem("fontSize")) || 100;
    let contrast = localStorage.getItem("contrast") || "off";

    applyAccessibility();

    const btnIncrease = document.getElementById("btn-increase");
    const btnDecrease = document.getElementById("btn-decrease");
    const btnContrast = document.getElementById("btn-contrast");
    const btnReset = document.getElementById("btn-reset");

    btnIncrease?.addEventListener("click", () => {
        fontSize += 10;
        if (fontSize > 200) fontSize = 200;
        localStorage.setItem("fontSize", fontSize);
        applyAccessibility();
    });

    btnDecrease?.addEventListener("click", () => {
        fontSize -= 10;
        if (fontSize < 60) fontSize = 60;
        localStorage.setItem("fontSize", fontSize);
        applyAccessibility();
    });

    btnContrast?.addEventListener("click", () => {
        contrast = contrast === "off" ? "on" : "off";
        localStorage.setItem("contrast", contrast);
        applyAccessibility();
    });

    btnReset?.addEventListener("click", () => {
        fontSize = 100;
        contrast = "off";
        localStorage.setItem("fontSize", fontSize);
        localStorage.setItem("contrast", contrast);
        applyAccessibility();
    });

    function applyAccessibility() {
        document.documentElement.style.fontSize = fontSize + "%";

        if (contrast === "on") {
            document.body.classList.add("high-contrast");
        } else {
            document.body.classList.remove("high-contrast");
        }
    }

    const trackMarcas = document.querySelector('.marcas-track');
    if (trackMarcas) {
        let isDown = false;
        let startX;
        let scrollLeft;

        trackMarcas.addEventListener('mousedown', (e) => {
            isDown = true;
            startX = e.pageX - trackMarcas.offsetLeft;
            scrollLeft = trackMarcas.scrollLeft;
        });

        trackMarcas.addEventListener('mouseleave', () => {
            isDown = false;
        });

        trackMarcas.addEventListener('mouseup', () => {
            isDown = false;
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
