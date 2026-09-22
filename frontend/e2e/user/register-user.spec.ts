import { test, expect } from '@playwright/test';
import { mockRegisterUser } from '../mocks/user';

test.use({
    ignoreHTTPSErrors: true
});

test("ユーザー登録", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("username").fill("username");
    await page.getByTestId("password").fill("Abcdefg1!");
    await page.getByTestId("passwordCheck").fill("Abcdefg1!");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByText("usernameを作成しました")).toBeVisible();
});

test("ユーザー名を入力しない場合、エラーメッセージを表示する", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("password").fill("Abcdefg1!");
    await page.getByTestId("passwordCheck").fill("Abcdefg1!");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByTestId('username')).toHaveJSProperty(
        'validity.valueMissing',
        true,
    );
});

test("パスワードを入力しない場合、エラーメッセージを表示する", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("username").fill("username");
    await page.getByTestId("passwordCheck").fill("Abcdefg1!");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByTestId('password')).toHaveJSProperty(
        'validity.valueMissing',
        true,
    );
});

test("確認用パスワードを入力しない場合、エラーメッセージを表示する", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("username").fill("username");
    await page.getByTestId("password").fill("Abcdefg1!");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByTestId('passwordCheck')).toHaveJSProperty(
        'validity.valueMissing',
        true,
    );
});

test("正しい形式のメールアドレスを入力しない場合、エラーメッセージを表示する", async ({ page }) => {
    await mockRegisterUser(page);

    await page.goto("/register/user");
    await page.getByTestId("username").fill("username");
    await page.getByTestId("password").fill("Abcdefg1!");
    await page.getByTestId("passwordCheck").fill("Abcdefg1!");
    await page.getByTestId("email").fill("invalid-email");
    await page.getByTestId("register-user-button").click();

    await expect(page.getByTestId('email')).toHaveJSProperty(
        'validity.typeMismatch',
        true,
    );
});
