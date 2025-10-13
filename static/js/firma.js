document.addEventListener('DOMContentLoaded', function() {
    ['firma_cliente', 'firma_tecnico'].forEach(function(fieldName) {
        let input = document.getElementById('id_' + fieldName);
        if (!input) return;

        // Crear contenedor responsive
        let container = document.createElement('div');
        container.style.width = '100%';
        container.style.maxWidth = '500px'; // límite máximo
        container.style.margin = '0 auto';
        input.parentNode.insertBefore(container, input.nextSibling);

        // Crear canvas de alta resolución
        let canvas = document.createElement('canvas');
        const scale = 2; // Escala para mayor calidad
        canvas.width = 500 * scale; // ancho real
        canvas.height = 150 * scale; // alto real
        canvas.style.width = '100%'; // ancho visual
        canvas.style.height = '150px'; // alto visual
        canvas.style.border = "1px solid #000";
        container.appendChild(canvas);

        let ctx = canvas.getContext('2d');
        ctx.scale(scale, scale); // Escalar contexto para alta resolución
        let drawing = false;

        // Función para obtener coordenadas correctas
        function getXY(event) {
            const rect = canvas.getBoundingClientRect();
            if (event.touches) { // Touch
                return {
                    x: (event.touches[0].clientX - rect.left),
                    y: (event.touches[0].clientY - rect.top)
                };
            } else { // Mouse
                return {
                    x: (event.offsetX * scale),
                    y: (event.offsetY * scale)
                };
            }
        }

        // Iniciar dibujo
        function startDraw(e) {
            e.preventDefault();
            drawing = true;
            const pos = getXY(e);
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        }

        // Dibujar
        function draw(e) {
            if (!drawing) return;
            e.preventDefault();
            const pos = getXY(e);
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.strokeStyle = '#000';
            ctx.lineTo(pos.x, pos.y);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(pos.x, pos.y);
        }

        // Terminar dibujo
        function endDraw(e) {
            e.preventDefault();
            drawing = false;
            ctx.beginPath();
        }

        // Eventos mouse
        canvas.addEventListener('mousedown', startDraw);
        canvas.addEventListener('mousemove', draw);
        canvas.addEventListener('mouseup', endDraw);
        canvas.addEventListener('mouseleave', endDraw);

        // Eventos touch
        canvas.addEventListener('touchstart', startDraw);
        canvas.addEventListener('touchmove', draw);
        canvas.addEventListener('touchend', endDraw);

        // Reset
        let resetBtn = document.createElement('button');
        resetBtn.type = 'button';
        resetBtn.textContent = 'Reset';
        resetBtn.style.display = 'block';
        resetBtn.style.margin = '10px auto';
        resetBtn.addEventListener('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
        container.appendChild(resetBtn);

        // Al enviar el form, guardar base64 en input
        input.closest('form').addEventListener('submit', e => {
            input.value = canvas.toDataURL();
        });

        // Ocultar input original
        input.style.display = 'none';
    });
});
