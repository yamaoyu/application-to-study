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
    }
});