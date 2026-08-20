import { describe, it, expect, vi, beforeEach } from 'vitest';
import TargetTab from '@/views/TargetTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post)

describe('目標時間の登録(一括)', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(TargetTab, {});
    }
    );

    it('フォームの操作', async () => {
        // 追加
        wrapper.find("[data-testid='increase-target-row']").trigger("click");
        await flushPromises(); // html要素が変わるため変更を待つ
        const rows = wrapper.findAll('[data-testid="target-row"]');
        expect(rows).toHaveLength(2);
        // 減らす
        wrapper.find("[data-testid='decrease-target-row-1']").trigger("click");
        await flushPromises();
        const newRows = wrapper.findAll('[data-testid="target-row"]');
        expect(newRows).toHaveLength(1);
        // 値の入力
        const dateField = wrapper.find("[data-testid='target-date-row-0']") as DOMWrapper<HTMLInputElement>;
        await dateField.setValue("2025-01-01");
        expect(dateField.element.value).toEqual("2025-01-01");
        const timeField = wrapper.find("[data-testid='target-time-row-0']") as DOMWrapper<HTMLInputElement>;
        await timeField.setValue(3);
        expect(timeField.element.value).toEqual("3");
    });

    it('成功', async () => {
        const insertDate = "2025-01-01";
        const insertTime = 3;

        const dateField = wrapper.find("[data-testid='target-date-row-0']") as DOMWrapper<HTMLInputElement>;
        await dateField.setValue(insertDate);
        const timeField = wrapper.find("[data-testid='target-time-row-0']") as DOMWrapper<HTMLInputElement>;
        await timeField.setValue(insertTime);
        await flushPromises();

        mockedPost.mockResolvedValue({
            status: 200,
            data: {
                success_count: 1,
                error_count: 0,
                results: [
                    { result: "success", date: "2025/1/1", target_time: insertTime }
                ]
            }
        });

        await wrapper.find("[data-testid='submit-multi-target']").trigger("click");
        await flushPromises();

        // モーダルのOKボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPost).toBeCalledWith(
            `activities/bulk-create-targets`,
            {
                activities: [
                    {
                        date: insertDate,
                        target_time: insertTime
                    }
                ]
            }
        );
        const expectedMessage = "【目標時間登録】登録1件、エラー0件\n2025/1/1の目標時間を3時間に登録しました";
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    });

    it('失敗', async () => {
        const insertData = [{ "date": "2025-01-01", "target_time": 3 }, { "date": "2025-02-01", "target_time": 4 }];

        await wrapper.find("[data-testid='increase-target-row']").trigger("click");
        await flushPromises();

        for (let i = 0; i < insertData.length; i++) {
            const { date, target_time } = insertData[i];
            const dateField = wrapper.find(`[data-testid='target-date-row-${i}']`) as DOMWrapper<HTMLInputElement>;
            await dateField.setValue(date);
            const timeField = wrapper.find(`[data-testid='target-time-row-${i}']`) as DOMWrapper<HTMLInputElement>;
            await timeField.setValue(target_time);
            await flushPromises();
        }

        mockedPost.mockResolvedValue({
            status: 201,
            data: {
                success_count: 0,
                error_count: 2,
                results: [
                    { result: "error", date: "2025/1/1", reason: "TARGET_TIME_ALREADY_REGISTERED" },
                    { result: "error", date: "2025/2/1", reason: "SALARY_NOT_FOUND" }
                ]
            }
        });

        await wrapper.find("[data-testid='submit-multi-target']").trigger("click");
        await flushPromises();

        // モーダルのOKボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPost).toBeCalledWith(
            `activities/bulk-create-targets`,
            {
                activities: insertData
            }
        );
        const expectedMessage = "【目標時間登録】登録0件、エラー2件\n2025/1/1の目標時間登録に失敗: 既に登録されています\n2025/2/1の目標時間登録に失敗: 月収が登録されていません";
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    });
});
