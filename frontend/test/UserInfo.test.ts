import { describe, it, expect, vi, beforeEach } from 'vitest'
import UserInfo from '@/views/UserInfo.vue'
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post)
const mockedPut = vi.mocked(apiClient.put)

describe('パスワード変更フォームの動作確認', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
    }
    );

    it('パスワード変更のチェックボックスの操作', async () => {
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        // デフォルトではパスワード変更フォームに入力できない
        expect(checkBox.element.checked).toBe(false);
        // チェックを入れて入力できるようにする
        await checkBox.setValue(true);
        expect(checkBox.element.checked).toBe(true);
    });

    it('現在のパスワード入力フォームに値が入力できる', async () => {
        // 初期状態では入力フォームに入力できない
        const oldPassForm = wrapper.find('[data-testid="oldPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(oldPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        await checkBox.setValue(true);
        expect(oldPassForm.element.disabled).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const oldPassword = "oldPassword";
        await oldPassForm.setValue(oldPassword);
        expect(oldPassForm.element.value).toEqual(oldPassword);
    });

    it('現在のパスワード入力フォームに値がないとリクエストを送信できない', async () => {
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const oldPassForm = wrapper.find('[data-testid="oldPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(oldPassForm.element.disabled).toBe(true);
        expect(oldPassForm.element.value).toBe("");

        // 値がないとリクエストを送信できないことを確認する
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');
        expect(mockedPut).toBeCalledTimes(0);
    });

    it('新しいパスワード(1回目)を入力フォームに値が入力できる', async () => {
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        await checkBox.setValue(true);
        expect(newPassForm.element.disabled).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newP@ssword1";
        await newPassForm.setValue(newPassword);
        expect(newPassForm.element.value).toEqual(newPassword);
    });

    it('新しいパスワード(1回目)を入力フォームに値が入力できない', async () => {
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);
        expect(newPassForm.element.value).toBe("");

        // 値がないとリクエストを送信できないことを確認する
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');
        expect(mockedPut).toBeCalledTimes(0);
    });

    it('新しいパスワード(確認用)を入力フォームで値を更新できる', async () => {
        // 初期状態では入力フォームに入力できない
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]') as DOMWrapper<HTMLInputElement>;
        expect(passCheckForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        await checkBox.setValue(true);
        expect(passCheckForm.element.disabled).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const newPasswordCheck = "newP@ssword1";
        await passCheckForm.setValue(newPasswordCheck);
        expect(passCheckForm.element.value).toEqual(newPasswordCheck);
    });

    it('新しいパスワード(確認用)を入力フォームに値が入力できない', async () => {
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]') as DOMWrapper<HTMLInputElement>;
        expect(passCheckForm.element.disabled).toBe(true);
        expect(passCheckForm.element.value).toBe("");

        // 値がないとリクエストを送信できないことを確認する
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');
        expect(mockedPut).toBeCalledTimes(0);
    });
});

describe('パスワードのバリデーション', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
    }
    );

    it('新しいパスワード(1回目)に大文字が含まれないパスワードを入力', async () => {
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setValue(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newp@ssword";
        await newPassForm.setValue(newPassword);
        expect(newPassForm.element.value).toEqual(newPassword);

        // バリデーションに通らないことの確認
        const passValidateMessage = wrapper.get("[data-testid='pass-validate-message']") as DOMWrapper<HTMLDivElement>;
        expect(passValidateMessage.text()).toContain("大文字が含まれていません");
        const validPassword = wrapper.get("[data-testid='valid-password']") as DOMWrapper<HTMLDivElement>;
        expect(validPassword.classes()).not.toContain('d-block'); // validの場合のコンポーネントが見つからないことを確認
    });

    it('新しいパスワード(1回目)に小文字が含まれないパスワードを入力', async () => {
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setValue(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "NEWPASSWORD";
        await newPassForm.setValue(newPassword);
        expect(newPassForm.element.value).toEqual(newPassword);

        // バリデーションに通らないことの確認
        const passValidateMessage = wrapper.get("[data-testid='pass-validate-message']") as DOMWrapper<HTMLDivElement>;
        expect(passValidateMessage.text()).toContain("小文字が含まれていません");
        const validPassword = wrapper.get("[data-testid='valid-password']") as DOMWrapper<HTMLDivElement>;
        expect(validPassword.classes()).not.toContain('d-block'); // validの場合のコンポーネントが見つからないことを確認
    });

    it('新しいパスワード(1回目)に数字が含まれないパスワードを入力', async () => {
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setValue(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newP@ssword";
        await newPassForm.setValue(newPassword);
        expect(newPassForm.element.value).toEqual(newPassword);

        // バリデーションに通らないことの確認
        const passValidateMessage = wrapper.get("[data-testid='pass-validate-message']") as DOMWrapper<HTMLDivElement>;
        expect(passValidateMessage.text()).toContain("数字が含まれていません");
        const validPassword = wrapper.get("[data-testid='valid-password']") as DOMWrapper<HTMLDivElement>;
        expect(validPassword.classes()).not.toContain('d-block'); // validの場合のコンポーネントが見つからないことを確認
    });

    it('新しいパスワード(1回目)に記号が含まれないパスワードを入力', async () => {
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        expect(newPassForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        await checkBox.setValue(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newPassword1";
        await newPassForm.setValue(newPassword);
        expect(newPassForm.element.value).toEqual(newPassword);

        // バリデーションに通らないことの確認
        const passValidateMessage = wrapper.get("[data-testid='pass-validate-message']") as DOMWrapper<HTMLDivElement>;
        expect(passValidateMessage.text()).toContain("記号が含まれていません");
        const validPassword = wrapper.get("[data-testid='valid-password']") as DOMWrapper<HTMLDivElement>;
        expect(validPassword.classes()).not.toContain('d-block'); // validの場合のコンポーネントが見つからないことを確認
    });

    it('1回目に入力したパスワードと確認用パスワードが一致しない', async () => {
        // 初期状態では入力フォームに入力できない
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]') as DOMWrapper<HTMLInputElement>;
        expect(passCheckForm.element.disabled).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]') as DOMWrapper<HTMLInputElement>;
        await checkBox.setValue(true);

        // 新しいパスワードを入力
        const newPassForm = wrapper.find('[data-testid="newPassword"]') as DOMWrapper<HTMLInputElement>;
        const newPassword = "newP@ssword1";
        await newPassForm.setValue(newPassword);

        // 確認用パスワードを入力
        const newPasswordCheck = "newP@sswordCheck";
        await passCheckForm.setValue(newPasswordCheck);

        // バリデーションに通らないことの確認
        const passEqualInvalid = wrapper.get("[data-testid='pass-equal-invalid']") as DOMWrapper<HTMLDivElement>;
        expect(passEqualInvalid.text()).toContain("パスワードが一致しません");
        const passEqualValid = wrapper.get("[data-testid='pass-equal-valid']") as DOMWrapper<HTMLDivElement>;
        expect(passEqualValid.classes()).not.toContain('d-block'); // validの場合のコンポーネントが見つからないことを確認
    });
})

describe('パスワード変更リクエストを送信', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
    }
    );

    it('パスワードを変更リクエストを送信', async () => {
        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setValue(true);

        // 現在のパスワード
        const oldPassForm = wrapper.find('[data-testid="oldPassword"]');
        const oldPassword = "oldPassword";
        await oldPassForm.setValue(oldPassword);

        // 新しいパスワード
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        const newPassword = "newP@ssword1";
        await newPassForm.setValue(newPassword);

        // パスワード確認
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
        const newPasswordCheck = "newP@ssword1";
        await passCheckForm.setValue(newPasswordCheck);

        const expectedMessage = "パスワードの変更に成功しました"
        mockedPut.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage
            }
        });
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');

        // 更新リクエストが正しく行われたことを確認
        expect(mockedPut).toBeCalledWith(
            "password",  // 正しいURL
            {
                old_password: oldPassword,    // 正しいパラメータ
                new_password: newPassword
            }
        );
        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    });

    it('必須項目を入力しないとリクエストを送信できない', async () => {
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');
        expect(mockedPost).toBeCalledTimes(0);
    })
});