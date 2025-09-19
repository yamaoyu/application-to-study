import { describe, it, expect, vi, beforeEach } from 'vitest'
import { flushPromises } from '@vue/test-utils'
import RegisterTodo from '@/views/RegisterTodo.vue'
import { mountComponent } from './vitest.setup';
import axios from 'axios';


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
        const expectedMessage = '以下の内容で作成しました';

        axios.post.mockResolvedValue({
            status: 201,
            data:  {
                message: expectedMessage,
                title: expectedTodo.title,
                detail: expectedTodo.detail,
                due: expectedTodo.due
            }
        });
        // 入力フィールドにタイトルを設定
        await wrapper.find('[data-testid="todo-title"]').setValue(expectedTodo.title);
        expect(wrapper.find('[data-testid="todo-title"]').element.value).toBe(expectedTodo.title);
        // 入力フィールドに詳細を設定
        await wrapper.find('[data-testid="todo-detail"]').setValue(expectedTodo.detail);
        expect(wrapper.find('[data-testid="todo-detail"]').element.value).toBe(expectedTodo.detail);
        // 入力フィールドに期限を設定
        await wrapper.find('[data-testid="todo-due"]').setValue(expectedTodo.due);
        expect(wrapper.find('[data-testid="todo-due"]').element.value).toBe(expectedTodo.due);
        // フォームを送信
        await wrapper.find('[data-testid="submit-todo"]').trigger('submit');
        await flushPromises();

        // APIが正しいパラメータで呼び出されたことを確認
        expect(axios.post).toHaveBeenCalledTimes(1);
        expect(axios.post).toHaveBeenCalledWith(
            process.env.VITE_BACKEND_URL + 'todos', 
            expectedTodo,
            {
                headers: {
                    "Authorization": "登録なし"
                }
            }
        );
        expect(wrapper.find('[data-testid="message"]').element.textContent).toBe(
            "以下の内容で作成しました\n" +
            "タイトル:Test Todo\n" +
            "詳細:This is a test todo detail\n" +
            "期限:2025-01-01"
        );
    });
});

describe('データを入力せずにリクエストが送信されないパターン', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterTodo)
    })

    it('Todoを送信に失敗', async () => {
        // タイトルの入力が空であることを確認
        const titleInput = wrapper.find('[data-testid="todo-title"]');
        expect(titleInput.element.value).toBe("");
        // タイトルの入力を求めるメッセージを表示されることを確認
        expect(titleInput.element.validity.valid).toBe(false);
        expect(titleInput.element.validity.valueMissing).toBe(true);
        await wrapper.find('[data-testid="submit-todo"]').trigger('submit');

        // リクエストが送信されないことを確認
        expect(axios.post).toHaveBeenCalledTimes(0);
    });
});