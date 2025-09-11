import { defineConfig, loadEnv  } from 'vite';
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
        port: import.meta.env.FRONTEND_PORT,
        host: true,
        allowedHosts: [import.meta.env.FRONTEND_DOMAIN]
    }
});