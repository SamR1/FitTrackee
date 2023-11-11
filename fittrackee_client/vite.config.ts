import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '~@/scss': fileURLToPath(new URL('./src/scss', import.meta.url)),
      '~@/assets': fileURLToPath(new URL('./src/assets', import.meta.url))
    }
  },
  server: {
    port: 3000
  },
  build: {
    outDir: path.resolve(__dirname, '../fittrackee/dist'),
    emptyOutDir: true,
    assetsDir: 'static'
  }
})
