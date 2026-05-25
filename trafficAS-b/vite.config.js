import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath, URL } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  resolve: { alias: { '@': fileURLToPath(new URL('./src', import.meta.url)) } },
  server: {
    port: 5174,
    strictPort: true,
    proxy: {
      '/api': 'http://127.0.0.1:8080',
      '/static/detections': 'http://127.0.0.1:8000',
    },
  },
  preview: {
    port: 5174,
    strictPort: true,
  },
  test: {
    environment: 'happy-dom',
    globals: true,
    include: ['tests/**/*.test.js'],
  },
})
