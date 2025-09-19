import { describe, it, expect, vi, beforeEach } from 'vitest';
import ShowTodo from '@/views/ShowTodo.vue';
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('フィルターなし', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("データあり", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedTodos
        });

        await wrapper.vm.getTodos();
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        expect(wrapper.vm.todos).toEqual(expectedTodos);
    });

    it("データなし", async() =>{
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
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },            
        )
        expect(wrapper.vm.todoMsg).toBe(expectedMessage);
    });
});

describe('フィルターの操作', ()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("ステータスを選択", async() =>{
        // すべてに変更
        wrapper.vm.statusFilter = "すべて";
        expect(wrapper.vm.statusFilter).toEqual("すべて");
        // 未完了に変更
        wrapper.vm.statusFilter = "未完了";
        expect(wrapper.vm.statusFilter).toEqual("未完了");
        // 完了に変更
        wrapper.vm.statusFilter = "完了";
        expect(wrapper.vm.statusFilter).toEqual("完了");
        
    });

    it("期限(以前)を入力", async() =>{
        wrapper.vm.startDue = "2025-1-1";
        expect(wrapper.vm.startDue).toEqual("2025-1-1");
    });

    it("期限(以降)を入力", async() =>{
        wrapper.vm.endDue = "2025-1-1";
        expect(wrapper.vm.endDue).toEqual("2025-1-1");
    });

    it("タイトルを入力", async() =>{
        wrapper.vm.title = "title";
        expect(wrapper.vm.title).toEqual("title");
    });

    it("フィルターをリセット", async() =>{
        wrapper.vm.statusFilter = "完了";
        wrapper.vm.startDue = "2025-1-1";
        wrapper.vm.endDue = "2025-1-2";
        wrapper.vm.title = "title";
        // リセット
        await wrapper.find("[data-testid='reset']").trigger("click");
        expect(wrapper.vm.statusFilter).toEqual("");
        expect(wrapper.vm.startDue).toEqual("");
        expect(wrapper.vm.endDue).toEqual("");
        expect(wrapper.vm.title).toEqual("");
    });
});

describe('ステータスでフィルター', ()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("完了", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: [expectedTodos[0]]
        });

        // フィルター適用前
        wrapper.vm.todos = expectedTodos;
        expect(wrapper.vm.todos).toEqual(expectedTodos);

        wrapper.vm.statusFilter = "true";
        await wrapper.find("[data-testid='apply']").trigger("click");
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos?status=true",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual([expectedTodos[0]]);
    });

    it("未完了", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: [expectedTodos[1]]
        });

        // フィルター適用前
        wrapper.vm.todos = expectedTodos;
        expect(wrapper.vm.todos).toEqual(expectedTodos);

        wrapper.vm.statusFilter = "false";
        await wrapper.find("[data-testid='apply']").trigger("click");
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos?status=false",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual([expectedTodos[1]]);
    });
});

describe('期限(以前)でフィルター', ()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("データあり", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: [expectedTodos[0]]
        });

        // フィルター適用前
        wrapper.vm.todos = expectedTodos;
        expect(wrapper.vm.todos).toEqual(expectedTodos);

        wrapper.vm.startDue = "2025-1-1";
        await wrapper.find("[data-testid='apply']").trigger("click");
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos?start_due=2025-1-1",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual([expectedTodos[0]]);
    });
});

describe('期限(以降)でフィルター', ()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("データあり", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: [expectedTodos[1]]
        });

        // フィルター適用前
        wrapper.vm.todos = expectedTodos;
        expect(wrapper.vm.todos).toEqual(expectedTodos);

        wrapper.vm.endDue = "2025-1-2";
        await wrapper.find("[data-testid='apply']").trigger("click");
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos?end_due=2025-1-2",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual([expectedTodos[1]]);
    });
});

describe('タイトル名でフィルター', ()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowTodo);
        }
    );

    it("データあり", async() =>{
        const expectedTodos = [
            {
                detail: "test detail1",
                due: "2025-1-1",
                status: true,
                title: "test title1",
                todo_id: 1,
                username: "test"
            },
            {
                detail: "test detail2",
                due: "2025-1-2",
                status: false,
                title: "test title2",
                todo_id: 2,
                username: "test"
            },
        ];

        axios.get.mockResolvedValue({
            status: 200,
            data: [expectedTodos[0]]
        });

        // フィルター適用前
        wrapper.vm.todos = expectedTodos;
        expect(wrapper.vm.todos).toEqual(expectedTodos);

        wrapper.vm.title = "title1";
        await wrapper.find("[data-testid='apply']").trigger("click");
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "todos?title=title1",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );
        expect(wrapper.vm.todos).toEqual([expectedTodos[0]]);
    });
});