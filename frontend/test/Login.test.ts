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
            "login",  // 正しいURL
            {
                username: "testuser",    // 正しいパラメータ
                password: "Test1234!"
            },
            {
                withCredentials: true    // 正しい設定
            }
        )
    })
})

describe('ユーザー名を入力せずにログインしようとする', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(Login)
    })

    it('ユーザー名を入力していない場合、ユーザー名の入力を求めるメッセージを表示する', async () => {
        const usernameInput = wrapper.find('[data-testid="username"]').element as HTMLInputElement;
        // ユーザー名の入力が空であることを確認
        expect(usernameInput.value).toBe("");
        await wrapper.find('[data-testid="login-form"]').trigger('submit');
        // ユーザー名の入力を求めるメッセージを表示されることを確認
        expect(usernameInput.validity.valid).toBe(false);
        expect(usernameInput.validity.valueMissing).toBe(true);
        // リクエストが送信されないことを確認
        expect(apiClient.post).toHaveBeenCalledTimes(0);
    })
})

describe('パスワードを入力せずにログインしようとする', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(Login)
    })

    it('パスワードを入力していない場合、パスワードの入力を求めるメッセージを表示する', async () => {
        const usernameInput = wrapper.find('[data-testid="username"]') as DOMWrapper<HTMLInputElement>;
        await usernameInput.setValue("testuser");
        // ユーザー名が入力されていることを確認
        expect(usernameInput.element.value).toBe("testuser");
        // パスワードの入力が空であることを確認
        const passwordInput = wrapper.find('[data-testid="password"]').element as HTMLInputElement;
        expect(passwordInput.value).toBe("");
        await wrapper.find('[data-testid="login-form"]').trigger('submit');
        // パスワードの入力を求めるメッセージを表示されることを確認
        expect(passwordInput.validity.valid).toBe(false);
        expect(passwordInput.validity.valueMissing).toBe(true);
        // リクエストが送信されないことを確認
        expect(apiClient.post).toHaveBeenCalledTimes(0);
    })
})