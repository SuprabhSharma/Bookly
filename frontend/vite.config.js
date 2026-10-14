import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

export default defineConfig({
  plugins: [react()],
  server: {
    port: 5173,
    host: true,
    proxy: {
      '/api': {
        target: process.env.VITE_PROXY_TARGET || 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: { rollupOptions: { output: { manualChunks: { react: ['react', 'react-dom'], router: ['react-router-dom'], query: ['@tanstack/react-query'] } } } },
})
