import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

const backendTarget = process.env.VITE_BACKEND_TARGET || 'http://localhost:8000'
const wsTarget = backendTarget.replace(/^http/, 'ws')

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    proxy: {
      '/api': backendTarget,
      '/uploads': backendTarget,
      '/ws': { target: wsTarget, ws: true },
    },
  },
})
