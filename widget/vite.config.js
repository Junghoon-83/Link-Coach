import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, ''),
      },
      '/dev/token': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
  build: {
    // 청크 분할 최적화
    rollupOptions: {
      output: {
        manualChunks: {
          // React 관련 라이브러리를 별도 청크로 분리
          'react-vendor': ['react', 'react-dom'],
        },
      },
    },
    // 청크 크기 경고 임계값 (500KB)
    chunkSizeWarningLimit: 500,
    // CSS 코드 스플리팅
    cssCodeSplit: true,
    // 소스맵 생성 (프로덕션에서는 false로 설정 가능)
    sourcemap: false,
  },
  // 최적화 설정
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
