<script setup>
import { ref, onMounted, onUnmounted, computed } from 'vue';
import api from '../services/api';
import { Bar } from 'vue-chartjs';
import { Chart as ChartJS, Title, Tooltip, Legend, BarElement, CategoryScale, LinearScale } from 'chart.js';
import ChartDataLabels from 'chartjs-plugin-datalabels';

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ChartDataLabels);

const activeTab = ref('Vision General');
const tabs = ['Vision General', 'Top Maquinas', 'Top Trabajadores', 'Control Herramientas', 'Taller', 'Rendimiento Diesel'];

const bitacora = ref([]);
const completadosDatos = ref([]);
const herramientas = ref([]);
const taller = ref([]);
const maquinasCatalogo = ref([]);
const cargando = ref(true);

const saludo = ref('');
const nombreUsuario = ref('');
const clima = ref({ temp: '--', desc: 'Cargando...', icono: 'nublado' });

let intervaloActualizacion;

onMounted(async () => {
  determinarSaludo();
  nombreUsuario.value = localStorage.getItem('user') || 'Administrador';
  iniciarClima();
  await cargarDatosPrincipales();

  intervaloActualizacion = setInterval(() => {
    cargarDatosPrincipales();
  }, 300000);
});

onUnmounted(() => {
  if (intervaloActualizacion) {
    clearInterval(intervaloActualizacion);
  }
});

const determinarSaludo = () => {
  const hora = new Date().getHours();
  if (hora >= 5 && hora < 12) saludo.value = 'Buenos días';
  else if (hora >= 12 && hora < 19) saludo.value = 'Buenas tardes';
  else saludo.value = 'Buenas noches';
};

const obtenerClima = async (lat = 30.98, lon = -110.30, nombreCiudad = 'Cananea, Son.') => {
  try {
    const res = await fetch(`https://api.open-meteo.com/v1/forecast?latitude=${lat}&longitude=${lon}&current_weather=true`);
    const data = await res.json();
    const temp = data.current_weather.temperature;

    let icono = 'nublado';
    if (data.current_weather.weathercode <= 3) icono = 'despejado';
    else if (data.current_weather.weathercode >= 51) icono = 'lluvia';

    clima.value = {
      temp: `${Math.round(temp)}°C`,
      desc: nombreCiudad,
      icono
    };
  } catch (e) {
    clima.value = { temp: '--', desc: 'No disponible', icono: 'nublado' };
  }
};

const iniciarClima = () => {
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position) => obtenerClima(position.coords.latitude, position.coords.longitude, 'Ubicación Local'),
      () => obtenerClima()
    );
  } else {
    obtenerClima();
  }
};

const cargarDatosPrincipales = async () => {
  try {
    const [resBitacora, resCompletados, resHerramientas, resTaller, resMaquinas] = await Promise.all([
      api.get('bitacora/'),
      api.get('completados/'),
      api.get('herramientas/'),
      api.get('taller/'),
      api.get('maquinas/')
    ]);
    bitacora.value = resBitacora.data;
    completadosDatos.value = resCompletados.data;
    herramientas.value = resHerramientas.data;
    taller.value = resTaller.data;
    maquinasCatalogo.value = resMaquinas.data;
  } catch (error) {
    console.error(error);
  } finally {
    cargando.value = false;
  }
};

const calcularDias = (fechaStr) => {
  if (!fechaStr) return 0;
  
  let dateString = fechaStr;
  if (dateString.includes('T')) {
    dateString = dateString.split('T')[0];
  }
  
  const parts = dateString.split('-');
  if (parts.length !== 3) return 0;
  
  const year = parseInt(parts[0], 10);
  const month = parseInt(parts[1], 10) - 1;
  const day = parseInt(parts[2], 10);
  
  const inicio = new Date(year, month, day);
  const hoy = new Date();
  
  const utcInicio = Date.UTC(inicio.getFullYear(), inicio.getMonth(), inicio.getDate());
  const utcHoy = Date.UTC(hoy.getFullYear(), hoy.getMonth(), hoy.getDate());
  
  const diferenciaMs = utcHoy - utcInicio;
  const dias = Math.floor(diferenciaMs / (1000 * 60 * 60 * 24));
  
  return dias > 0 ? dias : 0;
};

const formatoFecha = (fechaStr) => {
  if (!fechaStr) return '-';
  let dateString = fechaStr;
  if (dateString.includes('T')) {
    dateString = dateString.split('T')[0];
  }
  const parts = dateString.split('-');
  if (parts.length !== 3) return '-';
  return `${parts[0]}-${parts[1]}-${parts[2]}`;
};

const formatoFechaHora = (isoStr) => {
  if (!isoStr) return '-';
  const fecha = new Date(isoStr);
  return fecha.toLocaleString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};

const totalPersonal = computed(() => bitacora.value.length);
const actividadesCerradas = computed(() => completadosDatos.value.length);

const avancePromedio = computed(() => {
  let totalSuma = 0;
  let totalTareasActivas = 0;
  bitacora.value.forEach(t => {
    for (let i = 1; i <= 5; i++) {
      if (t[`tarea_${i}`] && t[`tarea_${i}`] !== '-') {
        totalSuma += t[`avance_${i}`] || 0;
        totalTareasActivas++;
      }
    }
  });
  return totalTareasActivas === 0 ? '0.0' : (totalSuma / totalTareasActivas).toFixed(1);
});

const obtenerTareasActivas = (trabajador) => {
  const tareas = [];
  for (let i = 1; i <= 5; i++) {
    if (trabajador[`tarea_${i}`] && trabajador[`tarea_${i}`] !== '-') {
      tareas.push({
        numero: i, descripcion: trabajador[`tarea_${i}`], maquina: trabajador[`maquina_${i}`],
        avance: trabajador[`avance_${i}`], dias: calcularDias(trabajador[`fecha_inicio_${i}`])
      });
    }
  }
  return tareas;
};

const topMaquinasData = computed(() => {
  const conteo = {};
  completadosDatos.value.forEach(item => {
    const maq = item.maquina;
    if (maq && maq !== '-') conteo[maq] = (conteo[maq] || 0) + 1;
  });
  const sorted = Object.entries(conteo).sort((a, b) => b[1] - a[1]).slice(0, 10);
  return {
    labels: sorted.map(item => item[0]),
    datasets: [{ label: 'Servicios', backgroundColor: '#2C3E50', data: sorted.map(item => item[1]), borderRadius: 6 }]
  };
});

const chartOptions = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#333333', font: { weight: 'bold', family: 'Inter', size: 12 } } },
  scales: {
    y: { beginAtZero: true, grid: { color: '#F0F2F5', drawBorder: false }, title: { display: true, text: 'Servicios', color: '#64748B', font: { family: 'Inter', weight: '600' } } },
    x: { grid: { display: false, drawBorder: false }, title: { display: true, text: 'Máquina', color: '#64748B', font: { family: 'Inter', weight: '600' } } }
  }
};

const maquinaSeleccionada = ref('');
const maquinasConHistorial = computed(() => {
  const unicas = new Set(completadosDatos.value.map(item => item.maquina).filter(m => m && m !== '-'));
  return Array.from(unicas).sort();
});
const historialFiltrado = computed(() => completadosDatos.value.filter(item => item.maquina === maquinaSeleccionada.value));

const topTrabajadoresData = computed(() => {
  const conteo = {};
  completadosDatos.value.forEach(item => {
    const trab = item.nombre;
    if (trab) conteo[trab] = (conteo[trab] || 0) + 1;
  });
  const sorted = Object.entries(conteo).sort((a, b) => b[1] - a[1]).slice(0, 10);
  return {
    labels: sorted.map(item => item[0]),
    datasets: [{ label: 'Tareas', backgroundColor: '#E74C3C', data: sorted.map(item => item[1]), borderRadius: 6 }]
  };
});

const chartOptionsTrabajadores = {
  responsive: true, maintainAspectRatio: false,
  plugins: { legend: { display: false }, datalabels: { anchor: 'end', align: 'end', color: '#333333', font: { weight: 'bold', family: 'Inter', size: 12 } } },
  scales: {
    y: { beginAtZero: true, grid: { color: '#F0F2F5', drawBorder: false }, title: { display: true, text: 'Tareas', color: '#64748B', font: { family: 'Inter', weight: '600' } } },
    x: { grid: { display: false, drawBorder: false }, title: { display: true, text: 'Trabajador', color: '#64748B', font: { family: 'Inter', weight: '600' } } }
  }
};

const trabajadorSeleccionado = ref('');
const trabajadoresConHistorial = computed(() => {
  const unicas = new Set(completadosDatos.value.map(item => item.nombre).filter(n => n));
  return Array.from(unicas).sort();
});
const historialTrabajadorFiltrado = computed(() => completadosDatos.value.filter(item => item.nombre === trabajadorSeleccionado.value));

const formHerramienta = ref({ trabajador: '', herramienta: '', tarea: '' });
const herramientasEnUso = computed(() => herramientas.value.filter(h => h.estado === 'Prestado').sort((a, b) => new Date(b.fecha_prestamo) - new Date(a.fecha_prestamo)));
const historialDevoluciones = computed(() => herramientas.value.filter(h => h.estado === 'Devuelto').sort((a, b) => new Date(b.fecha_devolucion) - new Date(a.fecha_devolucion)));

const registrarSalidaHerramienta = async () => {
  if (!formHerramienta.value.trabajador || !formHerramienta.value.herramienta) return;
  try {
    await api.post('herramientas/', { ...formHerramienta.value, tarea: formHerramienta.value.tarea || 'Sin especificar', fecha_prestamo: new Date().toISOString(), estado: 'Prestado' });
    formHerramienta.value = { trabajador: '', herramienta: '', tarea: '' };
    await cargarDatosPrincipales();
  } catch (e) { console.error(e); }
};

const devolverHerramienta = async (id) => {
  try {
    await api.patch(`herramientas/${id}/`, { estado: 'Devuelto', fecha_devolucion: new Date().toISOString() });
    await cargarDatosPrincipales();
  } catch (e) { console.error(e); }
};

const formTaller = ref({ maquina: '', falla: '' });

const obtenerActividadesPorMaquina = (nombreMaquina) => {
  const tareas = [];
  bitacora.value.forEach(t => {
    for (let i = 1; i <= 5; i++) {
      if (t[`maquina_${i}`] === nombreMaquina && t[`tarea_${i}`] && t[`tarea_${i}`] !== '-') {
        tareas.push({
          trabajador: t.nombre,
          descripcion: t[`tarea_${i}`],
          avance: t[`avance_${i}`]
        });
      }
    }
  });
  return tareas;
};

const registrarIngresoTaller = async () => {
  if (!formTaller.value.maquina || !formTaller.value.falla) return;
  try {
    const hoy = new Date().toISOString().split('T')[0];
    await api.post('taller/', {
      maquina: formTaller.value.maquina,
      motivo: formTaller.value.falla,
      fecha_ingreso: hoy
    });
    formTaller.value = { maquina: '', falla: '' };
    await cargarDatosPrincipales();
  } catch (error) {
    console.error(error.response?.data || error);
  }
};

const marcarReparada = async (id) => {
  try {
    await api.delete(`taller/${id}/`);
    await cargarDatosPrincipales();
  } catch (error) {
    console.error(error);
  }
};
</script>

<template>
  <div class="dashboard-wrapper">

    <header class="dashboard-main-header">
      <div class="header-left">
        <h1 class="main-title">Hola, {{ saludo.toLowerCase() }} bienvenido de nuevo <span class="greeting-name">{{ nombreUsuario }}</span></h1>
        <h2 class="sub-title-heading">Estado operativo del personal y equipos</h2>
      </div>

      <div class="header-right">
        <div class="weather-widget">
          <div class="weather-icon-wrapper">
            <svg v-if="clima.icono === 'despejado'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <circle cx="12" cy="12" r="4" />
              <line x1="12" y1="2" x2="12" y2="4" />
              <line x1="12" y1="20" x2="12" y2="22" />
              <line x1="4.93" y1="4.93" x2="6.34" y2="6.34" />
              <line x1="17.66" y1="17.66" x2="19.07" y2="19.07" />
              <line x1="2" y1="12" x2="4" y2="12" />
              <line x1="20" y1="12" x2="22" y2="12" />
              <line x1="4.93" y1="19.07" x2="6.34" y2="17.66" />
              <line x1="17.66" y1="6.34" x2="19.07" y2="4.93" />
            </svg>
            <svg v-else-if="clima.icono === 'lluvia'" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 16.58A5 5 0 0018 7h-1.26A8 8 0 104 15.25" />
              <line x1="8" y1="19" x2="8" y2="21" />
              <line x1="12" y1="19" x2="12" y2="21" />
              <line x1="16" y1="19" x2="16" y2="21" />
            </svg>
            <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <path d="M20 16.58A5 5 0 0018 7h-1.26A8 8 0 104 15.25" />
            </svg>
          </div>
          <div class="weather-info">
            <span class="weather-temp">{{ clima.temp }}</span>
            <span class="weather-desc">{{ clima.desc }}</span>
          </div>
        </div>
      </div>
    </header>

    <nav class="modern-tabs">
      <button
        v-for="tab in tabs"
        :key="tab"
        :class="['tab-btn', { 'tab-active': activeTab === tab }]"
        @click="activeTab = tab"
      >
        {{ tab }}
      </button>
    </nav>

    <div v-if="cargando" class="loader-container">
      <div class="spinner"></div>
      <span>Cargando datos...</span>
    </div>

    <main class="dashboard-content" v-else>

      <div v-if="activeTab === 'Vision General'" class="fade-in">
        <div class="kpi-container">
          <div class="kpi-box">
            <span class="kpi-label">TOTAL PERSONAL</span>
            <span class="kpi-number">{{ totalPersonal }}</span>
          </div>
          <div class="kpi-box kpi-highlight">
            <span class="kpi-label">AVANCE PROMEDIO</span>
            <span class="kpi-number">{{ avancePromedio }}%</span>
          </div>
          <div class="kpi-box">
            <span class="kpi-label">ACTIVIDADES CERRADAS</span>
            <span class="kpi-number">{{ actividadesCerradas }}</span>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Registro Completo</h2>
            <p>Todos los trabajadores activos en el sistema</p>
          </div>
          <div class="table-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Nombre</th>
                  <th>Fecha</th>
                  <th>Tarea Principal</th>
                  <th>Máquina</th>
                  <th>Avance</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="t in bitacora" :key="t.id">
                  <td class="cell-id">TRAB-00{{ t.id }}</td>
                  <td class="cell-name">{{ t.nombre }}</td>
                  <td class="cell-date">{{ t.fecha }}</td>
                  <td>{{ t.tarea_1 }}</td>
                  <td class="cell-machine">{{ t.maquina_1 }}</td>
                  <td>
                    <div class="mini-progress">
                      <div class="mini-progress-bar" :style="{ width: t.avance_1 + '%' }"></div>
                      <span>{{ t.avance_1 }}%</span>
                    </div>
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Avance por Trabajador</h2>
            <p>Progreso individual de actividades activas</p>
          </div>
          <div class="masonry-grid">
            <div v-for="trabajador in bitacora" :key="trabajador.id" class="glass-card">
              <div class="card-top">
                <span class="badge-id">TRAB-00{{ trabajador.id }}</span>
                <h3>{{ trabajador.nombre }}</h3>
              </div>
              <div class="card-body">
                <span class="section-label">PROGRESO ACTUAL</span>
                <div v-for="tarea in obtenerTareasActivas(trabajador)" :key="tarea.numero" class="task-item">
                  <div class="task-header">
                    <span class="task-desc">{{ tarea.descripcion }}</span>
                    <span class="task-meta">{{ tarea.maquina }} | {{ tarea.dias }}d</span>
                  </div>
                  <div class="track-bar">
                    <div class="fill-bar" :style="{ width: tarea.avance + '%' }"></div>
                  </div>
                  <div class="task-footer">
                    <span class="percent-val">{{ tarea.avance }}%</span>
                  </div>
                </div>
                <div v-if="obtenerTareasActivas(trabajador).length === 0" class="empty-msg">
                  Sin actividades asignadas
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'Top Maquinas'" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Top Máquinas</h2>
            <p>Equipos con mayor cantidad de servicios completados</p>
          </div>
          <div class="chart-box">
            <Bar :data="topMaquinasData" :options="chartOptions"/>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Historial por Máquina</h2>
          </div>
          <div class="input-row">
            <div class="input-group">
              <label>Selecciona una máquina</label>
              <select v-model="maquinaSeleccionada" class="modern-select">
                <option value="" disabled>Elige del catálogo...</option>
                <option v-for="m in maquinasConHistorial" :key="m" :value="m">{{ m }}</option>
              </select>
            </div>
          </div>

          <div v-if="maquinaSeleccionada" class="data-reveal">
            <span class="result-count">{{ historialFiltrado.length }} registros encontrados</span>
            <div class="table-wrapper">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>Empleado</th>
                    <th>Actividad</th>
                    <th>Fecha Inicio</th>
                    <th>Fecha Cierre</th>
                    <th>Días</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="reg in historialFiltrado" :key="reg.id">
                    <td class="cell-name">{{ reg.nombre }}</td>
                    <td>{{ reg.tarea }}</td>
                    <td class="cell-date">{{ formatoFecha(reg.fecha_inicio) }}</td>
                    <td class="cell-date">{{ formatoFecha(reg.fecha_cierre) }}</td>
                    <td class="cell-highlight">{{ reg.dias_duracion }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'Top Trabajadores'" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Top Trabajadores</h2>
            <p>Personal con mayor cantidad de tareas completadas</p>
          </div>
          <div class="chart-box">
            <Bar :data="topTrabajadoresData" :options="chartOptionsTrabajadores"/>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Historial por Trabajador</h2>
          </div>
          <div class="input-row">
            <div class="input-group">
              <label>Selecciona un trabajador</label>
              <select v-model="trabajadorSeleccionado" class="modern-select">
                <option value="" disabled>Elige del catálogo...</option>
                <option v-for="t in trabajadoresConHistorial" :key="t" :value="t">{{ t }}</option>
              </select>
            </div>
          </div>

          <div v-if="trabajadorSeleccionado" class="data-reveal">
            <span class="result-count">{{ historialTrabajadorFiltrado.length }} registros encontrados</span>
            <div class="table-wrapper">
              <table class="modern-table">
                <thead>
                  <tr>
                    <th>Actividad</th>
                    <th>Máquina</th>
                    <th>Fecha Inicio</th>
                    <th>Fecha Cierre</th>
                    <th>Días</th>
                  </tr>
                </thead>
                <tbody>
                  <tr v-for="reg in historialTrabajadorFiltrado" :key="reg.id">
                    <td>{{ reg.tarea }}</td>
                    <td class="cell-machine">{{ reg.maquina }}</td>
                    <td class="cell-date">{{ formatoFecha(reg.fecha_inicio) }}</td>
                    <td class="cell-date">{{ formatoFecha(reg.fecha_cierre) }}</td>
                    <td class="cell-highlight">{{ reg.dias_duracion }}</td>
                  </tr>
                </tbody>
              </table>
            </div>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'Control Herramientas'" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Registro de Salida</h2>
            <p>Asignación de herramientas de almacén</p>
          </div>
          <form @submit.prevent="registrarSalidaHerramienta" class="modern-form">
            <div class="form-cols">
              <div class="input-group">
                <label>Trabajador</label>
                <select v-model="formHerramienta.trabajador" required class="modern-select">
                  <option value="" disabled>Seleccionar...</option>
                  <option v-for="t in bitacora" :key="t.id" :value="t.nombre">{{ t.nombre }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>Herramienta</label>
                <input v-model="formHerramienta.herramienta" type="text" required class="modern-input" />
              </div>
              <div class="input-group">
                <label>Tarea / Motivo</label>
                <input v-model="formHerramienta.tarea" type="text" placeholder="Opcional" class="modern-input" />
              </div>
            </div>
            <div class="form-action">
              <button type="submit" class="btn-primary">Registrar Salida</button>
            </div>
          </form>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Herramientas en Uso</h2>
            <p>Pendientes de devolución</p>
          </div>
          <div class="tools-grid">
            <div v-for="h in herramientasEnUso" :key="h.id" class="tool-ticket">
              <div class="ticket-left">
                <span class="ticket-user">{{ h.trabajador }}</span>
                <span class="ticket-item">{{ h.herramienta }}</span>
                <span class="ticket-task">{{ h.tarea }}</span>
              </div>
              <div class="ticket-right">
                <span class="ticket-time">{{ formatoFechaHora(h.fecha_prestamo) }}</span>
                <button @click="devolverHerramienta(h.id)" class="btn-secondary">Devolver</button>
              </div>
            </div>
            <div v-if="herramientasEnUso.length === 0" class="empty-msg">
              Almacén completo, no hay herramientas fuera.
            </div>
          </div>
        </div>

        <div class="content-panel">
          <div class="panel-header">
            <h2>Historial de Devoluciones</h2>
          </div>
          <div class="table-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Trabajador</th>
                  <th>Herramienta</th>
                  <th>Tarea</th>
                  <th>Fecha Salida</th>
                  <th>Fecha Entrega</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="h in historialDevoluciones" :key="h.id">
                  <td class="cell-name">{{ h.trabajador }}</td>
                  <td class="cell-machine">{{ h.herramienta }}</td>
                  <td>{{ h.tarea }}</td>
                  <td class="cell-date">{{ formatoFechaHora(h.fecha_prestamo) }}</td>
                  <td class="cell-date">{{ formatoFechaHora(h.fecha_devolucion) }}</td>
                </tr>
                <tr v-if="historialDevoluciones.length === 0">
                  <td colspan="5" class="empty-msg">Sin registros históricos.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-else-if="activeTab === 'Taller'" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Gestión de Taller</h2>
            <p>Registro de equipos en reparación</p>
          </div>
          <form @submit.prevent="registrarIngresoTaller" class="modern-form">
            <div class="form-cols split-1-2">
              <div class="input-group">
                <label>Máquina</label>
                <select v-model="formTaller.maquina" required class="modern-select">
                  <option value="" disabled>Seleccionar...</option>
                  <option v-for="m in maquinasCatalogo" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>Falla Reportada</label>
                <input v-model="formTaller.falla" type="text" required class="modern-input" />
              </div>
            </div>
            <div class="form-action">
              <button type="submit" class="btn-primary">Ingresar al Taller</button>
            </div>
          </form>
        </div>

        <div class="content-panel">
          <div class="panel-header" style="display: flex; justify-content: space-between; align-items: center;">
            <h2>Equipos Activos en Taller</h2>
            <a 
              href="https://grupoleravi.sharepoint.com/:f:/s/Programademantenimiento/IgBEQ002_JlWR60nEEL3tiUtAbMkYMGSlo3Ho9SfGrfRYb0?e=Wh2ygB" 
              target="_blank" 
              rel="noopener noreferrer" 
              class="btn-secondary" 
              style="text-decoration: none; display: flex; align-items: center; gap: 8px;"
            >
              <svg width="18" height="18" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
              </svg>
              Documentos DE MAQUINAS CAIDAS
            </a>
          </div>
          <div class="workshop-grid">
            <div v-for="equipo in taller" :key="equipo.id" class="workshop-card">
              <div class="wk-head">
                <h3 class="wk-machine">{{ equipo.maquina }}</h3>
                <div class="wk-status">
                  <span class="time-tag">{{ calcularDias(equipo.fecha_ingreso) }} días</span>
                  <button @click="marcarReparada(equipo.id)" class="btn-success">Finalizar</button>
                </div>
              </div>
              <div class="wk-body">
                <div class="wk-report">
                  <span>Motivo:</span> {{ equipo.motivo || '-' }}
                </div>
                <div class="wk-activities">
                  <template v-if="obtenerActividadesPorMaquina(equipo.maquina).length > 0">
                    <span class="section-label">TRABAJO EN PROCESO</span>
                    <ul>
                      <li v-for="(act, index) in obtenerActividadesPorMaquina(equipo.maquina)" :key="index">
                        <span class="act-worker">{{ act.trabajador }}</span>
                        <span class="act-desc">{{ act.descripcion }}</span>
                        <span class="act-prog">{{ act.avance }}%</span>
                      </li>
                    </ul>
                  </template>
                  <template v-else>
                    <span class="empty-msg">No hay mecánicos asignados actualmente.</span>
                  </template>
                </div>
              </div>
            </div>
            <div v-if="taller.length === 0" class="empty-msg">
              El taller está vacío en este momento.
            </div>
          </div>
        </div>
      </div>

      <div v-else class="fade-in">
        <div class="content-panel empty-panel">
          <h2>Módulo: {{ activeTab }}</h2>
          <p>Modulo en construccion...</p>
        </div>
      </div>

    </main>
  </div>
</template>

<style src="./DashboardView.css" scoped></style>
