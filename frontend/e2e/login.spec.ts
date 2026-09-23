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

// コンテナ作成時に作成しているテスト用ユーザーを使用する想定
const TEST_USERNAME: string = process.env.E2E_TEST_USER || "testuser1"
const TEST_USER_PASSWORD: string = process.env.E2E_TEST_PASSWORD || "Abcdefg1!"


test('ログイン成功', async ({ page }) => {
  // ログインのテストのみは実APIを使用してリロード後のトークン再取得まで確認できるようにする
  await page.goto("/login");
  await page.getByTestId(SELECTORS.username).fill(TEST_USERNAME);
  await page.getByTestId(SELECTORS.password).fill(TEST_USER_PASSWORD);
  await page.getByTestId(SELECTORS.loginButton).click();
  // // ログインに成功したか確認
  await expect(page).toHaveURL("/home");
  // ページをリロードしてもログイン状態が保持されるか確認
  await page.reload();
  await expect(page).toHaveURL("/home");
});

test('ユーザー名を入力していない場合、ユーザー名の入力を求めるメッセージを表示する', async ({ page }) => {
  // ログインのテストのみは実APIを使用してリロード後のトークン再取得まで確認できるようにする
  await page.goto("/login");
  await page.getByTestId(SELECTORS.password).fill(TEST_USER_PASSWORD);
  await page.getByTestId(SELECTORS.loginButton).click();
  // ログインに失敗し、ログインフォームにいる確認
  await expect(page).toHaveURL("/login");
  // ブラウザの制約が効いていることを確認
  await expect(page.getByTestId('username')).toHaveJSProperty(
    'validity.valueMissing',
    true,
  );
});

test('パスワードを入力していない場合、パスワードの入力を求めるメッセージを表示する', async ({ page }) => {
  // ログインのテストのみは実APIを使用してリロード後のトークン再取得まで確認できるようにする
  await page.goto("/login");
  await page.getByTestId(SELECTORS.username).fill(TEST_USERNAME);
  await page.getByTestId(SELECTORS.loginButton).click();
  // ログインに失敗し、ログインフォームにいる確認
  await expect(page).toHaveURL("/login");
  // ブラウザの制約が効いていることを確認
  await expect(page.getByTestId('password')).toHaveJSProperty(
    'validity.valueMissing',
    true,
  );
})
