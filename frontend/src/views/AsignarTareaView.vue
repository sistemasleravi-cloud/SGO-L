<script setup>
import { ref, onMounted, computed } from 'vue';
import api from '../services/api';

const trabajadores = ref([]);
const maquinas = ref([]);

const form = ref({
  trabajador_id: '',
  espacio: '1',
  tarea: '',
  maquina: '-'
});

const mensaje = ref({ texto: '', tipo: '' });

onMounted(async () => {
  try {
    const [resTrabajadores, resMaquinas] = await Promise.all([
      api.get('bitacora/'),
      api.get('maquinas/')
    ]);
    trabajadores.value = resTrabajadores.data;
    maquinas.value = resMaquinas.data;
  } catch (error) {
    console.error("Error cargando catalogos:", error);
  }
});

// Computed para obtener los datos del trabajador seleccionado actualmente
const trabajadorSeleccionado = computed(() => {
  if (!form.value.trabajador_id) return null;
  return trabajadores.value.find(t => t.id === form.value.trabajador_id);
});

// Computed para estructurar el estado de los 5 espacios del trabajador
const estadoEspacios = computed(() => {
  if (!trabajadorSeleccionado.value) return [];
  const espacios = [];
  for (let i = 1; i <= 5; i++) {
    const tarea = trabajadorSeleccionado.value[`tarea_${i}`];
    const ocupado = tarea && tarea !== '-' && tarea.trim() !== '';
    espacios.push({
      numero: i,
      ocupado: ocupado,
      tarea: ocupado ? tarea : 'Espacio disponible',
      maquina: ocupado ? trabajadorSeleccionado.value[`maquina_${i}`] : '-',
      avance: ocupado ? trabajadorSeleccionado.value[`avance_${i}`] : 0
    });
  }
  return espacios;
});

const asignarTarea = async () => {
  if (!form.value.trabajador_id || !form.value.tarea) {
    mensaje.value = { texto: 'Por favor, completa los campos requeridos.', tipo: 'error' };
    return;
  }

  const hoy = new Date().toISOString().split('T')[0];
  const espacio = form.value.espacio;
  
  // Validacion de precaucion (opcional)
  const estadoActual = estadoEspacios.value.find(e => e.numero === parseInt(espacio));
  if (estadoActual && estadoActual.ocupado) {
    if (!confirm(`El Espacio ${espacio} ya tiene una actividad asignada. ¿Deseas sobreescribirla?`)) {
      return;
    }
  }

  const payload = {
    [`tarea_${espacio}`]: form.value.tarea,
    [`maquina_${espacio}`]: form.value.maquina,
    [`fecha_inicio_${espacio}`]: hoy,
    [`avance_${espacio}`]: 0
  };

  try {
    await api.patch(`bitacora/${form.value.trabajador_id}/`, payload);
    mensaje.value = { texto: 'Tarea asignada exitosamente.', tipo: 'success' };
    
    // Recargar datos para actualizar la vista de los espacios
    const resTrabajadores = await api.get('bitacora/');
    trabajadores.value = resTrabajadores.data;

    form.value.tarea = '';
    form.value.maquina = '-';
  } catch (error) {
    mensaje.value = { texto: 'Error al asignar la tarea.', tipo: 'error' };
  }
  
  setTimeout(() => mensaje.value.texto = '', 4000);
};
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="main-title">Asignación de Tareas</h1>
        <p class="sub-title">Selecciona a un trabajador y asígnale una nueva actividad y equipo.</p>
      </div>
    </header>

    <div v-if="mensaje.texto" :class="['alert-toast', mensaje.tipo === 'success' ? 'toast-success' : 'toast-error']">
      {{ mensaje.texto }}
    </div>

    <div class="split-layout">
      <!-- PANEL IZQUIERDO: FORMULARIO -->
      <div class="content-panel main-form-panel fade-in">
        <form @submit.prevent="asignarTarea" class="modern-form">
          
          <div class="form-cols single-col">
            <div class="input-group">
              <label>Trabajador *</label>
              <select v-model="form.trabajador_id" class="modern-select" required>
                <option value="" disabled>Selecciona un trabajador...</option>
                <option v-for="t in trabajadores" :key="t.id" :value="t.id">
                  {{ t.nombre }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-cols">
            <div class="input-group">
              <label>Espacio de Trabajo *</label>
              <select v-model="form.espacio" class="modern-select">
                <option value="1">Espacio 1</option>
                <option value="2">Espacio 2</option>
                <option value="3">Espacio 3</option>
                <option value="4">Espacio 4</option>
                <option value="5">Espacio 5</option>
              </select>
            </div>

            <div class="input-group">
              <label>Máquina Asignada</label>
              <select v-model="form.maquina" class="modern-select">
                <option value="-">- N/A -</option>
                <option v-for="m in maquinas" :key="m.id" :value="m.nombre">
                  {{ m.nombre }}
                </option>
              </select>
            </div>
          </div>

          <div class="form-cols single-col">
            <div class="input-group">
              <label>Descripción de la Tarea *</label>
              <input 
                v-model="form.tarea" 
                type="text" 
                class="modern-input"
                placeholder="Ej. Cambio de aceite y filtros..." 
                required 
              />
            </div>
          </div>

          <div class="form-action mt-auto">
            <button type="submit" class="btn-primary">Confirmar Asignación</button>
          </div>
        </form>
      </div>

      <!-- PANEL DERECHO: ESTADO DE ESPACIOS -->
      <div class="side-panel">
        <div class="panel-header">
          <h2>Estado Operativo</h2>
          <p class="sub-title" v-if="trabajadorSeleccionado">
            Espacios de <strong>{{ trabajadorSeleccionado.nombre }}</strong>
          </p>
          <p class="sub-title" v-else>
            Selecciona un trabajador para ver sus espacios.
          </p>
        </div>
        
        <div class="spaces-list" v-if="trabajadorSeleccionado">
          <div 
            v-for="espacio in estadoEspacios" 
            :key="espacio.numero" 
            :class="['space-card', espacio.ocupado ? 'space-occupied' : 'space-free']"
          >
            <div class="space-header">
              <span class="space-label">ESPACIO {{ espacio.numero }}</span>
              <span v-if="espacio.ocupado" class="status-badge occupied">OCUPADO</span>
              <span v-else class="status-badge free">LIBRE</span>
            </div>
            
            <div class="space-body">
              <span class="space-task" :class="{ 'task-muted': !espacio.ocupado }">
                {{ espacio.tarea }}
              </span>
              <div v-if="espacio.ocupado" class="space-meta">
                <span class="meta-machine">{{ espacio.maquina }}</span>
                <span class="meta-percent">{{ espacio.avance }}%</span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- ESTADO VACÍO -->
        <div class="empty-state-panel" v-else>
          <div class="empty-icon">👤</div>
          <p>La información de espacios aparecerá aquí al elegir personal.</p>
        </div>
      </div>
    </div>
  </div>
</template>

<style src="./AsignarTareaView.css" scoped></style>