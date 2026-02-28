import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  // base: "/compressPDFApp/",
  base: "./",
  build: {
    outDir: 'dist',
    assetsDir: 'assets',
    sourcemap: false,
    rollupOptions: {
      output: {
        manualChunks: undefined,
      },
    },
  },
  server: {
    port: 3000,
    proxy: {
      '/compress': {
        target: 'http://localhost:8084',
        changeOrigin: true,
      },
      '/removeFiles': {
        target: 'http://localhost:8084',
        changeOrigin: true,
      },
      '/health': {
        target: 'http://localhost:8084',
        changeOrigin: true,
      }
    }
  }
})