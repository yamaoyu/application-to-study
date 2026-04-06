import { describe, it, expect, vi, beforeEach } from 'vitest';
import ShowInquiry from '@/views/ShowInquiry.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

describe('データあり', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        }
    );

    it('ページを開いて問い合わせ一覧が表示される', async () =>{
        const inquiries = [
            {
                "category": "要望",
                "detail": "新しい機能を追加",
                "is_checked": false,
                "date": "2025-01-01"
            }
        ]

        apiClient.get.mockResolvedValue({
            status: 200,
            data: inquiries
        });
        wrapper = mountComponent(ShowInquiry);

        await flushPromises();
        expect(apiClient.get).toBeCalledWith(
            "inquiries"
        );

        expect(wrapper.find("[data-testid='index-0']").text()).toBe("1");
        expect(wrapper.find("[data-testid='category-0']").text()).toEqual("要望");
        expect(wrapper.find("[data-testid='detail-0']").text()).toEqual("新しい機能を追加");
        expect(wrapper.find("[data-testid='date-0']").text()).toEqual("2025-01-01");
        expect(wrapper.find("[data-testid='is_checked-0']").text()).toEqual("未確認");
    });
});

describe('データなし', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        }
    );

    it('データがないためメッセージが表示される', async () =>{
        const expectedMessage = "問い合わせはありません";
        apiClient.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });
        wrapper = mountComponent(ShowInquiry);
        await flushPromises();

        expect(apiClient.get).toBeCalledWith(
            "inquiries"
        );

        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    });
});

describe('権限なし', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ShowInquiry);
        }
    );

    it('権限がないためメッセージが表示される', async () =>{
        const expectedMessage = "管理者権限を持つユーザー以外はアクセスできません";
        apiClient.get.mockRejectedValue({
            response: {
                status: 403,
                data: {
                    detail: expectedMessage
                }
            }
        });

        wrapper = mountComponent(ShowInquiry);
        await flushPromises();

        expect(apiClient.get).toBeCalledWith(
            "inquiries"
        );

        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    });
});
