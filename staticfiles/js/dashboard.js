async function cargarDashboard() {

let r = await fetch('/api/');
let data = await r.json();

document.getElementById('total_ots').innerText = data.kpis.total_ots;
document.getElementById('clientes').innerText = data.kpis.clientes_atendidos;
document.getElementById('facturacion').innerText = "$" + data.kpis.facturacion_total;
document.getElementById('preventivos').innerText = data.kpis.preventivos;


// CLIENTES TOP
new Chart(document.getElementById('clientesChart'), {
type: 'bar',
data: {
labels: data.clientes_top.map(x => x.cliente__nombre_empresa),
datasets: [{
label: 'OTs',
data: data.clientes_top.map(x => x.total)
}]
}
});


// TIPOS
new Chart(document.getElementById('tiposChart'), {
type: 'pie',
data: {
labels: data.tipos.map(x => x.tipo_actividad),
datasets: [{
data: data.tipos.map(x => x.total)
}]
}
});


// COSTOS
new Chart(document.getElementById('costosChart'), {
type: 'bar',
data: {
labels: data.costos.map(x => x.cliente__nombre_empresa),
datasets: [{
label: 'Facturación',
data: data.costos.map(x => x.total)
}]
}
});

}

cargarDashboard();