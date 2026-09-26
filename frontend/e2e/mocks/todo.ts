import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

const today = new Date();
const year = today.getFullYear();
const month = today.getMonth() + 1; // 月は0から始まるため、1を加算
const day = today.getDate();
const formattedDate = `${year}-${month.toString().padStart(2, '0')}-${day.toString().padStart(2, '0')}`;

export async function mockTodos(page: Page) {
    let todos = [
        {
            todo_id: 1,
            title: 'title1',
            detail: 'detail1',
            due: '2026-09-30',
            status: false,
        },
    ];

    await page.route(
        url => url.origin === BACKEND_URL && url.pathname.startsWith('/todos'),
        async (route) => {
            const request = route.request();
            const method = request.method();
            const url = new URL(request.url());

            if (method === 'GET') {
                await route.fulfill({
                    status: 200,
                    json: { todos },
                });
                return;
            }

            if (
                method === "POST" &&
                url.pathname.endsWith('/todos/bulk-delete')
            ) {
                // 削除後の取得処理用に削除したtodoを配列から削除する
                const { ids } = request.postDataJSON();
                todos = todos.filter(todo => !ids.includes(todo.todo_id));

                // 削除のモック
                await route.fulfill({
                    status: 200,
                    json: {
                        "success_count": 1,
                        "error_count": 0,
                        "results": [
                            {
                                "todo_id": 1,
                                "title": "title1",
                                "result": "success",
                                "reason": null
                            }
                        ]
                    },
                });

                return;
            }

            if (
                method === "PATCH" &&
                url.pathname.endsWith('/todos/bulk-finish')
            ) {
                // 削除後の取得処理用に削除したtodoを配列から削除する
                const { ids } = request.postDataJSON();
                todos = todos.filter(todo => !ids.includes(todo.todo_id));

                // 削除のモック
                await route.fulfill({
                    status: 200,
                    json: {
                        "success_count": 1,
                        "error_count": 0,
                        "results": [
                            {
                                "todo_id": 1,
                                "title": "title1",
                                "result": "success",
                                "reason": null
                            }
                        ]
                    },
                });
                return;
            }

            if (
                method === "PATCH" &&
                url.pathname.startsWith('/todos/update')
            ) {
                todos[1] =
                {
                    todo_id: 2,
                    title: 'title-new',
                    detail: 'detail-new',
                    due: formattedDate,
                    status: false,
                }

                await route.fulfill({
                    status: 200,
                    json: {
                        "success_count": 1,
                        "error_count": 0,
                        "results": [
                            {
                                "title": "title-new",
                                "due": formattedDate,
                                "detail": "detail-new",
                                "result": "success",
                                "reason": null
                            }
                        ]
                    },
                });
                return;
            }

            await route.continue();
        }
    );

    await page.route(`${BACKEND_URL}/todos/bulk-create`, async (route) => {
        if (route.request().method() !== 'POST') {
            await route.continue();
            return;
        }

        todos.push(
            {
                todo_id: 2,
                title: 'title',
                detail: 'detail',
                due: formattedDate,
                status: false,
            },
        )

        await route.fulfill({
            status: 200,
            json: {
                "success_count": 1,
                "error_count": 0,
                "results": [
                    {
                        "title": "title",
                        "due": formattedDate,
                        "detail": "detail",
                        "reason": null,
                        "result": "success"
                    }
                ]
            },
        });
    });
}
