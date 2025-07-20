import { describe, it, expect, vi, beforeEach } from 'vitest'
import Login from '@/views/LoginForm.vue'
import { mockAxios, mountComponent } from './vitest.setup';

describe('Login', () => {
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(Login)
    })

    it('ログインに成功', async () => {
        mockAxios.post.mockResolvedValue({
            status: 200,
            data: {
                access_token: 'mock-token',
                token_type: 'Bearer'
            }
        });

        await wrapper.find('[data-testid="username"]').setValue("testuser");
        // ユーザー名が正しく入力されていることを確認
        expect(wrapper.find('[data-testid="username"]').element.value).toBe("testuser");
        await wrapper.find('[data-testid="password"]').setValue("Test1234!");
        // パスワードが正しく入力されていることを確認
        expect(wrapper.find('[data-testid="password"]').element.value).toBe("Test1234!");
        expect(wrapper.find('[data-testid="login-button"]').exists()).toBe(true);
        await wrapper.find('[data-testid="login-button"]').trigger('submit');
        // リクエストが正しく行われたことを確認
        expect(mockAxios.post).toHaveBeenCalledTimes(1)
        expect(mockAxios.post).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + "login",  // 正しいURL
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
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(Login)
    })

    it('ユーザー名を入力していない場合、ユーザー名の入力を求めるメッセージを表示する', async () => {
        const usernameInput = wrapper.find('[data-testid="username"]');
        // ユーザー名の入力が空であることを確認
        expect(usernameInput.element.value).toBe("");
        await wrapper.find('[data-testid="login-form"]').trigger('submit');
        // ユーザー名の入力を求めるメッセージを表示されることを確認
        expect(usernameInput.element.validity.valid).toBe(false);
        expect(usernameInput.element.validity.valueMissing).toBe(true);
        // リクエストが送信されないことを確認
        expect(mockAxios.post).toHaveBeenCalledTimes(0);
    })
})

describe('パスワードを入力せずにログインしようとする', () => {
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(Login)
    })

    it('パスワードを入力していない場合、パスワードの入力を求めるメッセージを表示する', async () => {
        await wrapper.find('[data-testid="username"]').setValue("testuser");
        // ユーザー名が入力されていることを確認
        expect(wrapper.find('[data-testid="username"]').element.value).toBe("testuser");
        const passwordInput = wrapper.find('[data-testid="password"]');
        // パスワードの入力が空であることを確認
        expect(passwordInput.element.value).toBe("");
        await wrapper.find('[data-testid="login-form"]').trigger('submit');
        // パスワードの入力を求めるメッセージを表示されることを確認
        expect(passwordInput.element.validity.valid).toBe(false);
        expect(passwordInput.element.validity.valueMissing).toBe(true);
        // リクエストが送信されないことを確認
        expect(mockAxios.post).toHaveBeenCalledTimes(0);
    })
})