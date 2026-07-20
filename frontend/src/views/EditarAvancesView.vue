<script setup>
import { ref, onMounted, watch, computed } from 'vue';
import api from '../services/api';

const trabajadores = ref([]);
const maquinas = ref([]);
const trabajadorSeleccionadoId = ref('');
const trabajadorActual = ref(null);
const mensaje = ref({ texto: '', tipo: '' });

const cargarDatos = async () => {
  try {
    const [resTrabajadores, resMaquinas] = await Promise.all([
      api.get('bitacora/'),
      api.get('maquinas/')
    ]);
    trabajadores.value = resTrabajadores.data;
    maquinas.value = resMaquinas.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(cargarDatos);

watch(trabajadorSeleccionadoId, (nuevoId) => {
  if (nuevoId) {
    const encontrado = trabajadores.value.find(t => t.id === nuevoId);
    trabajadorActual.value = JSON.parse(JSON.stringify(encontrado));
  } else {
    trabajadorActual.value = null;
  }
});

const ajustarAvance = (i, cantidad) => {
  if (!trabajadorActual.value) return;
  const actual = parseInt(trabajadorActual.value[`avance_${i}`]) || 0;
  let nuevo = actual + cantidad;
  if (nuevo < 0) nuevo = 0;
  if (nuevo > 100) nuevo = 100;
  trabajadorActual.value[`avance_${i}`] = nuevo;
};

const actividadesActivas = computed(() => {
  if (!trabajadorActual.value) return [];
  const activas = [];
  for (let i = 1; i <= 5; i++) {
    const tarea = trabajadorActual.value[`tarea_${i}`];
    if (tarea && tarea !== '-' && tarea.trim() !== '') {
      activas.push({
        espacio: i,
        tarea: tarea,
        avance: trabajadorActual.value[`avance_${i}`] || 0
      });
    }
  }
  return activas;
});

const borrarActividad = async (espacio) => {
  if (!confirm('¿Eliminar esta actividad permanentemente? Esta accion no se puede deshacer.')) return;
  
  trabajadorActual.value[`tarea_${espacio}`] = '-';
  trabajadorActual.value[`maquina_${espacio}`] = '-';
  trabajadorActual.value[`avance_${espacio}`] = 0;
  
  await guardarAvances(true);
};

const guardarAvances = async (esBorrado = false) => {
  if (!trabajadorActual.value) return;

  try {
    await api.patch(`bitacora/${trabajadorActual.value.id}/`, trabajadorActual.value);
    
    if (esBorrado) {
      mensaje.value = { texto: 'Actividad eliminada correctamente.', tipo: 'success' };
    } else {
      mensaje.value = { texto: 'Avances actualizados exitosamente.', tipo: 'success' };
    }
    
    await cargarDatos();
    
    const actualizado = trabajadores.value.find(t => t.id === trabajadorSeleccionadoId.value);
    trabajadorActual.value = actualizado ? JSON.parse(JSON.stringify(actualizado)) : null;

  } catch (error) {
    mensaje.value = { texto: 'Error al actualizar los datos.', tipo: 'error' };
  }
  
  setTimeout(() => mensaje.value.texto = '', 4000);
};
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="main-title">Editar Avances</h1>
        <p class="sub-title">Actualiza el progreso de las actividades. Al llegar a 100%, la tarea se enviara al historial.</p>
      </div>
    </header>

    <div v-if="mensaje.texto" :class="['alert-toast', mensaje.tipo === 'success' ? 'toast-success' : 'toast-error']">
      {{ mensaje.texto }}
    </div>

    <div class="content-panel selector-panel">
      <div class="input-group">
        <label>Seleccionar Trabajador</label>
        <select v-model="trabajadorSeleccionadoId" class="modern-select">
          <option value="">-- Elige un trabajador --</option>
          <option v-for="t in trabajadores" :key="t.id" :value="t.id">
            {{ t.nombre }}
          </option>
        </select>
      </div>
    </div>

    <div v-if="trabajadorActual" class="split-layout fade-in">
      
      <div class="content-panel main-form-panel">
        <form @submit.prevent="guardarAvances(false)" class="modern-form">
          
          <div v-for="i in 5" :key="i" class="workspace-block">
            <div class="workspace-header">
              <span class="workspace-badge">ESPACIO {{ i }}</span>
            </div>
            
            <div class="form-cols custom-grid">
              <div class="input-group">
                <label>Tarea {{ i }}</label>
                <input v-model="trabajadorActual['tarea_' + i]" type="text" class="modern-input" placeholder="-" />
              </div>

              <div class="input-group">
                <label>Maquina {{ i }}</label>
                <select v-model="trabajadorActual['maquina_' + i]" class="modern-select">
                  <option value="-">- N/A -</option>
                  <option v-for="m in maquinas" :key="m.id" :value="m.nombre">
                    {{ m.nombre }}
                  </option>
                </select>
              </div>

              <div class="input-group">
                <label>Avance %</label>
                <div class="stepper-container">
                  <button type="button" class="stepper-btn" @click="ajustarAvance(i, -1)">-</button>
                  <input v-model="trabajadorActual['avance_' + i]" type="number" min="0" max="100" class="stepper-input" />
                  <button type="button" class="stepper-btn" @click="ajustarAvance(i, 1)">+</button>
                </div>
              </div>
            </div>
          </div>

          <div class="form-action">
            <button type="submit" class="btn-primary full-width-btn">Guardar Cambios</button>
          </div>
        </form>
      </div>

      <div class="side-panel">
        <div class="panel-header">
          <h2>Eliminar Actividad</h2>
          <p class="sub-title">Elimina una actividad por error. Esta accion no se puede deshacer.</p>
        </div>
        
        <div class="delete-list">
          <div v-for="act in actividadesActivas" :key="act.espacio" class="delete-card">
            <div class="delete-info">
              <span class="delete-label">TAREA {{ act.espacio }}</span>
              <div class="delete-title">
                {{ act.tarea }} <span class="delete-percent">{{ act.avance }}%</span>
              </div>
            </div>
            <button type="button" class="btn-danger-solid" @click="borrarActividad(act.espacio)">BORRAR</button>
          </div>
          
          <div v-if="actividadesActivas.length === 0" class="empty-msg">
            No hay actividades activas para eliminar.
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<style src="./EditarAvancesView.css" scoped></style>