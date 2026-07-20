import { createRouter, createWebHistory } from 'vue-router';
import DashboardView from '../views/DashboardView.vue';
import RegistrosView from '../views/RegistrosView.vue';
import AsignarTareaView from '../views/AsignarTareaView.vue';
import EditarAvancesView from '../views/EditarAvancesView.vue';
import BitacoraView from '../views/BitacoraView.vue';
import AlmacenView from '../views/AlmacenView.vue';
import LoginView from '../views/LoginView.vue'; // <-- 1. Importamos la vista de Login

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: LoginView // <-- Ruta pública para iniciar sesión
    },
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView,
      meta: { requiresAuth: true } // <-- Candado activado
    },
    { 
      path: '/almacen',
      name: 'almacen',
      component: AlmacenView,
      meta: { requiresAuth: true }
    },
    {
      path: '/registros',
      name: 'registros',
      component: RegistrosView,
      meta: { requiresAuth: true }
    },
    {
      path: '/asignar-tarea',
      name: 'asignar-tarea',
      component: AsignarTareaView,
      meta: { requiresAuth: true }
    },
    {
      path: '/editar-avances',
      name: 'editar-avances',
      component: EditarAvancesView,
      meta: { requiresAuth: true }
    },
    {
      path: '/bitacora',
      name: 'bitacora',
      component: BitacoraView,
      meta: { requiresAuth: true }
    }
  ]
});

// 2. Guardián de Navegación (El Portero)
router.beforeEach((to, from, next) => {
  // Buscamos el token JWT en la memoria del navegador
  const token = localStorage.getItem('access_token');
  
  if (to.meta.requiresAuth && !token) {
    // Si quiere ir a una ruta protegida y NO tiene token -> Lo mandamos a loguearse
    next({ name: 'login' });
  } else if (to.name === 'login' && token) {
    // Si quiere ir al login pero YA está logueado -> Lo mandamos al dashboard
    next({ name: 'dashboard' });
  } else {
    // En cualquier otro caso, lo dejamos pasar
    next();
  }
});

export default router;