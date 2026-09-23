import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算
const day = today.getDate();
const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

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

export async function mockRegisterTarget(page: Page) {
    await page.route(`${BACKEND_URL}/activities/bulk-create-targets`, async (route) => {
        if (route.request().method() !== 'POST') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "success_count": 1,
                "error_count": 0,
                "results": [
                    {
                        "date": formattedDate,
                        "result": "success",
                        "target_time": 5.0,
                        "reason": null
                    }
                ]
            },
        });
    });
}

export async function mockNotFinishedActivities(page: Page) {
    await page.route(`${BACKEND_URL}/activities?status=pending`, async (route) => {
        if (route.request().method() !== 'GET') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "activities": [
                    {
                        "activity_id": 1,
                        "date": formattedDate,
                        "target_time": 5.0,
                        "actual_time": 5.0,
                        "status": "success",
                        "bonus": 0.0,
                        "penalty": 0.0
                    }
                ]
            }
        });
    });
}

export async function mockRegisterActual(page: Page) {
    await page.route(`${BACKEND_URL}/activities/bulk-update-actuals`, async (route) => {
        if (route.request().method() !== 'PATCH') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "success_count": 1,
                "error_count": 0,
                "results": [
                    {
                        "date": formattedDate,
                        "result": "success",
                        "actual_time": 5.0,
                        "reason": null
                    }
                ]
            },
        });
    });
}

export async function mockFinishActivity(page: Page) {
    await page.route(`${BACKEND_URL}/activities/bulk-finish`, async (route) => {
        if (route.request().method() !== 'PATCH') {
            await route.continue();
            return;
        }

        await route.fulfill({
            status: 200,
            json: {
                "success_count": 1,
                "error_count": 0,
                "pay_adjustment": 0.5,
                "total_bonus": 0.5,
                "total_penalty": 0,
                "results": [
                    {
                        "date": formattedDate,
                        "result": "success",
                        "status": "success",
                        "bonus": 0.58,
                        "penalty": 0.0,
                        "reason": null
                    }
                ]
            },
        });
    });
}
