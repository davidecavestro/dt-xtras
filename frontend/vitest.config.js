import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  test: {
    environment: 'jsdom',
    include: ['src/utils/__tests__/**/*.test.js'],
    exclude: ['node_modules', 'dist'],
    globals: true,
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      all: true,
      include: ['src/**/*.{js,vue}'],
      exclude: [
        'node_modules/',
        'dist/',
        '**/*.test.js',
        '**/*.config.js',
        'src/main.js'
      ]
    }
  }
})
