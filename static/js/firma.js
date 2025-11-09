document.addEventListener('DOMContentLoaded', function() {
    ['firma_cliente', 'firma_tecnico'].forEach(function(fieldName) {
        const input = document.getElementById('id_' + fieldName);
        if (!input) return;

        // --- Crear contenedor ---
        const container = document.createElement('div');
        container.style.width = '100%';
        container.style.maxWidth = '500px';
        container.style.margin = '0 auto 10px auto';
        input.parentNode.insertBefore(container, input.nextSibling);

        // --- Crear canvas ---
        const canvas = document.createElement('canvas');
        canvas.style.width = '100%';
        canvas.style.height = '150px';
        canvas.style.border = '1px solid #000';
        canvas.style.touchAction = 'none'; // Evita scroll en móviles
        container.appendChild(canvas);

        const ctx = canvas.getContext('2d');

        // --- Ajuste de resolución para responsive ---
        function resizeCanvas() {
            const rect = canvas.getBoundingClientRect();
            canvas.width = rect.width;   // ancho real = ancho visible
            canvas.height = rect.height; // alto real = alto visible
        }

        resizeCanvas();
        // window.addEventListener('resize', resizeCanvas);

        // --- Variables de dibujo ---
        let dibujando = false;
        let lastX = 0, lastY = 0;

        function startDraw(x, y) {
            dibujando = true;
            lastX = x;
            lastY = y;
        }

        function draw(x, y) {
            if (!dibujando) return;
            ctx.beginPath();
            ctx.moveTo(lastX, lastY);
            ctx.lineTo(x, y);
            ctx.strokeStyle = '#000';
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.stroke();
            lastX = x;
            lastY = y;
        }

        function stopDraw() {
            dibujando = false;
            // Guardar firma en base64 en input oculto
            input.value = canvas.toDataURL('image/png').split(',')[1];
        }

        // --- Eventos de ratón ---
        canvas.addEventListener('mousedown', e => startDraw(e.offsetX, e.offsetY));
        canvas.addEventListener('mousemove', e => draw(e.offsetX, e.offsetY));
        canvas.addEventListener('mouseup', stopDraw);
        canvas.addEventListener('mouseleave', stopDraw);

        // --- Eventos táctiles ---
        canvas.addEventListener('touchstart', e => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            startDraw((touch.clientX - rect.left), (touch.clientY - rect.top));
        });

        canvas.addEventListener('touchmove', e => {
            e.preventDefault();
            const rect = canvas.getBoundingClientRect();
            const touch = e.touches[0];
            draw((touch.clientX - rect.left), (touch.clientY - rect.top));
        });

        canvas.addEventListener('touchend', stopDraw);

        // --- Botón borrar ---
        const resetBtn = document.createElement('button');
        resetBtn.type = 'button';
        resetBtn.textContent = 'Borrar';
        resetBtn.style.display = 'block';
        resetBtn.style.margin = '10px auto';
        resetBtn.addEventListener('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
            input.value = ''; // limpia base64
        });
        container.appendChild(resetBtn);

        // --- Guardar automáticamente al enviar el form ---
        const form = input.closest('form');
        if (form) {
            form.addEventListener('submit', () => {
                input.value = canvas.toDataURL('image/png').split(',')[1];
            });
        }

        // --- Ocultar input original ---
        input.style.display = 'none';
    });
});

