import { fileURLToPath, URL } from 'node:url'
import path from 'path'

import vue from '@vitejs/plugin-vue'
import { defineConfig } from 'vite'

const zxcvbnRe = /@zxcvbn-ts\/language-(\w+-?\w+?)\//

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
      '~@/scss': fileURLToPath(new URL('./src/scss', import.meta.url)),
      '~@/assets': fileURLToPath(new URL('./src/assets', import.meta.url)),
    },
  },
  server: {
    host: true,
    port: 3000,
  },
  build: {
    outDir: path.resolve(__dirname, '../fittrackee/dist'),
    emptyOutDir: true,
    assetsDir: 'static',
    rollupOptions: {
      output: {
        assetFileNames({ name }) {
          if (name?.includes('pt-sans-v9-latin'))
            return 'static/fonts/[name]-[hash][extname]'
          if (name?.includes('.svg')) return 'static/img/[name]-[hash][extname]'
          if (name?.includes('.css')) return 'static/css/[name]-[hash][extname]'
          return 'static/[name]-[hash][extname]'
        },
        manualChunks: (id) => {
          if (id.includes('@zxcvbn-ts/language-')) {
            const matches = id.match(zxcvbnRe)
            if (matches && matches.length === 2) {
              return `password.${matches[1]}`
            }
          }
          if (id.includes('node_modules')) {
            if (
              id.includes('/chart.js') ||
              id.includes('/chartjs-plugin-datalabels')
            )
              return 'charts'
            if (id.includes('/leaflet')) return 'maps'
          }
        },
      },
    },
  },
})
