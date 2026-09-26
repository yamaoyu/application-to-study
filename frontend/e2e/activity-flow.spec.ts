import { test, expect } from '@playwright/test';
import { mockAuth } from './mocks/auth';
import { mockRegisterSalary, mockGetMonthlySalary } from './mocks/salary';
import {
    mockRegisterTarget,
    mockRegisterActual,
    mockFinishActivity,
    mockNotFinishedActivities
} from './mocks/activity';

test.use({
    ignoreHTTPSErrors: true
});

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算
const day = today.getDate();
const formattedMonthWithZero = `${year}-${month.toString().padStart(2, '0')}`;
const formattedDateWithZero = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

test('月収登録から活動終了までのフロー', async ({ page }) => {
    await mockAuth(page);
    await mockRegisterSalary(page);

    await page.goto("/register/salary");

    await page.getByTestId("selected-month").fill(formattedMonthWithZero);
    await page.getByTestId("income-form").fill("30");
    await page.getByTestId("submit").click();

    await expect(page.getByText(`${year}-${month}の月収:30万円`)).toBeVisible();
    await mockGetMonthlySalary(page);
    await mockRegisterTarget(page);
    await mockRegisterActual(page);
    await mockFinishActivity(page);
    await mockNotFinishedActivities(page);

    await page.getByRole('link', { name: '活動記録' }).click();
    await page.getByTestId('target-date-row-0').fill(formattedDateWithZero);
    await page.getByTestId('target-time-row-0').fill('5');
    await page.getByTestId('submit-multi-target').click();
    await page.getByRole('button', { name: 'はい' }).click();
    await expect(page.getByText('【目標時間登録】登録1件、エラー0件')).toBeVisible();

    await page.getByTestId('actual').click();
    await page.getByTestId('actual-time-row-0').fill('6');
    await page.getByTestId('select-edited-activities').click();
    await page.getByTestId('submit-multi-actual').click();
    await page.getByRole('button', { name: 'はい' }).click();
    await expect(page.getByText('【活動時間登録】更新1件、エラー0件')).toBeVisible();

    await page.getByTestId('finish').click();
    await page.getByTestId('select-all-activities').click();
    await page.getByTestId('finish-multi').click();
    await page.getByRole('button', { name: 'はい' }).click();
    await expect(page.getByText('【活動終了】終了済み1件、エラー0件')).toBeVisible();
});
