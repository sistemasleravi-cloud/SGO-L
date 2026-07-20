<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import api from '../services/api';

const activeTab = ref(0);

const inventario = ref([]);
const movimientos = ref([]);
const trabajadores = ref([]);
const maquinas = ref([]);

const searchStock = ref('');
const searchHist = ref('');

const mensaje = ref({ texto: '', tipo: '' });

const prodEntSel = ref('NUEVO');
const claveEnt = ref('');
const descEnt = ref('');
const piezasEnt = ref(1);
const ordenEnt = ref('');
const obraEnt = ref('');

const prodSalSel = ref('');
const piezasSal = ref(1);
const obraDest = ref('');
const solicitanteSal = ref('');
const maquinaSal = ref('-');

const cargarDatos = async () => {
  try {
    const [resInv, resMov, resTrab, resMaq] = await Promise.all([
      api.get('inventario/'),
      api.get('movimientos/'),
      api.get('bitacora/'),
      api.get('maquinas/')
    ]);
    inventario.value = resInv.data;
    movimientos.value = resMov.data;
    trabajadores.value = resTrab.data;
    maquinas.value = resMaq.data;
  } catch (error) {
    console.error(error);
  }
};

onMounted(cargarDatos);

watch(prodEntSel, (val) => {
  if (val === 'NUEVO') {
    claveEnt.value = '';
    descEnt.value = '';
  } else {
    const prod = inventario.value.find(p => p.clave === val);
    if (prod) {
      claveEnt.value = prod.clave;
      descEnt.value = prod.descripcion;
    }
  }
});

const productoSalidaActual = computed(() => {
  return inventario.value.find(p => p.clave === prodSalSel.value) || null;
});

const inventarioFiltrado = computed(() => {
  if (!searchStock.value) return inventario.value;
  const q = searchStock.value.toLowerCase();
  return inventario.value.filter(p => 
    p.clave.toLowerCase().includes(q) ||
    p.descripcion.toLowerCase().includes(q) ||
    (p.obra && p.obra.toLowerCase().includes(q)) ||
    (p.orden && p.orden.toLowerCase().includes(q))
  );
});

const historialFiltrado = computed(() => {
  if (!searchHist.value) return movimientos.value;
  const q = searchHist.value.toLowerCase();
  return movimientos.value.filter(m => 
    m.producto.toLowerCase().includes(q) ||
    (m.producto_detalle?.descripcion && m.producto_detalle.descripcion.toLowerCase().includes(q)) ||
    (m.solicitante && m.solicitante.toLowerCase().includes(q)) ||
    (m.maquina && m.maquina.toLowerCase().includes(q)) ||
    (m.obra && m.obra.toLowerCase().includes(q))
  );
});

const registrarEntrada = async () => {
  if (!claveEnt.value || !descEnt.value) return;
  
  try {
    const claveLimpia = claveEnt.value.trim().toUpperCase();
    
    if (prodEntSel.value === 'NUEVO') {
      await api.post('inventario/', {
        clave: claveLimpia,
        descripcion: descEnt.value.trim(),
        stock: 0
      });
    }

    await api.post('movimientos/', {
      producto: claveLimpia,
      tipo: 'Entrada',
      piezas: piezasEnt.value,
      orden: ordenEnt.value.trim(),
      obra: obraEnt.value.trim()
    });

    mensaje.value = { texto: 'Entrada registrada exitosamente.', tipo: 'success' };
    
    prodEntSel.value = 'NUEVO';
    claveEnt.value = '';
    descEnt.value = '';
    piezasEnt.value = 1;
    ordenEnt.value = '';
    obraEnt.value = '';
    
    await cargarDatos();
  } catch (error) {
    mensaje.value = { texto: 'Error al registrar la entrada de material.', tipo: 'error' };
  }
  setTimeout(() => mensaje.value.texto = '', 3000);
};

const registrarSalida = async () => {
  if (!prodSalSel.value || !solicitanteSal.value) return;

  try {
    await api.post('movimientos/', {
      producto: prodSalSel.value,
      tipo: 'Salida',
      piezas: piezasSal.value,
      solicitante: solicitanteSal.value,
      maquina: maquinaSal.value,
      obra: obraDest.value.trim()
    });

    mensaje.value = { texto: 'Salida registrada exitosamente.', tipo: 'success' };
    
    prodSalSel.value = '';
    piezasSal.value = 1;
    obraDest.value = '';
    solicitanteSal.value = '';
    maquinaSal.value = '-';
    
    await cargarDatos();
  } catch (error) {
    mensaje.value = { texto: 'Error al registrar la salida de material.', tipo: 'error' };
  }
  setTimeout(() => mensaje.value.texto = '', 3000);
};

const formatearFecha = (fechaStr) => {
  if (!fechaStr) return '-';
  const fecha = new Date(fechaStr);
  return fecha.toLocaleString('es-MX', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' });
};
</script>

<template>
  <div class="dashboard-wrapper">
    <header class="dashboard-header">
      <div class="header-content">
        <h1 class="main-title">Control de Almacen</h1>
        <p class="sub-title">
          {{ activeTab === 0 ? 'Inventario Stock en Almacen' : activeTab === 1 ? 'Registrar Entrada de Material' : activeTab === 2 ? 'Registrar Salida de Material' : 'Historial de Movimientos' }}
        </p>
      </div>
    </header>

    <nav class="modern-tabs">
      <button :class="['tab-btn', { 'tab-active': activeTab === 0 }]" @click="activeTab = 0">Stock Almacen</button>
      <button :class="['tab-btn', { 'tab-active': activeTab === 1 }]" @click="activeTab = 1">Registro de Entrada</button>
      <button :class="['tab-btn', { 'tab-active': activeTab === 2 }]" @click="activeTab = 2">Registro de Salida</button>
      <button :class="['tab-btn', { 'tab-active': activeTab === 3 }]" @click="activeTab = 3">Historial</button>
    </nav>

    <div v-if="mensaje.texto" :class="['alert-toast', mensaje.tipo === 'success' ? 'toast-success' : 'toast-error']">
      {{ mensaje.texto }}
    </div>

    <main class="dashboard-content">
      
      <div v-if="activeTab === 0" class="fade-in">
        <div class="content-panel search-panel">
          <div class="input-group">
            <label>FILTRAR INVENTARIO</label>
            <input v-model="searchStock" type="text" class="modern-input" placeholder="Buscar por clave, descripcion, obra u orden..." />
          </div>
        </div>

        <div class="content-panel">
          <div class="table-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Clave (ID)</th>
                  <th>Descripción</th>
                  <th>Stock Disponible</th>
                  <th>Número de Orden</th>
                  <th>Obra</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="item in inventarioFiltrado" :key="item.clave">
                  <td class="cell-id">{{ item.clave }}</td>
                  <td class="cell-name">{{ item.descripcion }}</td>
                  <td>
                    <span :class="['stock-pill', item.stock === 0 ? 'pill-zero' : 'pill-ok']">
                      {{ item.stock }} pz
                    </span>
                  </td>
                  <td>{{ item.orden || '-' }}</td>
                  <td>{{ item.obra || '-' }}</td>
                </tr>
                <tr v-if="inventarioFiltrado.length === 0">
                  <td colspan="5" class="empty-msg">El almacén está vacío o ningún producto coincide con el filtro.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div v-if="activeTab === 1" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Ingreso de Material</h2>
          </div>
          <div class="input-row" style="margin-bottom: 2rem;">
            <div class="input-group">
              <label>Seleccionar producto existente o registrar uno nuevo</label>
              <select v-model="prodEntSel" class="modern-select">
                <option value="NUEVO">-- NUEVO PRODUCTO --</option>
                <option v-for="p in inventario" :key="p.clave" :value="p.clave">
                  {{ p.clave }} - {{ p.descripcion }}
                </option>
              </select>
            </div>
          </div>

          <form @submit.prevent="registrarEntrada" class="modern-form">
            <div class="form-cols">
              <div class="input-group">
                <label>Clave del Producto (ID)</label>
                <input v-model="claveEnt" type="text" class="modern-input" placeholder="" :disabled="prodEntSel !== 'NUEVO'" required />
              </div>
              <div class="input-group" style="grid-column: span 2;">
                <label>Descripción del Producto</label>
                <input v-model="descEnt" type="text" class="modern-input" placeholder="" :disabled="prodEntSel !== 'NUEVO'" required />
              </div>
            </div>
            
            <div class="form-cols">
              <div class="input-group">
                <label>Piezas que entran</label>
                <input v-model="piezasEnt" type="number" min="1" class="modern-input" required />
              </div>
              <div class="input-group">
                <label>Número de Orden</label>
                <input v-model="ordenEnt" type="text" class="modern-input" placeholder="" />
              </div>
              <div class="input-group">
                <label>Obra</label>
                <input v-model="obraEnt" type="text" class="modern-input" placeholder="" />
              </div>
            </div>

            <div class="form-action" style="margin-top: 1rem;">
              <button type="submit" class="btn-primary">Registrar Entrada</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="activeTab === 2" class="fade-in">
        <div class="content-panel">
          <div class="panel-header">
            <h2>Egreso de Material</h2>
          </div>
          <div class="input-row" style="margin-bottom: 1.5rem;">
            <div class="input-group">
              <label>Seleccionar Producto (ID y Descripción)</label>
              <select v-model="prodSalSel" class="modern-select">
                <option value="" disabled>-- Seleccione un artículo con stock disponible --</option>
                <option v-for="p in inventario.filter(i => i.stock > 0)" :key="p.clave" :value="p.clave">
                  {{ p.clave }} - {{ p.descripcion }} (Stock: {{ p.stock }})
                </option>
              </select>
            </div>
          </div>

          <form v-if="prodSalSel" @submit.prevent="registrarSalida" class="modern-form">
            <div class="stock-banner">
              Stock disponible actual: <span class="stock-highlight">{{ productoSalidaActual?.stock }} pz</span>
            </div>

            <div class="form-cols">
              <div class="input-group">
                <label>Piezas que salen</label>
                <input v-model="piezasSal" type="number" min="1" :max="productoSalidaActual?.stock || 1" class="modern-input" required />
              </div>
              <div class="input-group">
                <label>Obra Destino</label>
                <input v-model="obraDest" type="text" class="modern-input" placeholder="Ej. Mina LIX" required />
              </div>
            </div>

            <div class="form-cols">
              <div class="input-group">
                <label>Nombre del Solicitante</label>
                <select v-model="solicitanteSal" class="modern-select" required>
                  <option value="" disabled>-- Seleccione un trabajador --</option>
                  <option v-for="t in trabajadores" :key="t.id" :value="t.nombre">{{ t.nombre }}</option>
                </select>
              </div>
              <div class="input-group">
                <label>Maquinaria Asociada</label>
                <select v-model="maquinaSal" class="modern-select">
                  <option value="-">- Sin Maquinaria Asociada -</option>
                  <option v-for="m in maquinas" :key="m.id" :value="m.nombre">{{ m.nombre }}</option>
                </select>
              </div>
            </div>

            <div class="form-action" style="margin-top: 1rem;">
              <button type="submit" class="btn-primary" style="background-color: #0F172A;">Registrar Salida</button>
            </div>
          </form>
        </div>
      </div>

      <div v-if="activeTab === 3" class="fade-in">
        <div class="content-panel search-panel">
          <div class="input-group">
            <label>BUSCAR EN HISTORIAL</label>
            <input v-model="searchHist" type="text" class="modern-input" placeholder="Buscar por clave, descripción, solicitante, máquina, obra..." />
          </div>
        </div>

        <div class="content-panel">
          <div class="table-wrapper">
            <table class="modern-table">
              <thead>
                <tr>
                  <th>Fecha y Hora</th>
                  <th>Tipo</th>
                  <th>Clave</th>
                  <th>Descripción</th>
                  <th>Piezas</th>
                  <th>Solicitante</th>
                  <th>Máquina</th>
                  <th>Obra</th>
                  <th>Orden</th>
                </tr>
              </thead>
              <tbody>
                <tr v-for="m in historialFiltrado" :key="m.id">
                  <td class="cell-date">{{ formatearFecha(m.fecha) }}</td>
                  <td>
                    <span :class="['type-pill', m.tipo === 'Entrada' ? 'pill-ent' : 'pill-sal']">
                      {{ m.tipo }}
                    </span>
                  </td>
                  <td class="cell-id">{{ m.producto }}</td>
                  <td>{{ m.producto_detalle?.descripcion || 'Artículo Removido' }}</td>
                  <td class="cell-highlight">{{ m.piezas }} pz</td>
                  <td>{{ m.solicitante || '-' }}</td>
                  <td class="cell-machine">{{ m.maquina || '-' }}</td>
                  <td>{{ m.obra || '-' }}</td>
                  <td>{{ m.orden || '-' }}</td>
                </tr>
                <tr v-if="historialFiltrado.length === 0">
                  <td colspan="9" class="empty-msg">No hay registro de movimientos bajo los parámetros de búsqueda.</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </div>

    </main>
  </div>
</template>

<style src="./AlmacenView.css" scoped></style>