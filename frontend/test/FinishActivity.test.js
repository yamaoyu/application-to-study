import { describe, it, expect, vi, beforeEach } from 'vitest';
import FinishTab from '@/views/FinishTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

describe('活動の終了(一括)', () => {
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    const pendingActivities = [
      {
        date: "2025/1/1",
        target_time: 3,
        actual_time: 3,
        status: "success"
      },
      {
        date: "2025/1/2",
        target_time: 3.5,
        actual_time: 3.5,
        status: "pending"
      }
    ];
    wrapper = mountComponent(FinishTab, {
      props: {
        pendingActivities: pendingActivities
      }
    });
    }
  );

  it('フォームの操作', async() =>{
    // 初期値
    expect(wrapper.vm.selectedActivities.length).toBe(0);
    // 選択
    wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
    expect(wrapper.vm.selectedActivities.length).toBe(1);
    // 解除
    wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
    expect(wrapper.vm.selectedActivities.length).toBe(0);
  })

  it("全てを選択/解除", async() =>{
    // 初期値確認
    expect(wrapper.vm.selectedActivities).toEqual([]);
    // 全て選択
    wrapper.find("[data-testid='toggle-all-activities']").trigger("click");
    expect(wrapper.vm.selectedActivities).toEqual(wrapper.props().pendingActivities);
    // 全て解除
    wrapper.find("[data-testid='toggle-all-activities']").trigger("click");
    expect(wrapper.vm.selectedActivities).toEqual([]);
  })


  it('成功', async() =>{
    // 数値は仮のもの
    const selectedActivities = [
      {
        date: "2025/1/1",
        target_time: 3,
        actual_time: 3,
        status: "pending"
      },
      {
        date: "2025/1/2",
        target_time: 3.5,
        actual_time: 3.5,
        status: "pending"
      }
    ];
    wrapper.vm.selectedActivities = selectedActivities;
    const originalMessage = "ボーナス：0.5万円(5000円)\nペナルティ：0.2万円(2000円)\n2025/1/1の活動を終了:ボーナス0.5万円(5000円)\n2025/1/2の活動を終了ペナルティ0.2万円(2000円)";
    const payAdjustment = "0.3万円(3000円)";
    const expectedDates = [
      "2025/1/1", "2025/1/2"
    ];
    apiClient.put.mockResolvedValue({
      status: 200,
      data: { 
        message: originalMessage,
        pay_adjustment: payAdjustment
      }
    });

    await wrapper.vm.onSubmit();
    expect(apiClient.put).toBeCalledWith(
      `activities/multi/finish`,
      {
        dates: expectedDates
      }
    );
    const expectedMessage = "ボーナス-ペナルティ：0.3万円(3000円)\n" + originalMessage;
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })
});
