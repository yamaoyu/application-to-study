import { test, expect } from '@playwright/test';
import { mockAuth } from './mocks/auth';
import { mockRegisterTodo } from './mocks/todo';

test.use({
    ignoreHTTPSErrors: true
});

test('test', async ({ page }) => {
    await mockAuth(page);
    await mockRegisterTodo(page);

    await page.goto("/register/todos");

    await page.getByTestId('add-todo').click();
    await page.getByTestId('title').fill('title');
    await page.getByTestId('detail').fill('detail');
    await page.getByTestId('due').fill('2026-09-23');
    await page.getByRole('button', { name: 'OK' }).click();
    await page.getByTestId('submit-todo').click();
    await expect(page.getByTestId("message")).toContainText('Todo登録成功');
});
