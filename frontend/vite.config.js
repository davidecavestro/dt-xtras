import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      'vue': 'vue/dist/vue.esm-bundler.js'
    }
  },
  build: {
    sourcemap: true
  },
  server: {
    host: '0.0.0.0',
    port: 5173,
    proxy: {
      '/api/v1': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      },
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
        secure: false
      }
    }
  },
  define: {
    // Make environment variables available to the app
    __DT_API_URL__: JSON.stringify(process.env.DT_API_URL || 'http://dtrack-apiserver:8080'),
    __DT_FRONTEND_URL__: JSON.stringify(process.env.DT_FRONTEND_URL || 'http://dtrack-frontend:8080'),
    __BACKEND_API_URL__: JSON.stringify(process.env.BACKEND_API_URL || 'http://localhost:8000')
  }
})
