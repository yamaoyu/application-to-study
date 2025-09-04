import { describe, it, expect, vi, beforeEach } from 'vitest'
import InquiryForm from '@/views/InquiryForm.vue'
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('問い合わせに成功する', async () =>{
    let wrapper;
    
    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('問い合わせを送信する', async () =>{
        const category = "要望";
        const detail = "テスト";
        const message = "問い合わせを受け付けました"

        axios.post.mockResolvedValue({
            status: 200,
            data: {
                category: category,
                detail: detail,
                message: message
            }
        })
        // カテゴリを選択し、カテゴリが要望になっていることを確認する
        await wrapper.find('[data-testid="request"]').setChecked(true);
        expect(wrapper.vm.category).toBe(category);
        // 詳細を入力し、詳細が入力されていることを確認する
        await wrapper.find('[data-testid="detail"]').setValue(detail);
        expect(wrapper.find('[data-testid="detail"]').element.value).toBe(detail);
        // 送信ボタンをクリックし、正しくリクエストが送信されることを確認する
        await wrapper.find('[data-testid="submit-button"]').trigger('submit');
        expect(axios.post).toHaveBeenCalledTimes(1);
        expect(axios.post).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + 'inquiries',
            {
                category: category,
                detail: detail
            },
            {
                headers: {
                    "Authorization": "登録なし"
                }
            }
        )
    })
})

describe('問い合わせに失敗する', async() =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('カテゴリを選択しないで送信した場合', async() =>{
        const detail = "テスト";
        const message = "カテゴリは要望・エラー報告・その他から選択してください";

        axios.post.mockRejectedValue({
            response :{
                status: 422,
                data: { detail : message }
            }
        })

        // 詳細を入力し、詳細が入力されていることを確認する
        await wrapper.find('[data-testid="detail"]').setValue(detail);
        expect(wrapper.find('[data-testid="detail"]').element.value).toBe(detail);
        // 送信ボタンをクリックし、正しくリクエストが送信されることを確認する
        await wrapper.find('[data-testid="submit-button"]').trigger('submit');
        expect(axios.post).toHaveBeenCalledTimes(1);
        expect(axios.post).toHaveBeenCalledWith(
            process.env.VUE_APP_BACKEND_URL + 'inquiries',
            {
                category: "",
                detail: detail
            },
            {
                headers: {
                    "Authorization": "登録なし"
                }
            }
        )
        // エラーメッセージが表示されることを確認する
        expect(wrapper.find('[data-testid="message"]').element.textContent).toBe(message)
    })
})

describe('カテゴリ選択の動作確認', async() =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('カテゴリの選択を切り替える', async () => {
        // 初期はカテゴリが空であることを確認
        expect(wrapper.vm.category).toBe("");
        // 要望を選択し、カテゴリが要望になっていることを確認
        await wrapper.find('[data-testid="request"]').setChecked(true);
        expect(wrapper.vm.category).toBe("要望");
        // エラーを選択し、カテゴリがエラーになっており前の値(要望)ではなくなっていることを確認
        await wrapper.find('[data-testid="error"]').setChecked(true);
        expect(wrapper.vm.category).toBe("エラー報告");
        expect(wrapper.find('[data-testid="request"]').element.checked).toBe(false);
        // その他を選択し、カテゴリがその他になっており前の値(エラー)ではなくなっていることを確認
        await wrapper.find('[data-testid="other"]').setChecked(true);
        expect(wrapper.vm.category).toBe("その他");
        expect(wrapper.find('[data-testid="error"]').element.checked).toBe(false);
    })
})