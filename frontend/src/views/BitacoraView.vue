<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';

const historial = ref([]);
const cargando = ref(true);
const filtroEmpleado = ref('Todos');
const busquedaTexto = ref('');

onMounted(async () => {
  try {
    const response = await api.get('completados/');
    historial.value = response.data;
  } catch (error) {
    console.error(error);
  } finally {
    cargando.value = false;
  }
});

const formatoFecha = (fechaStr) => {
  if (!fechaStr) return '-';
  return fechaStr; 
};

const totalCerradas = computed(() => historial.value.length);

const personalParticipante = computed(() => {
  const unicos = new Set(historial.value.map(item => item.nombre).filter(n => n));
  return unicos.size;
});

const ultimoCierre = computed(() => {
  if (historial.value.length === 0) return '-';
  const fechas = historial.value.map(item => new Date(item.fecha_cierre));
  const maxFecha = new Date(Math.max(...fechas));
  return maxFecha.toISOString().split('T')[0];
});

const empleadosUnicos = computed(() => {
  const unicos = new Set(historial.value.map(item => item.nombre).filter(n => n));
  return Array.from(unicos).sort();
});

const historialFiltrado = computed(() => {
  let filtrado = historial.value;
  
  if (filtroEmpleado.value !== 'Todos') {
    filtrado = filtrado.filter(item => item.nombre === filtroEmpleado.value);
  }
  
  if (busquedaTexto.value) {
    const query = busquedaTexto.value.toLowerCase();
    filtrado = filtrado.filter(item => 
      (item.tarea && item.tarea.toLowerCase().includes(query)) || 
      (item.maquina && item.maquina.toLowerCase().includes(query))
    );
  }
  
  return filtrado;
});
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="header-content">
        <div class="title-with-indicator">
          <div class="indicator-bar"></div>
          <h1 class="main-title">Bitacora de Actividades</h1>
        </div>
        <p class="sub-title">Historial completo de todas las tareas cerradas al 100%</p>
      </div>
    </header>

    <div v-if="cargando" class="loader-container">
      <div class="spinner"></div>
      <span>Cargando bitacora historica...</span>
    </div>

    <main v-else class="dashboard-content fade-in">
      
      <div class="kpi-grid">
        <div class="kpi-card-dark">
          <span class="kpi-label">TOTAL CERRADAS</span>
          <span class="kpi-value">{{ totalCerradas }}</span>
        </div>
        <div class="kpi-card-dark">
          <span class="kpi-label">PERSONAL PARTICIPANTE</span>
          <span class="kpi-value">{{ personalParticipante }}</span>
        </div>
        <div class="kpi-card-dark">
          <span class="kpi-label">ULTIMO CIERRE</span>
          <span class="kpi-value">{{ ultimoCierre }}</span>
        </div>
      </div>

      <div class="filter-section">
        <div class="filter-group">
          <label>FILTRAR POR EMPLEADO</label>
          <select v-model="filtroEmpleado" class="modern-select">
            <option value="Todos">Todos</option>
            <option v-for="emp in empleadosUnicos" :key="emp" :value="emp">{{ emp }}</option>
          </select>
        </div>
        <div class="filter-group flex-grow">
          <label>BUSCAR ACTIVIDAD O MAQUINA</label>
          <input v-model="busquedaTexto" type="text" class="modern-input" placeholder="Ej. motor, excavadora..." />
        </div>
      </div>

      <div class="content-panel">
        <div class="table-wrapper">
          <table class="modern-table">
            <thead>
              <tr>
                <th>Empleado</th>
                <th>Actividad</th>
                <th>Maquina</th>
                <th>Fecha Inicio</th>
                <th>Fecha Cierre</th>
                <th class="text-right">Dias</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="registro in historialFiltrado" :key="registro.id">
                <td class="cell-name">{{ registro.nombre }}</td>
                <td>{{ registro.tarea }}</td>
                <td class="cell-machine">{{ registro.maquina }}</td>
                <td class="cell-date">{{ formatoFecha(registro.fecha_inicio) }}</td>
                <td class="cell-date">{{ formatoFecha(registro.fecha_cierre) }}</td>
                <td class="cell-number">{{ registro.dias_duracion }}</td>
              </tr>
              <tr v-if="historialFiltrado.length === 0">
                <td colspan="6" class="empty-msg">No se encontraron registros que coincidan con la busqueda.</td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

    </main>
  </div>
</template>

<style src="./BitacoraView.css" scoped></style>