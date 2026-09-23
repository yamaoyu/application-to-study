import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算

export async function mockGetMonthlySalary(page: Page) {
    await page.route(`${BACKEND_URL}/incomes/${year}/${month}`, async (route) => {
        if (route.request().method() !== 'GET') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "year": year,
                "month": month,
                "salary": 30.0
            },
        });
    });
}

export async function mockRegisterSalary(page: Page) {
    await page.route(`${BACKEND_URL}/incomes/${year}/${month}`, async (route) => {
        if (route.request().method() !== 'POST') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 201,
            json: {
                "year": year,
                "month": month,
                "salary": 30.0
            },
        });
    });
}
