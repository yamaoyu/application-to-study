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
