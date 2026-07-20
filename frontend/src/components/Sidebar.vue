<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter, useRoute } from 'vue-router';

const router = useRouter();
const route = useRoute();

const nombreUsuario = ref('Admin');
const nombreSede = ref('Cananea');

onMounted(() => {
  const userGuardado = localStorage.getItem('user');
  if (userGuardado) {
    nombreUsuario.value = userGuardado.charAt(0).toUpperCase() + userGuardado.slice(1);
  }

  const sedeGuardada = localStorage.getItem('empresa_nombre');
  if (sedeGuardada) {
    nombreSede.value = sedeGuardada;
  }
});

const letraAvatar = computed(() => nombreUsuario.value.charAt(0).toUpperCase());

const navItems = [
  {
    name: 'Dashboard',
    path: '/',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zm10 0a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" /></svg>'
  },
  {
    name: 'Almacen General',
    path: '/almacen',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" /></svg>'
  },
  {
    name: 'Registros',
    path: '/registros',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-3 7h3m-3 4h3m-6-4h.01M9 16h.01" /></svg>'
  },
  {
    name: 'Asignar Tarea',
    path: '/asignar-tarea',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
  },
  {
    name: 'Editar Avances',
    path: '/editar-avances',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" /></svg>'
  },
  {
    name: 'Bitacora',
    path: '/bitacora',
    icon: '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>'
  }
];

const sharepointUrl = 'https://grupoleravi.sharepoint.com/sites/AdministracionLeraviCananea/SitePages/EventPlanHome.aspx';
const sharepointIcon = '<svg width="22" height="22" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M3 15a4 4 0 004 4h9a5 5 0 001.7-9.71 5.5 5.5 0 00-10.6-1.68A4.5 4.5 0 003 15z" /></svg>';

const fechaActual = computed(() => {
  const opciones = { day: '2-digit', month: 'short', year: 'numeric' };
  return new Date().toLocaleDateString('es-MX', opciones).replace('.', '');
});

const cerrarSesion = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  localStorage.removeItem('user');
  localStorage.removeItem('empresa_nombre');
  router.push('/login');
};
</script>

<template>
  <aside class="sidebar">
    <div class="brand-section">
      <h1 class="brand-title">LERAVI</h1>
      <div class="logo-container">
        <img src="/SIFClogo.jpg" alt="Logo Empresa" class="brand-logo" />
      </div>
      <p class="brand-subtitle">CONTROL ADMINISTRATIVO</p>
      <p class="brand-subtitle">SGO-L</p>
      <p class="brand-subtitle">Sede: {{ nombreSede }}</p>
    </div>

    <div class="divider-container">
      <hr class="divider" />
    </div>

    <div class="nav-section">
      <p class="nav-caption">Navegacion</p>
      <nav class="nav-list">
        <router-link
          v-for="item in navItems"
          :key="item.path"
          :to="item.path"
          class="nav-link"
          :class="{ active: route.path === item.path }"
        >
          <span class="icon-wrapper" v-html="item.icon"></span>
          {{ item.name }}
        </router-link>

        <a
          :href="sharepointUrl"
          target="_blank"
          rel="noopener noreferrer"
          class="nav-link"
        >
          <span class="icon-wrapper" v-html="sharepointIcon"></span>
          SharePoint
        </a>
      </nav>
    </div>

    <div class="footer-section">
      <div class="user-card">
        <div class="user-avatar">
          <span>{{ letraAvatar }}</span>
        </div>
        <div class="user-info">
          <br>
          <br>
          <p class="user-name">{{ nombreUsuario }}</p>
          <p class="user-date">{{ fechaActual }}</p>
          <p class="user-version">Version: 3.0</p>
        </div>
      </div>
      <button class="logout-button" @click="cerrarSesion">
        Cerrar Sesion
      </button>
    </div>
  </aside>
</template>

<style src="./Sidebar.css" scoped></style>