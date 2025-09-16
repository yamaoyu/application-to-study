import { describe, it, expect, vi, beforeEach } from 'vitest'
import UserInfo from '@/views/UserInfo.vue'
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('パスワード変更フォームの動作確認', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
        }
    );

    it('パスワード変更のチェックボックスの操作', async() =>{
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        // デフォルトではパスワード変更フォームに入力できない
        expect(wrapper.vm.isPasswordChangeEnabled).toBe(false);
        // チェックを入れて入力できるようにする
        await checkBox.setChecked(true);
        expect(wrapper.vm.isPasswordChangeEnabled).toBe(true);
    });

    it('現在のパスワード入力フォームに値が入力できる', async() =>{
        // 初期状態では入力フォームに入力できない
        const oldPassForm = wrapper.find('[data-testid="oldPassword"]');
        expect(oldPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);
        expect(oldPassForm.isDisabled()).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const oldPassword = "oldPassword";
        oldPassForm.setValue(oldPassword);
        expect(wrapper.vm.oldPassword).toEqual(oldPassword);
    });

    it('現在のパスワード入力フォームに値が入力できない', async() =>{
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const oldPassForm = wrapper.find('[data-testid="oldPassword"]');
        expect(oldPassForm.isDisabled()).toBe(true);

        // 値を入力しても値が更新されないことを確認する
        const oldPassword = "oldPassword";
        await oldPassForm.setValue(oldPassword);
        expect(wrapper.vm.oldPassword).not.toBe(oldPassword);
    });

    it('新しいパスワード(1回目)を入力フォームに値が入力できる', async() =>{
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);
        expect(newPassForm.isDisabled()).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newP@ssword1";
        newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).toEqual(newPassword);
    });

    it('新しいパスワード(1回目)を入力フォームに値が入力できない', async() =>{
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // 値を入力しても値が更新されないことを確認する
        const newPassword = "newPassword";
        await newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).not.toBe(newPassword);
    });

    it('新しいパスワード(確認用)を入力フォームで値を更新できる', async() =>{
        // 初期状態では入力フォームに入力できない
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
        expect(passCheckForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);
        expect(passCheckForm.isDisabled()).toBe(false);

        // 値を入力して、値が更新されることを確認する
        const newPasswordCheck = "newP@ssword1";
        passCheckForm.setValue(newPasswordCheck);
        expect(wrapper.vm.newPasswordCheck).toEqual(newPasswordCheck);
    });

    it('新しいパスワード(確認用)を入力フォームに値が入力できない', async() =>{
        // パスワードを変更するにチェックを入れず、入力できないことを確認する
        const passCheckForm = wrapper.find('[data-testid="newPassword"]');
        expect(passCheckForm.isDisabled()).toBe(true);

        // 値を入力しても値が更新されないことを確認する
        const newPassword = "newPassword";
        await passCheckForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).not.toBe(newPassword);
    });
});

describe('パスワードのバリデーション', async()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
        }
    );

    it('新しいパスワード(1回目)に大文字が含まれないパスワードを入力', async() =>{
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newp@ssword";
        newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).toEqual(newPassword);

        // バリデーションに通らないことの確認
        expect(wrapper.vm.isValidPassword).toEqual(
            {
                "message": "大文字が含まれていません",
                "valid": false,
            }
        );
    });

    it('新しいパスワード(1回目)に小文字が含まれないパスワードを入力', async() =>{
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "NEWPASSWORD";
        newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).toEqual(newPassword);

        // バリデーションに通らないことの確認
        expect(wrapper.vm.isValidPassword).toEqual(
            {
                "message": "小文字が含まれていません",
                "valid": false,
            }
        );
    });

    it('新しいパスワード(1回目)に数字が含まれないパスワードを入力', async() =>{
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newP@ssword";
        newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).toEqual(newPassword);

        // バリデーションに通らないことの確認
        expect(wrapper.vm.isValidPassword).toEqual(
            {
                "message": "数字が含まれていません",
                "valid": false,
            }
        );
    });

    it('新しいパスワード(1回目)に記号が含まれないパスワードを入力', async() =>{
        // 初期状態では入力フォームに入力できない
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        expect(newPassForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

        // 値を入力して、値が更新されることを確認する
        const newPassword = "newPassword1";
        newPassForm.setValue(newPassword);
        expect(wrapper.vm.newPassword).toEqual(newPassword);

        // バリデーションに通らないことの確認
        expect(wrapper.vm.isValidPassword).toEqual(
            {
                "message": "記号が含まれていません",
                "valid": false,
            }
        );
    });

    it('1回目に入力したパスワードと確認用パスワードが一致しない', async() =>{
        // 初期状態では入力フォームに入力できない
        const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
        expect(passCheckForm.isDisabled()).toBe(true);

        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

        // 新しいパスワードを入力
        const newPassForm = wrapper.find('[data-testid="newPassword"]');
        const newPassword = "newP@ssword1";
        newPassForm.setValue(newPassword);

        // 確認用パスワードを入力
        const newPasswordCheck = "newP@sswordCheck";
        passCheckForm.setValue(newPasswordCheck);

        // バリデーションに通らないことの確認
        expect(wrapper.vm.isEqualPassword).toBe(false);
    });
})

describe('パスワード変更リクエストを送信', async()=>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(UserInfo);
        }
    );

    it('パスワードを変更リクエストを送信', async() =>{
        // パスワードを変更するにチェックを入れ、入力できるようにする
        const checkBox = wrapper.find('[data-testid="isPasswordChangeEnabled"]');
        await checkBox.setChecked(true);

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
        axios.put.mockResolvedValue({
            status: 200,
            data: {
                message: expectedMessage
            }
        });
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');

        // 更新リクエストが正しく行われたことを確認
        expect(axios.put).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "password",  // 正しいURL
            {
                old_password: oldPassword,    // 正しいパラメータ
                new_password: newPassword
            },
            {
                headers: {
                    Authorization: "登録なし",
                }
            },
        );
        expect(wrapper.vm.message).toEqual(expectedMessage);
    });

    it('必須項目を入力しないとリクエストを送信できない', async() =>{
        await wrapper.find('[data-testid="password-change-button"]').trigger('submit');
        expect(axios.post).toBeCalledTimes(0);
    })
});