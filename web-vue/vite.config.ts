import { fileURLToPath, URL } from 'node:url'

import vue from '@vitejs/plugin-vue'
import { visualizer } from 'rollup-plugin-visualizer'
import { defineConfig, loadEnv } from 'vite'

export default defineConfig(({ mode }) => {
  const env = loadEnv(mode, process.cwd(), '')
  const base = env.VITE_BASE_PATH || '/'

  return {
    base,
    plugins: [
      vue(),
      visualizer({
        filename: 'dist/bundle-stats.html',
        gzipSize: true,
        brotliSize: true,
        template: 'treemap',
        open: false,
      }),
    ],
    resolve: {
      alias: {
        '@': fileURLToPath(new URL('./src', import.meta.url)),
      },
    },
    build: {
      manifest: true,
      sourcemap: false,
      assetsInlineLimit: 2048,
      rollupOptions: {
        output: {
          manualChunks: {
            'vue-runtime': ['vue', 'vue-router', 'pinia'],
          },
        },
      },
    },
    server: {
      proxy: {
        '/api': 'http://127.0.0.1:8010',
      },
    },
  }
})
