import { describe, it, expect, vi, beforeEach } from 'vitest';
import FinishTab from '@/views/FinishTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedPut = vi.mocked(apiClient.patch);

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
  },
  {
    date: "2025/1/3",
    target_time: 3,
    actual_time: 0,
    status: "pending"
  }
];

describe('活動の終了(一括)', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(FinishTab, {
      props: {
        pendingActivities: pendingActivities
      }
    });
  }
  );

  it('フォームの操作', async () => {
    // 初期値
    const defaultCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const defaultCheckedCount = defaultCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;
    expect(defaultCheckedCount).toBe(0);
    // 選択
    await wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
    const checkboxes = wrapper.findAll('input[type="checkbox"]');
    const checkedCount = checkboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(checkedCount).toBe(1);
    // 解除
    await wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
    const newCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const newCheckedCount = newCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(newCheckedCount).toBe(0);
  });

  it("全てを選択/解除", async () => {
    // 初期値
    const defaultCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const defaultCheckedCount = defaultCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;
    expect(defaultCheckedCount).toBe(0);
    // 選択
    await wrapper.find("[data-testid='select-all-activities']").trigger("click");
    const checkboxes = wrapper.findAll('input[type="checkbox"]');
    const checkedCount = checkboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(checkedCount).toBe(pendingActivities.length);
    // 解除
    await wrapper.find("[data-testid='select-all-activities']").trigger("click");
    const newCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const newCheckedCount = newCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(newCheckedCount).toBe(0);
  });


  it('成功', async () => {
    const payAdjustment = "0.3";
    const totalBonus = "0.5";
    const totalPenalty = "0.2";
    const expectedDates = [
      "2025/1/1", "2025/1/2", "2025/1/3"
    ];
    mockedPut.mockResolvedValue({
      status: 200,
      data: {
        success_count: 3,
        error_count: 0,
        pay_adjustment: payAdjustment,
        total_bonus: totalBonus,
        total_penalty: totalPenalty,
        results: [
          { "date": "2025/1/1", "result": "success", "status": "success", "bonus": 3, "penalty": 3 },
          { "date": "2025/1/2", "result": "success", "status": "success", "bonus": 3.5, "penalty": 3.5 },
          { "date": "2025/1/3", "result": "success", "status": "failure", "bonus": 0, "penalty": 3.0 }
        ]
      }
    });

    await wrapper.find("[data-testid='select-all-activities']").trigger("click");
    await flushPromises();

    await wrapper.find("[data-testid='finish-multi']").trigger("click");
    await flushPromises();

    // モーダルのOKボタンをクリック
    const bModal = wrapper.findComponent({ name: 'BModal' });
    await bModal.vm.$emit('ok');
    await flushPromises();

    expect(mockedPut).toBeCalledWith(
      `activities/bulk-finish`,
      {
        dates: expectedDates
      }
    );
    const expectedMessage = "【活動終了】終了済み3件、エラー0件\nボーナス-ペナルティ：0.3万円(3000円)\n" + "ボーナス：0.5万円(5000円)\nペナルティ：0.2万円(2000円)\n2025/1/1の活動を終了：ボーナス3万円(30000円)\n2025/1/2の活動を終了：ボーナス3.5万円(35000円)\n2025/1/3の活動を終了：ペナルティ3万円(30000円)";
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })

  it('失敗', async () => {
    const expectedDates = [
      "2025/1/1", "2025/1/2", "2025/1/3"
    ];
    mockedPut.mockResolvedValue({
      status: 200,
      data: {
        success_count: 0,
        error_count: 4,
        pay_adjustment: 0,
        total_bonus: 0,
        total_penalty: 0,
        results: [
          { "date": "2025/1/1", "result": "error", "reason": "ACTIVITY_NOT_FOUND", "status": null, "bonus": null, "penalty": null },
          { "date": "2025/1/2", "result": "error", "reason": "SALARY_NOT_FOUND", "status": null, "bonus": null, "penalty": null },
          { "date": "2025/1/3", "result": "error", "reason": "UNEXPECTED_ERROR", "status": null, "bonus": null, "penalty": null },
          { "date": "2025/1/4", "result": "error", "reason": "ACTIVITY_ALREADY_FINISHED", "status": null, "bonus": null, "penalty": null }
        ]
      }
    });

    await wrapper.find("[data-testid='select-all-activities']").trigger("click");
    await flushPromises();

    await wrapper.find("[data-testid='finish-multi']").trigger("click");
    await flushPromises();

    // モーダルのOKボタンをクリック
    const bModal = wrapper.findComponent({ name: 'BModal' });
    await bModal.vm.$emit('ok');
    await flushPromises();

    expect(mockedPut).toBeCalledWith(
      `activities/bulk-finish`,
      {
        dates: expectedDates
      }
    );
    const expectedMessage = [
      "【活動終了】終了済み0件、エラー4件",
      "ボーナス-ペナルティ：0万円(0円)",
      "ボーナス：0万円(0円)",
      "ペナルティ：0万円(0円)",
      "2025/1/1の活動終了に失敗: 活動が登録されていません",
      "2025/1/2の活動終了に失敗: 月収が登録されていません",
      "2025/1/3の活動終了に失敗: 予期せぬエラーが発生しました",
      "2025/1/4の活動終了に失敗: 既に確定されています"
    ];
    console.log(wrapper.find("[data-testid='reqMsg']").text())
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage.join("\n"));
  })
});
