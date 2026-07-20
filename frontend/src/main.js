import { createApp } from 'vue'
import App from './App.vue'
import router from './router' // Importamos las rutas

const app = createApp(App)

app.use(router) // Conectamos el router a la aplicación
app.mount('#app')