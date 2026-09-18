import { test, expect } from '@playwright/test';
import { mockAuth } from './mocks/auth';
import { mockChangePassword } from './mocks/user';

test.use({
    ignoreHTTPSErrors: true
});


test('パスワード変更', async ({ page }) => {
    await mockAuth(page);
    await mockChangePassword(page);

    await page.goto("/user/info");
    await page.getByText("パスワード変更").click();

    await page.getByTestId("isPasswordChangeEnabled").click();
    await page.getByTestId("oldPassword").fill("oldPassword1!");
    await page.getByTestId("newPassword").fill("newPassword1!");
    await page.getByTestId("newPasswordCheck").fill("newPassword1!");
    await page.getByTestId("password-change-button").click();

    await expect(page.getByText("パスワードの変更に成功しました")).toBeVisible();
});
