import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { configDefaults } from 'vitest/config'
import { fileURLToPath, URL } from 'node:url'

import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

export default defineConfig({
  plugins: [
    vue(),
    // Auto-import plugins removed for stability (caused CPU hang)
  ],
  // Vitest 配置：仅跑组件/单元测试，排除 e2e（Playwright）
  test: {
    globals: true,
    exclude: [...configDefaults.exclude, 'tests/e2e/**'],
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url)),
    },
  },
  server: {
    port: 5174,
    proxy: {
      '/api': {
        target: 'http://backend:8001',
        changeOrigin: true,
      }
    }
  }
})
