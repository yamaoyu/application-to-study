import { describe, it, expect, vi, beforeEach } from 'vitest'
import InquiryForm from '@/views/InquiryForm.vue'
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post);

describe('問い合わせに成功する', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('問い合わせを送信する', async () => {
        const category = "要望";
        const detail = "テスト";
        const message = "問い合わせを受け付けました"

        mockedPost.mockResolvedValue({
            status: 200,
            data: {
                category: category,
                detail: detail,
                message: message
            }
        })
        // カテゴリを選択し、カテゴリが要望になっていることを確認する
        const requestRadio = wrapper.find('[data-testid="request"]') as DOMWrapper<HTMLInputElement>;
        await requestRadio.setValue(true);
        expect(requestRadio.element.checked).toBe(true);
        // 詳細を入力し、詳細が入力されていることを確認する
        const detailInput = wrapper.find('[data-testid="detail"]') as DOMWrapper<HTMLInputElement>;
        await detailInput.setValue(detail);
        expect(detailInput.element.value).toBe(detail);
        // 送信ボタンをクリックし、正しくリクエストが送信されることを確認する
        await wrapper.find('[data-testid="submit-button"]').trigger('submit');
        expect(mockedPost).toHaveBeenCalledTimes(1);
        expect(mockedPost).toHaveBeenCalledWith(
            'inquiries',
            {
                category: category,
                detail: detail
            }
        )
    })
})

describe('問い合わせに失敗する', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('カテゴリを選択しないで送信した場合', async () => {
        const detail = "テスト";
        const message = "カテゴリは要望・エラー報告・その他から選択してください";

        mockedPost.mockRejectedValue({
            response: {
                status: 422,
                data: { detail: message }
            }
        })

        // 詳細を入力し、詳細が入力されていることを確認する
        const detailInput = wrapper.find('[data-testid="detail"]') as DOMWrapper<HTMLInputElement>;
        await detailInput.setValue(detail);
        expect(detailInput.element.value).toBe(detail);
        // 送信ボタンをクリックし、正しくリクエストが送信されることを確認する
        await wrapper.find('[data-testid="submit-button"]').trigger('submit');
        expect(mockedPost).toHaveBeenCalledTimes(1);
        expect(mockedPost).toHaveBeenCalledWith(
            'inquiries',
            {
                category: "",
                detail: detail
            }
        )
        // エラーメッセージが表示されることを確認する
        expect(wrapper.find('[data-testid="message"]').element.textContent).toBe(message)
    })
})

describe('カテゴリ選択の動作確認', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() // 呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(InquiryForm)
    })

    it('カテゴリの選択を切り替える', async () => {
        // 初期はカテゴリが空であることを確認
        const requestRadio = wrapper.find('[data-testid="request"]') as DOMWrapper<HTMLInputElement>;
        const errorRadio = wrapper.find('[data-testid="error"]') as DOMWrapper<HTMLInputElement>;
        const otherRadio = wrapper.find('[data-testid="other"]') as DOMWrapper<HTMLInputElement>;
        expect(requestRadio.element.checked).toBe(false);
        expect(errorRadio.element.checked).toBe(false);
        expect(otherRadio.element.checked).toBe(false);
        // 要望を選択し、カテゴリが要望になっていることを確認
        await requestRadio.setValue(true);
        expect(requestRadio.element.checked).toBe(true);
        // エラーを選択し、カテゴリがエラーになっており前の値(要望)ではなくなっていることを確認
        await errorRadio.setValue(true);
        expect(errorRadio.element.checked).toBe(true);
        expect(requestRadio.element.checked).toBe(false);
        // その他を選択し、カテゴリがその他になっており前の値(エラー)ではなくなっていることを確認
        await otherRadio.setValue(true);
        expect(otherRadio.element.checked).toBe(true);
        expect(errorRadio.element.checked).toBe(false);
    })
})