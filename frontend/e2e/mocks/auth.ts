import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

export async function mockAuth(page: Page) {
    const encode = (value: object) =>
        Buffer.from(JSON.stringify(value)).toString('base64url');

    // フロントエンドでデコードするためのダミー JWT
    const accessToken = [
        encode({ alg: 'HS256', typ: 'JWT' }),
        encode({ exp: Math.floor(Date.now() / 1000) + 3600 }),
        'mock-signature',
    ].join('.');

    // ページ移動時に再度ログインにならないように各機能のテストではログインAPIではなく、トークンAPIを使用する
    await page.route(`${BACKEND_URL}/token`, async route => {
        await route.fulfill({
            status: 200,
            json: {
                access_token: accessToken,
                token_type: 'bearer',
            },
        });
    });
}
