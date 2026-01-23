import { test, expect } from '@playwright/test';

test.use({
  ignoreHTTPSErrors: true
});

// アイテムの定数化
const SELECTORS = {
  username: 'username',
  password: 'password',
  loginButton: 'login-button'
};

const BASE_URL = process.env.FRONTEND_URL || 'https://local.example.com';

test('successfully login', async ({ page }) => {
  await page.goto(BASE_URL + "/login");
  await page.getByTestId(SELECTORS.username).fill('user1');
  await page.getByTestId(SELECTORS.password).fill('password');
  await page.getByTestId(SELECTORS.loginButton).click();
  // ログインに成功したか確認
  await expect(page).toHaveURL(BASE_URL + "/home");
  // ページをリロードしてもログイン状態が保持されるか確認
  await page.reload();
  await expect(page).toHaveURL(BASE_URL + "/home");
});