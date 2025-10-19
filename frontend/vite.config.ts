/// <reference types="vitest" />
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'
import { resolve } from 'path'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  // Map TS path aliases (tsconfig.paths) to Vite resolver
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
      '@components': resolve(__dirname, 'src/components')
    }
  },
  build: {
    outDir: '../dist',
    emptyOutDir: true
  },
  test:{
    globals: true,
    environment: 'jsdom',
    setupFiles: ['./src/setupTests.ts']
  }
})
