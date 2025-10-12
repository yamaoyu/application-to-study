import { describe, it, expect, vi, beforeEach } from 'vitest'
import RegisterTodo from '@/views/RegisterTodo.vue'
import { mountComponent } from './vitest.setup';
import axios from 'axios';
import { nextTick } from 'vue';
import { flushPromises } from '@vue/test-utils';


describe('Todoを送信に成功', () => {
    let wrapper;

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

        axios.post.mockResolvedValue({
            status: 201,
            data:  {
                message: expectedMessage
            }
        });
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect(wrapper.vm.modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // タイトル
        const titleInput = modal.querySelector('[data-testid="title"]');
        expect(titleInput).not.toBeNull();
        titleInput.value = expectedTodo.title;
        expect(titleInput.value).toEqual(expectedTodo.title);
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));
        // 詳細
        const detailInput = modal.querySelector('[data-testid="detail"]');
        expect(detailInput).not.toBeNull();
        detailInput.value = expectedTodo.detail;
        expect(detailInput.value).toEqual(expectedTodo.detail);
        detailInput.dispatchEvent(new Event('input', { bubbles: true }));
        // 期限
        const dueInput = modal.querySelector('[data-testid="due"]');
        expect(dueInput).not.toBeNull();
        dueInput.value = expectedTodo.due;
        expect(dueInput.value).toEqual(expectedTodo.due);
        dueInput.dispatchEvent(new Event('input', { bubbles: true }));

        // todoをリストに追加
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        expect(wrapper.vm.todos).toEqual([expectedTodo]);

        // todoを登録
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        await flushPromises(); // 非同期処理(今回はaxiosリクエスト)の終了を待つ
        // APIが正しいパラメータで呼び出されたことを確認
        expect(axios.post).toHaveBeenCalledTimes(1);
        expect(axios.post).toHaveBeenCalledWith(
            process.env.VITE_BACKEND_URL + 'todos/multi', 
            { todos : [expectedTodo] },
            {
                headers: {
                    "Authorization": "登録なし"
                }
            }
        );
        // メッセージとtodosがリセットされることを確認
        expect(wrapper.find('[data-testid="message"]').element.textContent).toBe(expectedMessage);
        expect(wrapper.vm.todos).toEqual([]);
    });
});

describe('リクエストを送信できないパターン', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('Todoがない場合は送信ボタンをクリックできない', async () => {
        expect(wrapper.vm.todos).toEqual([]);
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        expect(axios.post).toBeCalledTimes(0);
    });

    it('Todoが10個以上の場合は送信ボタンをクリックできない', async () => {
        const expectedTodo = [
            { title: 'Test Todo1', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo2', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo3', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo4', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo5', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo6', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo7', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo8', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo9', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo10', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo11', detail: 'This is a test todo detail', due: '2025-01-01'},
        ];
        wrapper.vm.todos = expectedTodo;
        await flushPromises();
        expect(wrapper.vm.message).toEqual("一度に登録できるのは10件までです");
        wrapper.find('[data-testid="submit-todo"]').trigger("submit");
        expect(axios.post).toBeCalledTimes(0);
    });
});

describe('必須項目を入力せずリストにtodoを追加できないパターン', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    });

    it('タイトルの入力がない場合は送信ボタンをクリックできない', async () => {
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect(wrapper.vm.modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // 期限
        const dueInput = modal.querySelector('[data-testid="due"]');
        expect(dueInput).not.toBeNull();
        dueInput.value = "2025-01-01";
        expect(dueInput.value).toEqual("2025-01-01");
        dueInput.dispatchEvent(new Event('input', { bubbles: true }));

        // クリックできるか確認
        expect(wrapper.vm.validateParams()).toBe(false);
    });

    it('期限の入力がない場合は送信ボタンをクリックできない', async () => {
        // モーダルを開いてtodoを入力
        const addButton = wrapper.find('[data-testid="add-todo"]');
        addButton.trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect(wrapper.vm.modalTitle).toEqual("Todo作成");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ
        // フォームにデータを入力
        // タイトル
        const titleInput = modal.querySelector('[data-testid="title"]');
        expect(titleInput).not.toBeNull();
        titleInput.value = "title";
        expect(titleInput.value).toEqual("title");
        titleInput.dispatchEvent(new Event('input', { bubbles: true }));

        // クリックできるか確認
        expect(wrapper.vm.validateParams()).toBe(false);
    });
});

describe('リストからtodo削除', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('期限の入力がない場合は送信ボタンをクリックできない', async () => {
        const todos = [
            { title: 'Test Todo1', detail: 'This is a test todo detail', due: '2025-01-01'},
            { title: 'Test Todo2', detail: 'This is a test todo detail', due: '2025-01-01'}
        ];

        const expectedTodo = [
            { title: 'Test Todo1', detail: 'This is a test todo detail', due: '2025-01-01'}
        ];

        wrapper.vm.todos = todos;
        await flushPromises();
        wrapper.find('[data-testid="del-todo-1"]').trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();
        expect(wrapper.vm.modalTitle).toEqual("Todo削除確認");
        await nextTick(); // DOM要素(今回はモーダル)の更新を待つ

        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(wrapper.vm.todos).toEqual(expectedTodo);

    });
});