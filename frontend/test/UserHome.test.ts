import { describe, it, expect, vi, beforeEach } from 'vitest';
import UserHome from '@/views/UserHome.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';
import { getToday } from '@/views/utils/date';

const mockedGet = vi.mocked(apiClient.get);
const mockedPut = vi.mocked(apiClient.put);

const today = getToday().split("-");
const expectedYear = today[0];
const expectedMonth = today[1];
const expectedDate = today[2];

type mock =
    | { type: 'resolve'; value: { status: number; data: Record<string, any> } }
    | { type: 'reject'; value: { response: { status: number; data: { detail: string } } } };

const defaultActivityData = {
    date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
    target_time: 3,
    actual_time: 0,
    status: "pending",
    bonus: 0,
    penalty: 0.38
};

const defaultIncomeData = {
    month_info: {
        salary: 25,
        total_bonus: 0.38,
        total_penalty: 0
    },
    total_income: 25.38,
    pay_adjustment: 0.38
};


const defaultTodosData = [
    {
        todo_id: 1,
        title: "title1",
        detail: "detail1",
        due: "2025-1-1"
    },
    {
        todo_id: 2,
        title: "title2",
        detail: "detail2",
        due: "2025-1-2"
    }
];

const createResolvedMock = (data: Record<string, any>, status = 200): mock => ({
    type: "resolve",
    value: {
        status: status,
        data: data
    }
});

const createRejectedMock = (detail: string, status = 404): mock => ({
    type: "reject",
    value: {
        response: {
            status,
            data: {
                detail: detail
            }
        }
    }
});

const mountUserHome = async ({
    activityMock = createResolvedMock(defaultActivityData),
    incomeMock = createResolvedMock(defaultIncomeData),
    todosMock = createResolvedMock(defaultTodosData),
}: { activityMock?: mock, incomeMock?: mock, todosMock?: mock } = {}) => {
    [activityMock, incomeMock, todosMock].forEach((mock) => {
        if (mock.type === "reject") {
            mockedGet.mockRejectedValueOnce(mock.value);
        } else {
            mockedGet.mockResolvedValueOnce(mock.value);
        }
    });

    const wrapper = mountComponent(UserHome);
    await flushPromises();
    return wrapper;
};


describe('ユーザーホームの表示(データあり)', () => {
    let wrapper: VueWrapper;

    beforeEach(async () => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('活動実績のデータがある(ステータスが未確定)', async () => {
        const wrapper = await mountUserHome();
        const expectedMessage = "このままだと、0.38万円(3800円)のペナルティが発生";
        expect(mockedGet).toBeCalledWith(
            `activities/${expectedYear}/${expectedMonth}/${expectedDate}`
        );

        // メッセージの確認
        expect(wrapper.find("[data-testid='activity-msg']").text()).toEqual(expectedMessage);
    });

    it('活動実績のデータがある(ステータスが成功)', async () => {
        const expectedData = {
            date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
            target_time: 3,
            actual_time: 3,
            status: "success",
            bonus: 0.38,
            penalty: 0
        };
        const expectedMessage = "目標達成!\nボーナス:0.38万円(3800円)";
        wrapper = await mountUserHome({ activityMock: createResolvedMock(expectedData) });
        expect(mockedGet).toBeCalledWith(
            `activities/${expectedYear}/${expectedMonth}/${expectedDate}`
        );

        // メッセージの確認
        expect(wrapper.find("[data-testid='activity-msg']").text()).toEqual(expectedMessage);
    });

    it('活動実績のデータがある(ステータスが失敗)', async () => {
        const expectedData = {
            date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
            target_time: 3,
            actual_time: 3,
            status: "failure",
            bonus: 0,
            penalty: 0.38
        };
        const expectedMessage = "目標失敗...\nペナルティ:0.38万円(3800円)";

        wrapper = await mountUserHome({ activityMock: createResolvedMock(expectedData) });
        expect(mockedGet).toBeCalledWith(
            `activities/${expectedYear}/${expectedMonth}/${expectedDate}`
        );
        expect(wrapper.find("[data-testid='activity-msg']").text()).toEqual(expectedMessage);
    });

    it('給料のデータがある', async () => {
        wrapper = await mountUserHome();
        expect(mockedGet).toBeCalledWith(
            `incomes/${expectedYear}/${expectedMonth}`
        );
        expect(wrapper.find("[data-testid='total-income']").text()).toEqual(defaultIncomeData.total_income.toString());
    });

    it('未完了Todoのデータがある', async () => {
        wrapper = await mountUserHome();
        expect(mockedGet).toBeCalledWith(
            "todos?status=false"
        );
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(defaultTodosData.length);
    });
});

describe('ユーザーホームの表示(データなし)', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('活動実績のデータがない', async () => {
        const expectedMessage = `${getToday()}の活動実績は未登録です`;
        wrapper = await mountUserHome({
            activityMock: createRejectedMock(expectedMessage)
        });
        expect(wrapper.find("[data-testid='activity-msg']").text()).toEqual(expectedMessage);
    });

    it('給料のデータがない', async () => {
        const expectedMessage = "2025-1の月収は未登録です";

        wrapper = await mountUserHome({
            incomeMock: createRejectedMock(expectedMessage)
        });

        expect(wrapper.find("[data-testid='income-msg']").text()).toEqual(expectedMessage);
    });

    it('未完了Todoのデータがない', async () => {
        const expectedMessage = "登録された情報はありません";

        wrapper = await mountUserHome({
            todosMock: createRejectedMock(expectedMessage)
        });

        expect(wrapper.find("[data-testid='todo-msg']").text()).toEqual(expectedMessage);
    });
});

describe('Todoの操作', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('Todo編集', async () => {
        const expectedMessage = "Todoを更新しました";
        const title = "new title";
        const detail = "new detail";
        const due = "new due";

        // editTodo()のモック
        mockedPut.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage,
                title: title,
                detail: detail,
                due: due
            }
        })
        wrapper = await mountUserHome();
        // editTodo()後のtodo再取得処理のモック
        mockedGet.mockResolvedValueOnce({
            status: 200,
            data: [
                {
                    detail: detail,
                    due: due,
                    status: true,
                    title: title,
                    todo_id: 1,
                    username: "test"
                },
            ]
        });

        await wrapper.find("[data-testid='edit-0']").trigger("click");
        // モーダルが開かれていることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo編集");
        // 編集モードであることを確認してからOkボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        expect(bModal.props("title")).toBe("Todo編集");
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPut).toHaveBeenCalledWith(
            "todos/1",
            {
                title: defaultTodosData[0].title,
                detail: defaultTodosData[0].detail,
                due: defaultTodosData[0].due
            }
        );
        expect(mockedPut).toBeCalledTimes(1);
        expect(wrapper.find("[data-testid='todo-msg']").text()).toEqual(expectedMessage);
    });

    it('Todo終了', async () => {
        const title = "Test Todo";
        const status = true;
        const expectedMessage = `1件のTodoを終了しました`;

        // finishTodo()のモック
        mockedPut.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage,
                titles: title,
                status: status
            }
        })
        wrapper = await mountUserHome();
        // finishTodo()後のtodo再取得処理のモック
        mockedGet.mockResolvedValueOnce({
            status: 200,
            data: [
                {
                    detail: "test detail",
                    due: "2025-1-1",
                    status: true,
                    title: "test title",
                    todo_id: 1,
                    username: "test"
                }
            ]
        });
        // 終了ボタンをクリックし、モーダルを開く
        await wrapper.find("[data-testid='finish-0']").trigger("click");
        // モーダルが開かれていることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo終了確認");
        // 終了モードであることを確認してからOkボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        expect(bModal.props("title")).toBe("Todo終了確認");
        await bModal.vm.$emit('ok');
        await flushPromises();

        expect(mockedPut).toHaveBeenCalledWith(
            "todos/multi/finish",
            {
                ids: [1]
            }
        );
        expect(wrapper.find("[data-testid='todo-msg']").text()).toEqual(`${expectedMessage}\n${title}`);
    })

    it('Todo削除', async () => {
        // deleteTodo()のモック
        mockedPut.mockResolvedValue({
            status: 204
        })
        wrapper = await mountUserHome();
        // deleteTodo()後のtodo再取得処理のモック
        mockedGet.mockResolvedValueOnce({
            status: 200,
            data: [
                {
                    detail: "test detail",
                    due: "2025-1-1",
                    status: true,
                    title: "test title",
                    todo_id: 1,
                    username: "test"
                },
            ]
        });
        // 削除ボタンをクリックし、モーダルを開く
        await wrapper.find("[data-testid='delete-0']").trigger("click");
        // モーダルが開かれていることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo削除確認");
        // 削除モードであることを確認してからOkボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        expect(bModal.props("title")).toBe("Todo削除確認");
        await bModal.vm.$emit('ok');
        await flushPromises();

        expect(mockedPut).toHaveBeenCalledWith(
            "todos/multi/delete",
            {
                ids: [1]
            }
        );
        expect(wrapper.find("[data-testid='todo-msg']").text()).toEqual("選択したTodoを削除しました");
    })
})

describe('Todoのソート', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('登録順', async () => {
        wrapper = await mountUserHome();
        await wrapper.find("[data-testid='sort-todos-id']").trigger("click");
        await flushPromises();
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(defaultTodosData.length);
    })

    it('期限順', async () => {
        wrapper = await mountUserHome();
        await wrapper.find("[data-testid='sort-todos-due']").trigger("click");
        await flushPromises();
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(defaultTodosData.length);
    })
});

describe('Todoリストページ', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('ページの移動', async () => {
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
        const wrapper = await mountUserHome({ todosMock: createResolvedMock(todos) });

        // 1ページ目のTodoの内容確認
        expect(wrapper.vm.paginatedTodos).toEqual(todos.slice(0, 5));
        expect(wrapper.vm.currentPage).toBe(currentPage);

        // 2ページ目へ移動
        currentPage += 1;
        wrapper.vm.goToPage(currentPage);
        expect(wrapper.vm.currentPage).toBe(currentPage);

        // 2ページ目のTodoの内容確認
        expect(wrapper.vm.paginatedTodos).toEqual(todos.slice(-1))
    })
});
