import { describe, it, expect, vi, beforeEach } from 'vitest';
import FinishTab from '@/views/FinishTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedPut = vi.mocked(apiClient.put);

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
    const originalMessage = "ボーナス：0.5万円(5000円)\nペナルティ：0.2万円(2000円)\n2025/1/1の活動を終了:ボーナス0.5万円(5000円)\n2025/1/2の活動を終了ペナルティ0.2万円(2000円)";
    const payAdjustment = "0.3万円(3000円)";
    const expectedDates = [
      "2025/1/1", "2025/1/2"
    ];
    mockedPut.mockResolvedValue({
      status: 200,
      data: {
        message: originalMessage,
        pay_adjustment: payAdjustment
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
      `activities/multi/finish`,
      {
        dates: expectedDates
      }
    );
    const expectedMessage = "ボーナス-ペナルティ：0.3万円(3000円)\n" + originalMessage;
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })
});
