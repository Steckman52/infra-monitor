import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      // Forward API calls to the local FastAPI server (see quickstart.md).
      '/api': 'http://localhost:8000',
    },
  },
})
