import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';


export async function mockRegisterUser(page: Page) {
    await page.route(`${BACKEND_URL}/users`, async (route) => {
        if (route.request().method() !== 'POST') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "username": "test",
                "password": "*********",
                "email": null,
                "role": "general"
            },
        });
    });
}

export async function mockChangePassword(page: Page) {
    await page.route(`${BACKEND_URL}/password`, async (route) => {
        if (route.request().method() !== 'PATCH') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {},
        });
    });
}
