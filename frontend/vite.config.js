import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    host: '0.0.0.0', // Permite acceso desde fuera del contenedor
    port: 3000,
    watch: {
      usePolling: true, // Necesario para hot-reload en Docker
    },
    proxy: {
      '/api': {
        target: process.env.VITE_API_BASE_URL?.replace('/api/v1', '') || 'http://api:8000',
        changeOrigin: true,
        secure: false,
      },
    },
  },
})

