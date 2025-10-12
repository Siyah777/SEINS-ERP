document.addEventListener('DOMContentLoaded', function() {
    ['firma_cliente', 'firma_tecnico'].forEach(function(fieldName) {
        let input = document.getElementById('id_' + fieldName);
        if (!input) return;

        // Crear canvas
        let canvas = document.createElement('canvas');
        canvas.width = 300;
        canvas.height = 100;
        canvas.style.border = "1px solid #000";
        input.parentNode.insertBefore(canvas, input.nextSibling);

        let ctx = canvas.getContext('2d');
        let drawing = false;

        canvas.addEventListener('mousedown', e => drawing = true);
        canvas.addEventListener('mouseup', e => drawing = false);
        canvas.addEventListener('mouseleave', e => drawing = false);
        canvas.addEventListener('mousemove', e => {
            if (!drawing) return;
            ctx.lineWidth = 2;
            ctx.lineCap = 'round';
            ctx.strokeStyle = '#000';
            ctx.lineTo(e.offsetX, e.offsetY);
            ctx.stroke();
            ctx.beginPath();
            ctx.moveTo(e.offsetX, e.offsetY);
        });

        // Reset
        let resetBtn = document.createElement('button');
        resetBtn.type = 'button';
        resetBtn.textContent = 'Reset';
        resetBtn.addEventListener('click', () => {
            ctx.clearRect(0, 0, canvas.width, canvas.height);
        });
        canvas.parentNode.insertBefore(resetBtn, canvas.nextSibling);

        // Al enviar el form, guardar base64 en input
        input.closest('form').addEventListener('submit', e => {
            input.value = canvas.toDataURL();
        });

        // Ocultar input original
        input.style.display = 'none';
    });
});
