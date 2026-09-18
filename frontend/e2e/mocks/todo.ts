import type { Page } from '@playwright/test';
import { BACKEND_URL } from '../config';

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

            await route.continue();
        }
    );

    // await page.route(`${BACKEND_URL}/todos/bulk-finish`, async (route) => {
    //     if (route.request().method() !== 'POST') {
    //         await route.continue();
    //         return;
    //     }


    // });
}

// export async function mockDeleteTodo(page: Page) {
//     await page.route(`${BACKEND_URL}/todos/bulk-delete`, async (route) => {
//         if (route.request().method() !== 'POST') {
//             await route.continue();
//             return;
//         }

//         await route.fulfill({
//             status: 200,
//             json: {
//                 "success_count": 1,
//                 "error_count": 0,
//                 "results": [
//                     {
//                         "todo_id": 1,
//                         "title": "title1",
//                         "result": "success",
//                         "reason": null
//                     }
//                 ]
//             },
//         });
//     });
// }
