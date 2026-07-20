import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: true, 
    watch: {
      usePolling: true, // 🔥 Esta es la magia para que Docker escuche a Windows
      interval: 100     // Revisa cambios cada 100 milisegundos
    }
  }
})