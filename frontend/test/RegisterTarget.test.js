import { describe, it, expect, vi, beforeEach } from 'vitest';
import TargetTab from '@/views/TargetTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

describe('目標時間の登録(一括)', () => {
  let wrapper;

  beforeEach(() => {
      vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
      wrapper = mountComponent(TargetTab, {});
      }
  );

  it('フォームの操作', async() =>{
      // 追加
      wrapper.find("[data-testid='increase-target-row']").trigger("click");
      expect(wrapper.vm.targetActivities.length).toBe(2);
      await flushPromises(); // html要素が変わるため変更を待つ
      // 減らす
      wrapper.find("[data-testid='decrease-target-row-1']").trigger("click");
      expect(wrapper.vm.targetActivities.length).toBe(1);
      // 値の入力
      const dateField = wrapper.find("[data-testid='target-date-row-0']");
      await dateField.setValue("2025-01-01");
      expect(dateField.element.value).toEqual("2025-01-01");
      const timeField = wrapper.find("[data-testid='target-time-row-0']");
      await timeField.setValue(3);
      expect(timeField.element.value).toEqual("3");
  });

  it('成功', async() =>{
    // タブの切り替え    
    const expectedMessage = "2025/1/1の目標時間を3時間に登録しました\n2025/1/2の目標時間を3.5時間に登録しました";

    const targetActivities = [
        {
            date: "2025/1/1",
            target_time: 3
        },
        {
            date: "2025/1/2",
            target_time: 3.5
        }
    ];
    wrapper.vm.targetActivities = targetActivities;

    apiClient.post.mockResolvedValue({
        status: 201,
        data: { message: expectedMessage }
    });

    await wrapper.vm.onSubmit();

    expect(apiClient.post).toBeCalledWith(
        `activities/multi/target`,
        {
            activities: targetActivities
        }
    );
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })
});
