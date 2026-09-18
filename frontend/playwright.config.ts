import { defineConfig } from '@playwright/test';

const port = process.env.FRONTEND_PORT || '8080';

export default defineConfig({
    testDir: './e2e',
    use: {
        baseURL: `http://localhost:${port}`, // おそらく開発環境でしか使わないのでローカルホスト固定
        ignoreHTTPSErrors: true,
    },
});
