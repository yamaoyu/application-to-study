import { describe, it, expect, vi, beforeEach } from 'vitest'
import RegisterUser from '@/views/RegisterUser.vue'
import { mockAxios, mountComponent } from './vitest.setup';

describe('ユーザー作成', () => {
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(RegisterUser)
    })

    it('ユーザー作成に成功', async () => {
        mockAxios.post.mockResolvedValue({
            status: 200,
            data: {
                access_token: 'mock-token',
                token_type: 'Bearer'
            }
        });

        // ユーザー名が正しく入力されていることを確認
        await wrapper.find('[data-testid="username"]').setValue("testuser");
        expect(wrapper.find('[data-testid="username"]').element.value).toBe("testuser");
        // パスワードが正しく入力されていることを確認
        await wrapper.find('[data-testid="password"]').setValue("Test1234!");
        expect(wrapper.find('[data-testid="password"]').element.value).toBe("Test1234!");
        // 確認用パスワードが正しく入力されていることを確認
        await wrapper.find('[data-testid="passwordCheck"]').setValue("Test1234!");
        expect(wrapper.find('[data-testid="passwordCheck"]').element.value).toBe("Test1234!");
        // パスワードと確認用パスワードが一致していることを確認
        expect(wrapper.vm.isEqualPassword).toBe(true);
        // メールアドレスが正しく入力されていることを確認
        await wrapper.find('[data-testid="email"]').setValue("test@example.com");
        expect(wrapper.find('[data-testid="email"]').element.value).toBe("test@example.com");
        // リクエストが正しく行われたことを確認
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        console.log(mockAxios.post)
        expect(mockAxios.post).toHaveBeenCalledTimes(1)
        expect(mockAxios.post).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + "users",  // 正しいURL
            {
                username: "testuser",    // 正しいパラメータ
                password: "Test1234!",
                email: "test@example.com"
            }
        )
    })
})

describe('ユーザー名を入力せずにリクエスト送信', () => {
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(RegisterUser)
    })

    it('ユーザー名の入力を求めるメッセージを表示する', async () => {
        const usernameInput = wrapper.find('[data-testid="username"]');
        // ユーザー名の入力が空であることを確認
        expect(usernameInput.element.value).toBe("");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // ユーザー名の入力を求めるメッセージを表示されることを確認
        expect(usernameInput.element.validity.valid).toBe(false);
        expect(usernameInput.element.validity.valueMissing).toBe(true);
    })
})

describe('パスワード検証', () => {
    let wrapper;

    beforeEach(() => {
        vi.clearAllMocks()
        wrapper = mountComponent(RegisterUser)
    })

    it('パスワードが入力されていない場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        // パスワードの入力が空であることを確認
        expect(passwordInput.element.value).toBe("");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // パスワードの入力を求めるメッセージを表示されることを確認
        expect(passwordInput.element.validity.valid).toBe(false);
        expect(passwordInput.element.validity.valueMissing).toBe(true);
    })

    it('確認用パスワードが入力されていない場合', async () => {
        const passwordCheckInput = wrapper.find('[data-testid="passwordCheck"]');
        // 確認用パスワードの入力が空であることを確認
        expect(passwordCheckInput.element.value).toBe("");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 確認用パスワードの入力を求めるメッセージを表示されることを確認
        expect(passwordCheckInput.element.validity.valid).toBe(false);
        expect(passwordCheckInput.element.validity.valueMissing).toBe(true);
    })

    it('大文字が含まれていない場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        await passwordInput.setValue("test1234");
        // パスワードの入力が大文字を含まないことを確認
        expect(passwordInput.element.value).toBe("test1234");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 大文字を含むパスワードを求めるメッセージが表示されることを確認
        expect(wrapper.vm.isValidPassword.valid).toBe(false);
        expect(wrapper.vm.isValidPassword.message).toBe("大文字が含まれていません")
    })

    it('小文字が含まれていない場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        await passwordInput.setValue("TEST1234");
        // パスワードの入力が小文字を含まないことを確認
        expect(passwordInput.element.value).toBe("TEST1234");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 小文字を含むパスワードを求めるメッセージが表示されることを確認
        expect(wrapper.vm.isValidPassword.valid).toBe(false);
        expect(wrapper.vm.isValidPassword.message).toBe("小文字が含まれていません")
    })

    it('数字が含まれていない場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        await passwordInput.setValue("Testtest");
        // パスワードの入力が数字を含まないことを確認
        expect(passwordInput.element.value).toBe("Testtest");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 数字を含むパスワードを求めるメッセージが表示されることを確認
        expect(wrapper.vm.isValidPassword.valid).toBe(false);
        expect(wrapper.vm.isValidPassword.message).toBe("数字が含まれていません")
    })

    it('記号が含まれていない場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        await passwordInput.setValue("Test1234");
        // パスワードの入力が記号を含まないことを確認
        expect(passwordInput.element.value).toBe("Test1234");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 記号を含むパスワードを求めるメッセージが表示されることを確認
        expect(wrapper.vm.isValidPassword.valid).toBe(false);
        expect(wrapper.vm.isValidPassword.message).toBe("記号が含まれていません")
    })

    it('パスワードが8文字未満の場合', async () => {
        const passwordInput = wrapper.find('[data-testid="password"]');
        await passwordInput.setValue("Test123");
        // パスワードの入力が8文字未満であることを確認
        expect(passwordInput.element.value).toBe("Test123");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // 8文字以上のパスワードを求めるメッセージが表示されることを確認
        expect(wrapper.vm.isValidPassword.valid).toBe(false);
        expect(wrapper.vm.isValidPassword.message).toBe("パスワードは8文字以上16文字以下にして下さい")
    })

    it('2つのパスワードが一致しない場合', async () => {
        const usernameInput = wrapper.find('[data-testid="username"]');
        const passwordInput = wrapper.find('[data-testid="password"]');
        const passwordCheckInput = wrapper.find('[data-testid="passwordCheck"]');
        await usernameInput.setValue("testuser");
        await passwordInput.setValue("Test1234!");
        await passwordCheckInput.setValue("Test12345");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // パスワードが一致しないことを確認
        expect(wrapper.vm.isEqualPassword).toBe(false);
    })
})

describe('メールアドレスの検証', () => {
    let wrapper;

    beforeEach(async () => {
        wrapper = mountComponent(RegisterUser);
    })

    it('メールアドレスに@が含まれていない場合', async () => {
        const emailInput = wrapper.find('[data-testid="email"]');
        await emailInput.setValue("testuser.com");
        // メールアドレスの入力が@を含まないことを確認
        expect(emailInput.element.value).toBe("testuser.com");
        await wrapper.find('[data-testid="register-user-button"]').trigger('submit');
        // @を含むメールアドレスを求めるメッセージが表示されることを確認
        expect(emailInput.element.validity.valid).toBe(false);
        expect(emailInput.element.validity.typeMismatch).toBe(true);
    })
})