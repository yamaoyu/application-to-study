import { describe, it, expect, vi, beforeEach } from 'vitest';
import showInquiry from '@/views/showInquiry.vue';
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('データあり', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(showInquiry);
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

        axios.get.mockResolvedValue({
            status: 200,
            data: inquiries
        });

        await wrapper.vm.getInquiries();
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "inquiries",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
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
        wrapper = mountComponent(showInquiry);
        }
    );

    it('データがないためメッセージが表示される', async () =>{
        const expectedMessage = "問い合わせはありません";
        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.getInquiries();
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "inquiries",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    });
});

describe('権限なし', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(showInquiry);
        }
    );

    it('権限がないためメッセージが表示される', async () =>{
        const expectedMessage = "管理者権限を持つユーザー以外はアクセスできません";
        axios.get.mockRejectedValue({
            response: {
                status: 403,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.getInquiries();
        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + "inquiries",
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    });
});