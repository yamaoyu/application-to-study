import { test, expect } from '@playwright/test';
import { mockAuth } from './mocks/auth';
import { mockUserHome } from './mocks/userHome';

test.use({
    ignoreHTTPSErrors: true
});


test("Todoの詳細を表示する", async ({ page }) => {
    await mockAuth(page);
    await mockUserHome(page);

    await page.goto("/home");

    await page.getByText("title1").click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await expect(page.getByRole("dialog")).toContainText("title1");
    await expect(page.getByRole("dialog")).toContainText("detail1");
    await expect(page.getByRole("dialog")).toContainText("2026-09-30");
});

test("Todoのを終了する", async ({ page }) => {
    await mockAuth(page);
    await mockUserHome(page);

    await page.goto("/home");

    await page.getByText("終了").click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByText("送信").click();
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expect(page.getByText("【Todo終了成功】")).toBeVisible();
});

test("Todoのを削除する", async ({ page }) => {
    await mockAuth(page);
    await mockUserHome(page);

    await page.goto("/home");

    await page.getByText("削除").click();
    await expect(page.getByRole("dialog")).toBeVisible();
    await page.getByText("送信").click();
    await expect(page.getByRole("dialog")).not.toBeVisible();
    await expect(page.getByText("【Todo削除成功】")).toBeVisible();
});
