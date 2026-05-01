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
        // タブの切り替え    
        const expectedMessage = "2025/1/1の目標時間を3時間に登録しました\n2025/1/2の目標時間を3.5時間に登録しました";

        const insertDate = "2025-01-01";
        const insertTime = 3;

        const dateField = wrapper.find("[data-testid='target-date-row-0']") as DOMWrapper<HTMLInputElement>;
        await dateField.setValue(insertDate);
        const timeField = wrapper.find("[data-testid='target-time-row-0']") as DOMWrapper<HTMLInputElement>;
        await timeField.setValue(insertTime);
        await flushPromises();

        mockedPost.mockResolvedValue({
            status: 201,
            data: { message: expectedMessage }
        });

        await wrapper.find("[data-testid='submit-multi-target']").trigger("click");
        await flushPromises();

        // モーダルのOKボタンをクリック
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPost).toBeCalledWith(
            `activities/multi/target`,
            {
                activities: [
                    {
                        date: insertDate,
                        target_time: insertTime
                    }
                ]
            }
        );
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    });
});
