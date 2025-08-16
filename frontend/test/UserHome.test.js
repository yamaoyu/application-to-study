import { describe, it, expect, vi, beforeEach } from 'vitest';
import UserHome from '@/views/UserHome.vue';
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('ユーザーホームの表示(データあり)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserHome);
        }
    );

    it('活動実績のデータがある(ステータスが未確定)', async() => {
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = today.getMonth() + 1;
        const expectedDate = today.getDate();
        
        const expectedData = {
            date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
            target_time: 3,
            actual_time: 0,
            status: "pending",
            bonus: 0,
            penalty: 0.38
        };
        const expectedMessage = "このままだと、0.38万円(3800円)のペナルティが発生";

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        // activityResに定義される
        await wrapper.vm.getTodayActivity();
        expect(wrapper.vm.activityRes.data).toEqual(expectedData);

        expect(axios.get).toBeCalledWith(
            process.env.VUE_APP_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}`,
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        // メッセージの確認
        wrapper.vm.setActivityMessage();
        expect(wrapper.vm.activityMsg).toEqual(expectedMessage);
    });

    it('活動実績のデータがある(ステータスが成功)', async() => {
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = today.getMonth() + 1;
        const expectedDate = today.getDate();

        const expectedData = {
            date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
            target_time: 3,
            actual_time: 3,
            status: "success",
            bonus: 0.38,
            penalty: 0
        };
        const expectedMessage = "目標達成!\nボーナス:0.38万円(3800円)";

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });
        
        // activityResに定義される
        await wrapper.vm.getTodayActivity();
        expect(wrapper.vm.activityRes.data).toEqual(expectedData);

        expect(axios.get).toBeCalledWith(
            process.env.VUE_APP_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}`,
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        // メッセージの確認
        wrapper.vm.setActivityMessage();
        expect(wrapper.vm.activityMsg).toEqual(expectedMessage);
    });

    it('活動実績のデータがある(ステータスが失敗)', async() => {
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = today.getMonth() + 1;
        const expectedDate = today.getDate();

        const expectedData = {
            date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
            target_time: 3,
            actual_time: 3,
            status: "failure",
            bonus: 0,
            penalty: 0.38
        };
        const expectedMessage = "目標失敗...\nペナルティ:0.38万円(3800円)";

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        // activityResに定義される
        await wrapper.vm.getTodayActivity();
        expect(wrapper.vm.activityRes.data).toEqual(expectedData);

        expect(axios.get).toBeCalledWith(
            process.env.VUE_APP_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}`,
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        // メッセージの確認
        wrapper.vm.setActivityMessage();
        expect(wrapper.vm.activityMsg).toEqual(expectedMessage);
    });

    it('給料のデータがある', async() =>{
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = today.getMonth() + 1;

        const expectedData = {
            month_info: {
                salary: 25,
                total_bonus: 0.38,
                total_penalty: 0
            },
            total_income: 25.38,
            pay_adjustment: 0.38
        };

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        await wrapper.vm.getThisMonthIncome();

        expect(axios.get).toBeCalledWith(
            process.env.VUE_APP_BACKEND_URL + `incomes/${expectedYear}/${expectedMonth}`,
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        expect(wrapper.vm.incomeRes.data).toEqual(expectedData);
    });

    it('未完了Todoのデータがある', async() =>{
        const expectedData = [
                {
                    todo_id : 1,
                    title: "title1",
                    detail: "detail1",
                    due: "due1"
                },
                {
                    todo_id : 2,
                    title: "title2",
                    detail: "detail2",
                    due: "due2"
                }
            ];

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        await wrapper.vm.getTodos();
        
        expect(axios.get).toBeCalledWith(
            process.env.VUE_APP_BACKEND_URL + "todos?status=false",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual(expectedData);
    });
});

describe('ユーザーホームの表示(データなし)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserHome);
        }
    );

    it('活動実績のデータがない', async() => {
        const expectedMessage = "2025-1-1の活動記録は未登録です";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.getTodayActivity();
        expect(wrapper.vm.activityMsg).toEqual(expectedMessage);
    });

    it('給料のデータがない', async() =>{
        const expectedMessage = "2025-1の月収は未登録です";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.getThisMonthIncome();
        expect(wrapper.vm.incomeMsg).toEqual(expectedMessage);
    });

    it('未完了Todoのデータがない', async() =>{
        const expectedMessage = "登録された情報はありません";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.getTodos();
        expect(wrapper.vm.todoMsg).toEqual(expectedMessage);
    });
});

describe('Todoの操作', () =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserHome);
        }
    );

    it('Todo編集', async() =>{
        const expectedMessage = "Todoを更新しました";
        const title = "new title";
        const detail = "new detail";
        const due = "new due";

        // editTodo()のモック
        axios.put.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage,
                title: title,
                detail: detail,
                due: due
            }
        })
        // editTodo()後のtodo際取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: {
                0: {
                    detail: "test detail",
                    due: "2025-1-1",
                    status: true,
                    title: "test title",
                    todo_id: 1,
                    username: "test"
                    },
            }
        });

        wrapper.vm.todoId = 1;
        wrapper.vm.newTodoTitle = title;
        wrapper.vm.newTodoDetail = detail;
        wrapper.vm.newTodoDue = due;
        await wrapper.vm.editTodo();
        expect(axios.put).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + "todos/1",
            {
                "detail": detail,
                "due": due,
                "title": title,
            },
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(axios.put).toBeCalledTimes(1);
        expect(wrapper.vm.todoMsg).toEqual(expectedMessage);
    })

    it('Todo終了', async() =>{
        const expectedMessage = "選択したTodoを終了しました";
        const title = "new title";
        const status = true;

        wrapper.vm.todoId = 1;
        // finishTodo()のモック
        axios.put.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage,
                title: title,
                status: status
            }
        })
        // finishTodo()後のtodo際取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: {
                0: {
                    detail: "test detail",
                    due: "2025-1-1",
                    status: true,
                    title: "test title",
                    todo_id: 1,
                    username: "test"
                    },
            }
        });
        await wrapper.vm.finishTodo();

        expect(axios.put).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + "todos/finish/1",
            {
            },
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(axios.put).toBeCalledTimes(1);        
        expect(wrapper.vm.todoMsg).toEqual(expectedMessage);
    })

    it('Todo削除', async() =>{
        // deleteTodo()のモック
        wrapper.vm.todoId = 1;
        axios.delete.mockResolvedValue({
            status: 204
        })
        // deleteTodo()後のtodo際取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: {
                0: {
                    detail: "test detail",
                    due: "2025-1-1",
                    status: true,
                    title: "test title",
                    todo_id: 1,
                    username: "test"
                    },
            }
        });

        await wrapper.vm.deleteTodo();
        expect(axios.delete).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + "todos/1",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(axios.delete).toBeCalledTimes(1);  
        expect(wrapper.vm.todoMsg).toEqual("選択したtodoを削除しました");
    })
})

describe('Todoのソート', () =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserHome);
        }
    );

    it('登録順', async() =>{
        const originalTodos = {
            1: {
                detail: "test detail2",
                due: "2025-1-1",
                status: true,
                title: "test title2",
                todo_id: 1,
                username: "test"
                },
            0: {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
                },
        };
        wrapper.vm.todos.value = originalTodos;
        const expectedTodos = {
            0: {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
                },
            1: {
                detail: "test detail2",
                due: "2025-1-1",
                status: true,
                title: "test title2",
                todo_id: 1,
                username: "test"
                },
        };
        await wrapper.vm.sortTodos("id");
        expect(wrapper.vm.todos.value).toEqual(expectedTodos);
    })

    it('期限順', async() =>{
        const originalTodos = {
            0: {
                detail: "test detail1",
                due: "2025-1-2",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
                },
            1: {
                detail: "test detail2",
                due: "2025-1-1",
                status: true,
                title: "test title2",
                todo_id: 1,
                username: "test"
                },
        };
        wrapper.vm.todos.value = originalTodos;
        const expectedTodos = {
            1: {
                detail: "test detail2",
                due: "2025-1-1",
                status: true,
                title: "test title2",
                todo_id: 1,
                username: "test"
                },
            0: {
                detail: "test detail1",
                due: "2025-1-2",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
                },
        };
        await wrapper.vm.sortTodos("due");
        expect(wrapper.vm.todos.value).toEqual(expectedTodos);
    })
});

describe('Todoリストページ', () =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserHome);
        }
    );

    it('ページの移動', async() =>{
        let currentPage = 1;
        const todos = [
            {
                detail: "test detail1",
                due: "2025-1-2",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-1",
                status: true,
                title: "test title2",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail3",
                due: "2025-1-2",
                status: true,
                title: "test title3",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail4",
                due: "2025-1-1",
                status: true,
                title: "test title4",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail5",
                due: "2025-1-2",
                status: true,
                title: "test title5",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail6",
                due: "2025-1-1",
                status: true,
                title: "test title6",
                todo_id: 1,
                username: "test"
            },
        ];

        // 1ページ目のTodoの内容確認
        wrapper.vm.todos = todos;
        expect(wrapper.vm.paginatedTodos).toEqual(todos.slice(0,5));
        expect(wrapper.vm.currentPage).toBe(currentPage);

        // 2ページ目へ移動
        currentPage += 1;
        console.log()
        wrapper.vm.goToPage(currentPage);
        expect(wrapper.vm.currentPage).toBe(currentPage);

        // 2ページ目のTodoの内容確認
        expect(wrapper.vm.paginatedTodos).toEqual(todos.slice(-1))
    })
})