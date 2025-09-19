import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

export default defineConfig({
    plugins: [vue()],
    resolve: {
        alias: {
            '@': '/src',
        },
    },
    test:{
        environment: 'jsdom',
        setupFiles: ['./test/vitest.setup.js'],
    },
    server: {
        port: process.env.FRONTEND_PORT,
        host: "0.0.0.0",
        allowedHosts: [process.env.FRONTEND_DOMAIN],
        hmr: {
            port: 24678,                             // HMR用WebSocket公開ポート
            host: process.env.FRONTEND_DOMAIN,  // ブラウザから見えるホスト名
            clientPort: 443,
            protocol: 'wss',
        }
    }
});