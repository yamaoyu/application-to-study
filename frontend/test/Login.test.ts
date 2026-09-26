import { describe, it, expect, vi, beforeEach } from 'vitest'
import Login from '@/views/LoginForm.vue'
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post);

describe('Login', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(Login)
    })

    it('ログインに成功', async () => {
        mockedPost.mockResolvedValue({
            status: 200,
            data: {
                access_token: 'mock-token',
                token_type: 'Bearer'
            }
        });
        // ユーザー名入力
        const usernameInput = wrapper.find('[data-testid="username"]') as DOMWrapper<HTMLInputElement>;
        await usernameInput.setValue("testuser");
        expect(usernameInput.element.value).toBe("testuser");

        // パスワード入力
        const passwordInput = wrapper.find('[data-testid="password"]') as DOMWrapper<HTMLInputElement>;
        await passwordInput.setValue("Test1234!");
        expect(passwordInput.element.value).toBe("Test1234!");
        expect(wrapper.find('[data-testid="login-button"]').exists()).toBe(true);
        await wrapper.find('[data-testid="login-button"]').trigger('submit');
        // リクエストが正しく行われたことを確認
        expect(apiClient.post).toHaveBeenCalledTimes(1)
        expect(apiClient.post).toHaveBeenCalledWith(
            "login",
            {
                username: "testuser",
                password: "Test1234!"
            },
            {
                withCredentials: true
            }
        )
    })

    it('ログインに失敗', async () => {
        mockedPost.mockRejectedValue({
            response: {
                status: 401,
                data: {
                    code: "LOGIN_FAILED",
                    message: "ユーザー名またはパスワードが正しくありません"
                }
            }
        });
        // ユーザー名入力
        const usernameInput = wrapper.find('[data-testid="username"]') as DOMWrapper<HTMLInputElement>;
        await usernameInput.setValue("testuser");
        expect(usernameInput.element.value).toBe("testuser");

        // パスワード入力
        const passwordInput = wrapper.find('[data-testid="password"]') as DOMWrapper<HTMLInputElement>;
        await passwordInput.setValue("WrongPassword!");
        expect(passwordInput.element.value).toBe("WrongPassword!");
        expect(wrapper.find('[data-testid="login-button"]').exists()).toBe(true);
        await wrapper.find('[data-testid="login-button"]').trigger('submit');
        // リクエストが正しく行われたことを確認
        expect(apiClient.post).toHaveBeenCalledTimes(1)
        expect(apiClient.post).toHaveBeenCalledWith(
            "login",
            {
                username: "testuser",
                password: "WrongPassword!"
            },
            {
                withCredentials: true
            }
        )
        // エラーメッセージが表示されることを確認
        expect(wrapper.find('[data-testid="message"]').text()).toBe("ユーザー名またはパスワードが正しくありません");
    })
})
