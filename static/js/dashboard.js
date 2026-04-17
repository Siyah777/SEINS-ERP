let clientesChart;
let tiposChart;
let costosChart;
let comparativoChart;
let tendenciaChart;
let equiposChart;
let equiposCostosChart;


async function cargarDashboard() {

let mes = document.getElementById('mes').value;
let anio = document.getElementById('anio').value;

let r = await fetch(`/indicadores/api/?mes=${mes}&anio=${anio}`);
let data = await r.json();


// ==================
// KPI
// ==================
document.getElementById('total_ots').innerText =
data.kpis.total_ots;

document.getElementById('facturacion').innerText =
"$" + Number(data.kpis.facturacion_total).toFixed(2);

document.getElementById('preventivos').innerText =
data.kpis.preventivos;

document.getElementById('correctivos').innerText =
data.kpis.correctivos;


// ==================
// CLIENTES TOP
// ==================
if (clientesChart) clientesChart.destroy();

clientesChart = new Chart(
document.getElementById('clientesChart'),
{
type:'bar',
data:{
labels:data.clientes_top.map(x => x.cliente__nombre_empresa),
datasets:[{
label:'OTs por clientes',
data:data.clientes_top.map(x => x.total)
}]
}
}
);


// ==================
// TIPOS ACTIVIDAD
// ==================
if (tiposChart) tiposChart.destroy();

tiposChart = new Chart(
document.getElementById('tiposChart'),
{
type:'pie',
data:{
labels:data.tipos.map(x => x.tipo_actividad),
datasets:[{
data:data.tipos.map(x => x.total)
}]
}
}
);


// ==================
// COSTOS CLIENTES
// ==================
if (costosChart) costosChart.destroy();

costosChart = new Chart(
document.getElementById('costosChart'),
{
type:'bar',
data:{
labels:data.costos.map(x => x.cliente__nombre_empresa),
datasets:[{
label:'Costos asociados por cliente',
data:data.costos.map(x => x.total)
}]
}
}
);

// ==================
// EQUIPOS CON MÁS OTs
// ==================
if (equiposChart) equiposChart.destroy();

equiposChart = new Chart(
document.getElementById('equiposChart'),
{
type:'bar',
data:{
labels:data.equipos_top.map(x => x.equipo__nombre),
datasets:[{
label:'Equipos con mas Ots asiganadas',
data:data.equipos_top.map(x => x.total)
}]
}
}
);


// ==================
// EQUIPOS CON MÁS COSTOS
// ==================
if (equiposCostosChart) equiposCostosChart.destroy();

equiposCostosChart = new Chart(
document.getElementById('equiposCostosChart'),
{
type:'bar',
data:{
labels:data.equipos_costos.map(x => x.equipo__nombre),
datasets:[{
label:'Equipos con mas costos asociados',
data:data.equipos_costos.map(x => x.total)
}]
}
}
);

// ==================
// COMPARATIVO
// ==================
if (comparativoChart) comparativoChart.destroy();

comparativoChart = new Chart(
document.getElementById('comparativoChart'),
{
type:'bar',
data:{
labels:data.comparativo.map(x => "Mes " + x.mes),
datasets:[{
label:'Tendencia mensual de costos',
data:data.comparativo.map(x => x.total)
}]
}
}
);

// ==================
// TENDENCIA
// ==================
if (tendenciaChart) tendenciaChart.destroy();

tendenciaChart = new Chart(
document.getElementById('tendenciaChart'),
{
type:'line',
data:{
labels:[
"Ene","Feb","Mar","Abr","May","Jun",
"Jul","Ago","Sep","Oct","Nov","Dic"
],
datasets:[
{
label:'Tendencia mensual de preventivos',
data:llenarMeses(data.tendencia.preventivos)
},
{
label:'Tendencia mensual de correctivos',
data:llenarMeses(data.tendencia.correctivos)
}
]
}
}
);

}

function llenarMeses(lista){

let meses = Array(12).fill(0);

lista.forEach(item => {
meses[item.mes - 1] = item.total;
});

return meses;
}

async function exportarPDF() {

let mes = document.getElementById('mes').value;
let anio = document.getElementById('anio').value;

/* mejorar resolución */
if (clientesChart) clientesChart.resize(1200,700);
if (tiposChart) tiposChart.resize(1200,700);
if (costosChart) costosChart.resize(1200,700);
if (equiposChart) equiposChart.resize(1200,700);
if (equiposCostosChart) equiposCostosChart.resize(1200,700);
if (comparativoChart) comparativoChart.resize(1200,700);
if (tendenciaChart) tendenciaChart.resize(1200,700);

/* imágenes */
let clientes = clientesChart ? clientesChart.toBase64Image() : "";
let tipos = tiposChart ? tiposChart.toBase64Image() : "";
let costos = costosChart ? costosChart.toBase64Image() : "";
let equipos = equiposChart ? equiposChart.toBase64Image() : "";
let equipos_costos = equiposCostosChart ? equiposCostosChart.toBase64Image() : "";
let comparativo = comparativoChart ? comparativoChart.toBase64Image() : "";
let tendencia = tendenciaChart ? tendenciaChart.toBase64Image() : "";

/* petición */
let response = await fetch('/indicadores/pdf/', {
method:'POST',
headers:{
'Content-Type':'application/json',
'X-CSRFToken': getCookie('csrftoken')
},
body: JSON.stringify({
mes: mes,
anio: anio,
clientes: clientes,
tipos: tipos,
costos: costos,
equipos: equipos,
equipos_costos: equipos_costos,
comparativo: comparativo,
tendencia: tendencia
})
});

/* blob pdf */
let blob = await response.blob();

let disposition = response.headers.get('Content-Disposition');
let filename = "Informe.pdf";

if (disposition && disposition.includes("filename=")) {
filename = disposition
.split("filename=")[1]
.replace(/"/g,'')
.trim();
}

/* descargar */
let url = window.URL.createObjectURL(blob);

let a = document.createElement('a');
a.href = url;
a.download = filename;

document.body.appendChild(a);
a.click();
a.remove();

window.URL.revokeObjectURL(url);
}


/* CSRF TOKEN */
function getCookie(name) {

let cookieValue = null;

if (document.cookie && document.cookie !== '') {

let cookies = document.cookie.split(';');

for (let i = 0; i < cookies.length; i++) {

let cookie = cookies[i].trim();

if (
cookie.substring(0, name.length + 1) ===
(name + '=')
) {
cookieValue = decodeURIComponent(
cookie.substring(name.length + 1)
);
break;
}

}
}

return cookieValue;
}

cargarDashboard();