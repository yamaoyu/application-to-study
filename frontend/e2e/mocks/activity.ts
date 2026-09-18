import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算
const day = today.getDate();
const formattedDate = `${year}-${month}-${day}`;

export async function mockActivityByDay(page: Page) {
    await page.route(`${BACKEND_URL}/${year}/${month}/${day}`, async (route) => {
        if (route.request().method() !== 'GET') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "activity_id": 1,
                "date": formattedDate,
                "target_time": 5.0,
                "actual_time": 0.0,
                "status": "pending",
                "bonus": 0.0,
                "penalty": 0.58
            },
        });
    });
}
