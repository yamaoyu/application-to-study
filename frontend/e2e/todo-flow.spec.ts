import { test, expect } from '@playwright/test';
import { mockAuth } from './mocks/auth';
import { mockTodos } from './mocks/todo';

test.use({
    ignoreHTTPSErrors: true
});

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算
const day = today.getDate();
const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

test('Todoを登録してから終了するまでのフロー', async ({ page }) => {
    await mockAuth(page);
    await mockTodos(page);

    await page.goto("/register/todo");

    await page.getByTestId('add-todo').click();
    await page.getByTestId('title').fill('title');
    await page.getByTestId('detail').fill('detail');
    await page.getByTestId('due').fill(formattedDate);
    await page.getByRole('button', { name: 'OK' }).click();
    await page.getByTestId('submit-todo').click();
    await expect(page.getByTestId("message")).toContainText('Todo作成成功');

    await page.getByRole('link', { name: 'Todo確認' }).click();
    await page.getByText('編集').last().click(); // 先ほど追加した新しいtodoを操作する
    await page.getByRole('textbox', { name: 'title' }).fill('title-new');
    await page.getByRole('dialog', { name: 'Todo編集' }).locator('input[type="date"]').fill(formattedDate);
    await page.getByRole('textbox', { name: 'detail' }).fill('detail-new');
    await page.getByRole('button', { name: '送信' }).click();
    await expect(page.getByTestId("message")).toContainText('Todo更新成功');

    await page.getByRole('button', { name: '一括操作ON' }).click();
    await page.getByRole('checkbox').last().click(); // 先ほど追加した新しいtodoを操作する
    await page.getByText('一括終了').click();
    await page.getByRole('button', { name: '送信' }).click();
    await expect(page.getByTestId('message')).toContainText('Todo終了成功');
});
