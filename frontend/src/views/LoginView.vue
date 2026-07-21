<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import api from '../services/api';

const username = ref('');
const password = ref('');
const errorMensaje = ref('');
const cargando = ref(false);
const mostrarPassword = ref(false);
const router = useRouter();

const iniciarSesion = async () => {
  if (!username.value || !password.value) return;
  cargando.value = true;
  errorMensaje.value = '';

  try {
    const response = await api.post('login/', {
      username: username.value,
      password: password.value
    });

    localStorage.setItem('access_token', response.data.access);
    localStorage.setItem('refresh_token', response.data.refresh);
    localStorage.setItem('user', username.value);
    
    if (response.data.empresa_nombre) {
      localStorage.setItem('empresa_nombre', response.data.empresa_nombre);
    }

    window.location.href = '/';
  } catch (error) {
    errorMensaje.value = 'Credenciales invalidas. Verifica tu usuario y contraseña.';
    cargando.value = false;
  }
};

const toggleMostrarPassword = () => {
  mostrarPassword.value = !mostrarPassword.value;
};
</script>

<template>
  <div class="login-wrapper">
    <div class="login-box">
      <div class="brand-section">
        <div class="logo-glow">
          <img src="/SIFClogo.jpg" alt="Logo Leravi" class="login-logo" />
        </div>
        <h1 class="brand-title">LERAVI</h1>
        <p class="brand-subtitle">CONTROL ADMINISTRATIVO</p>
        <p class="brand-subtitle">SGO-L</p>
      </div>

      <form @submit.prevent="iniciarSesion" class="login-form">
        <div v-if="errorMensaje" class="error-alert">
          {{ errorMensaje }}
        </div>

        <div class="input-group">
          <label>USUARIO</label>
          <input
            v-model="username"
            type="text"
            required
            placeholder="Ingresa tu usuario"
            :disabled="cargando"
          />
        </div>

        <div class="input-group">
          <label>CONTRASEÑA</label>
          <div class="password-field">
            <input
              v-model="password"
              :type="mostrarPassword ? 'text' : 'password'"
              required
              placeholder="••••••••"
              :disabled="cargando"
            />
            <button
              type="button"
              class="toggle-password"
              @click="toggleMostrarPassword"
              :disabled="cargando"
              tabindex="-1"
            >
              <svg v-if="!mostrarPassword" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                <circle cx="12" cy="12" r="3" />
              </svg>
              <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17.94 17.94A10.94 10.94 0 0 1 12 20c-7 0-11-8-11-8a18.6 18.6 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24" />
                <line x1="1" y1="1" x2="23" y2="23" />
              </svg>
            </button>
          </div>
        </div>

        <div class="action-section">
          <button type="submit" class="btn-login" :disabled="cargando">
            <span v-if="!cargando">INICIAR SESION</span>
            <span v-else>VERIFICANDO CREDENCIALES...</span>
          </button>

          <div v-if="cargando" class="loading-overlay">
            <div class="progress-bar">
              <div class="progress-fill"></div>
            </div>
            <span class="loading-text">Preparando el entorno de trabajo, por favor espera...</span>
          </div>
        </div>
      </form>

      <p class="footer-text">Sistema de Gestion Operativa v3.0</p>
    </div>
  </div>
</template>

<style src="./LoginView.css" scoped></style>
