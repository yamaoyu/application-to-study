import { describe, it, expect, vi, beforeEach } from 'vitest'
import RegisterTodo from '@/views/RegisterTodo.vue'
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { nextTick } from 'vue';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post);

describe('Todoを送信に成功', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('Todoを送信に成功', async () => {
        const expectedTodo = {
            title: 'Test Todo',
            detail: 'This is a test todo detail',
            due: '2025-01-01'
        };
        const expectedMessage = '【Todo作成成功】' + expectedTodo.title;

        mockedPost.mockResolvedValue({
            status: 201,
            data: {
                message: expectedMessage
            }
        });
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // タイトル
        const titleInput = modal.querySelector('[data-testid="title"]') as HTMLInputElement;
        expect(titleInput).not.toBeNull();
        titleInput.value = expectedTodo.title;
        expect(titleInput.value).toEqual(expectedTodo.title);
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
        // 詳細
        const detailInput = modal.querySelector('[data-testid="detail"]') as HTMLInputElement;
        expect(detailInput).not.toBeNull();
        detailInput.value = expectedTodo.detail;
        expect(detailInput.value).toEqual(expectedTodo.detail);
        detailInput.dispatchEvent(new Event('input', { bubbles: true }));
        // 期限
        const dueInput = modal.querySelector('[data-testid="due"]') as HTMLInputElement;
        expect(dueInput).not.toBeNull();
        dueInput.value = expectedTodo.due;
        expect(dueInput.value).toEqual(expectedTodo.due);
        dueInput.dispatchEvent(new Event('input', { bubbles: true }));

        // todoをリストに追加
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength([expectedTodo].length);

        // todoを登録
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        await flushPromises(); // 非同期処理(今回はaxiosリクエスト)の終了を待つ
        // APIが正しいパラメータで呼び出されたことを確認
        expect(mockedPost).toHaveBeenCalledTimes(1);
        expect(mockedPost).toHaveBeenCalledWith(
            'todos/multi',
            { todos: [expectedTodo] }
        );
        // メッセージとtodosがリセットされることを確認
        expect(wrapper.find('[data-testid="message"]').element.textContent).toBe(expectedMessage);
        const newRows = wrapper.findAll('[data-testid="todo-row"]');
        expect(newRows).toHaveLength(0);
    });
});

describe('リクエストを送信できないパターン', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('Todoがない場合は送信ボタンをクリックできない', async () => {
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(0);
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        expect(mockedPost).toBeCalledTimes(0);
    });

    it('Todoが10個を超える場合は送信ボタンをクリックできない', async () => {
        for (let i = 0; i < 11; i++) {
            await wrapper.find('[data-testid="add-todo"]').trigger('click');
            const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
            (modal.querySelector('[data-testid="title"]') as HTMLInputElement).value = `T${i}`;
            (modal.querySelector('[data-testid="title"]') as HTMLInputElement).dispatchEvent(new Event('input', { bubbles: true }));
            (modal.querySelector('[data-testid="due"]') as HTMLInputElement).value = '2025-01-01';
            (modal.querySelector('[data-testid="due"]') as HTMLInputElement).dispatchEvent(new Event('input', { bubbles: true }));
            const bModal = wrapper.findComponent({ name: 'BModal' });
            await bModal.vm.$emit('ok');
            await flushPromises();
        };
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(11);
        const messageElement = wrapper.find('[data-testid="message"]');
        expect(messageElement.text()).toBe("一度に登録できるのは10件までです");
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        expect(mockedPost).toBeCalledTimes(0);
    });
});

describe('必須項目を入力せずリストにtodoを追加できないパターン', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    });

    it('タイトルの入力がない場合は送信ボタンをクリックできない', async () => {
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        await addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // 期限
        const dueInput = modal.querySelector('[data-testid="due"]') as HTMLInputElement;
        expect(dueInput).not.toBeNull();
        dueInput.value = "2025-01-01";
        expect(dueInput.value).toEqual("2025-01-01");
        dueInput.dispatchEvent(new Event('input', { bubbles: true }));

        // クリックできるか確認
        expect((wrapper.vm as any).validateTodo("create", { title: "", due: "" })).toBe(false);
    });

    it('期限の入力がない場合は送信ボタンをクリックできない', async () => {
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // タイトル
        const titleInput = modal.querySelector('[data-testid="title"]') as HTMLInputElement;
        expect(titleInput).not.toBeNull();
        titleInput.value = "title";
        expect(titleInput.value).toEqual("title");
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));

        // クリックできるか確認
        expect((wrapper.vm as any).validateTodo("create", { title: "", due: "" })).toBe(false);
    });
});

describe('リストからtodo削除', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('todoを削除できる', async () => {
        for (let i = 0; i < 3; i++) {
            await wrapper.find('[data-testid="add-todo"]').trigger('click');
            const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
            (modal.querySelector('[data-testid="title"]') as HTMLInputElement).value = `T${i}`;
            (modal.querySelector('[data-testid="title"]') as HTMLInputElement).dispatchEvent(new Event('input', { bubbles: true }));
            (modal.querySelector('[data-testid="due"]') as HTMLInputElement).value = '2025-01-01';
            (modal.querySelector('[data-testid="due"]') as HTMLInputElement).dispatchEvent(new Event('input', { bubbles: true }));
            const bModal = wrapper.findComponent({ name: 'BModal' });
            await bModal.vm.$emit('ok');
            await flushPromises();
        };
        const rows = wrapper.findAll('[data-testid="todo-row"]');
        expect(rows).toHaveLength(3);
        await flushPromises();
        wrapper.find('[data-testid="del-todo-1"]').trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']") as HTMLDivElement;
        expect(modal).not.toBeNull();
        expect((wrapper.vm as any).modalTitle).toEqual("Todo削除確認");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ

        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        await flushPromises();
        const newRows = wrapper.findAll('[data-testid="todo-row"]');
        expect(newRows).toHaveLength(2);

    });
});