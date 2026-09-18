import type { Page } from '@playwright/test';
import { mockActivityByDay } from './activity';
import { mockGetMonthlySalary } from './salary';
import { mockTodos } from './todo';

export async function mockUserHome(page: Page) {
    await mockActivityByDay(page);
    await mockGetMonthlySalary(page);
    await mockTodos(page);
}