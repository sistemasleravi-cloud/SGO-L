<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue'; // Verifica que esta ruta sea la tuya

const route = useRoute();

// Computada que verifica si estamos en la pantalla de login
const mostrarSidebar = computed(() => {
  return route.path !== '/login';
});
</script>

<template>
  <!-- Le agregamos una clase dinámica al contenedor si no hay sidebar -->
  <div class="app-container" :class="{ 'pantalla-completa': !mostrarSidebar }">
    
    <!-- El v-if oculta el sidebar en el login -->
    <Sidebar v-if="mostrarSidebar" />
    
    <main class="main-content">
      <router-view />
    </main>
    
  </div>
</template>

<style src="./App.css" scoped></style>