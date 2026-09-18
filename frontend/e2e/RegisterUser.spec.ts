import { test, expect } from '@playwright/test';
import { mockRegisterUser } from './mocks/user';

test.use({
    ignoreHTTPSErrors: true
});

test("Todoのを削除する", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("username").fill("username");
    await page.getByTestId("password").fill("Abcdefg1!");
    await page.getByTestId("passwordCheck").fill("Abcdefg1!");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByText("usernameを作成しました")).toBeVisible();
});
