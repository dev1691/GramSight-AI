import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// Build output must be inside the project workdir so Docker builder can copy it.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist'
  }
})
