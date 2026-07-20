<script setup>
import { ref, onMounted } from 'vue';
import api from '../services/api';

const nombreTrabajador = ref('');
const nombreMaquina = ref('');
const mensajeAlta = ref({ texto: '', tipo: '' });

const trabajadores = ref([]);
const maquinas = ref([]);
const trabajadorAEliminar = ref('');
const maquinaAEliminar = ref('');
const mensajeBaja = ref({ texto: '', tipo: '' });

const cargarCatalogos = async () => {
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

onMounted(cargarCatalogos);

const registrarTrabajador = async () => {
  if (!nombreTrabajador.value) return;
  try {
    const hoy = new Date().toISOString().split('T')[0];
    await api.post('bitacora/', { nombre: nombreTrabajador.value, fecha: hoy });
    mensajeAlta.value = { texto: 'Trabajador registrado exitosamente', tipo: 'success' };
    nombreTrabajador.value = '';
    await cargarCatalogos(); 
  } catch (error) {
    mensajeAlta.value = { texto: 'Error al registrar trabajador', tipo: 'error' };
  }
  setTimeout(() => mensajeAlta.value.texto = '', 3000);
};

const registrarMaquina = async () => {
  if (!nombreMaquina.value) return;
  try {
    await api.post('maquinas/', { nombre: nombreMaquina.value.trim().toUpperCase() });
    mensajeAlta.value = { texto: 'Máquina registrada exitosamente', tipo: 'success' };
    nombreMaquina.value = '';
    await cargarCatalogos(); 
  } catch (error) {
    mensajeAlta.value = { texto: 'Error: La máquina ya existe o falló la conexión', tipo: 'error' };
  }
  setTimeout(() => mensajeAlta.value.texto = '', 3000);
};

const eliminarTrabajador = async () => {
  if (!trabajadorAEliminar.value) return;
  if (!confirm('¿Estás seguro de eliminar a este trabajador? Esta acción es irreversible.')) return;
  
  try {
    await api.delete(`bitacora/${trabajadorAEliminar.value}/`);
    mensajeBaja.value = { texto: 'Trabajador eliminado del sistema.', tipo: 'success' };
    trabajadorAEliminar.value = '';
    await cargarCatalogos();
  } catch (error) {
    mensajeBaja.value = { texto: 'Error al eliminar el trabajador.', tipo: 'error' };
  }
  setTimeout(() => mensajeBaja.value.texto = '', 3000);
};

const eliminarMaquina = async () => {
  if (!maquinaAEliminar.value) return;
  if (!confirm('¿Estás seguro de eliminar esta máquina del catálogo?')) return;
  
  try {
    await api.delete(`maquinas/${maquinaAEliminar.value}/`);
    mensajeBaja.value = { texto: 'Máquina eliminada del sistema.', tipo: 'success' };
    maquinaAEliminar.value = '';
    await cargarCatalogos();
  } catch (error) {
    mensajeBaja.value = { texto: 'Error al eliminar la máquina.', tipo: 'error' };
  }
  setTimeout(() => mensajeBaja.value.texto = '', 3000);
};
</script>

<template>
  <div class="dashboard-wrapper">
    
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="main-title">Registros Administrativos</h1>
        <p class="sub-title">Da de alta a nuevos trabajadores en la bitácora o registra nuevas máquinas en el catálogo.</p>
      </div>
    </header>

    <div v-if="mensajeAlta.texto" :class="['alert-toast', mensajeAlta.tipo === 'success' ? 'toast-success' : 'toast-error']">
      {{ mensajeAlta.texto }}
    </div>

    <div class="split-grid">
      <div class="content-panel panel-flex">
        <div class="panel-header">
          <h2>Alta de Trabajador</h2>
        </div>
        <form @submit.prevent="registrarTrabajador" class="modern-form flex-grow">
          <div class="input-group">
            <label>Nombre Completo del Trabajador</label>
            <input v-model="nombreTrabajador" type="text" class="modern-input" placeholder="Ej. Armando Narvaez" required />
          </div>
          <div class="form-action mt-auto">
            <button type="submit" class="btn-primary">Registrar Trabajador</button>
          </div>
        </form>
      </div>

      <div class="content-panel panel-flex">
        <div class="panel-header">
          <h2>Alta de Máquina</h2>
        </div>
        <form @submit.prevent="registrarMaquina" class="modern-form flex-grow">
          <div class="input-group">
            <label>Identificador de la Máquina</label>
            <input v-model="nombreMaquina" type="text" class="modern-input" placeholder="Ej. U-42" required />
          </div>
          <div class="form-action mt-auto">
            <button type="submit" class="btn-primary">Registrar Máquina</button>
          </div>
        </form>
      </div>
    </div>

    <header class="dashboard-header" style="margin-top: 3.5rem;">
      <div class="header-content">
        <h1 class="main-title">Bajas del Sistema</h1>
        <p class="sub-title">Elimina permanentemente trabajadores o máquinas de la base de datos de Leravi.</p>
      </div>
    </header>

    <div v-if="mensajeBaja.texto" :class="['alert-toast', mensajeBaja.tipo === 'success' ? 'toast-success' : 'toast-error']">
      {{ mensajeBaja.texto }}
    </div>

    <div class="split-grid">
      <div class="content-panel danger-panel panel-flex">
        <div class="panel-header">
          <h2 class="danger-heading">Dar de Baja Trabajador</h2>
        </div>
        <form @submit.prevent="eliminarTrabajador" class="modern-form flex-grow">
          <div class="input-group">
            <label>Seleccionar Trabajador</label>
            <select v-model="trabajadorAEliminar" class="modern-select" required>
              <option value="" disabled>-- Elige a quién eliminar --</option>
              <option v-for="t in trabajadores" :key="t.id" :value="t.id">{{ t.nombre }}</option>
            </select>
          </div>
          <div class="form-action mt-auto">
            <button type="submit" class="btn-danger">Eliminar Trabajador</button>
          </div>
        </form>
      </div>

      <div class="content-panel danger-panel panel-flex">
        <div class="panel-header">
          <h2 class="danger-heading">Dar de Baja Máquina</h2>
        </div>
        <form @submit.prevent="eliminarMaquina" class="modern-form flex-grow">
          <div class="input-group">
            <label>Seleccionar Máquina</label>
            <select v-model="maquinaAEliminar" class="modern-select" required>
              <option value="" disabled>-- Elige qué máquina eliminar --</option>
              <option v-for="m in maquinas" :key="m.id" :value="m.id">{{ m.nombre }}</option>
            </select>
          </div>
          <div class="form-action mt-auto">
            <button type="submit" class="btn-danger">Eliminar Máquina</button>
          </div>
        </form>
      </div>
    </div>

  </div>
</template>

<style src="./RegistrosView.css" scoped></style>