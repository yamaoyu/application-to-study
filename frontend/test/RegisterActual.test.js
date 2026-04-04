import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActualTab from '@/views/ActualTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

describe('実績時間の登録(一括)', () => {
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
    wrapper = mountComponent(ActualTab, {
      props: {
        pendingActivities: pendingActivities
      }
    });
  });

  it('フォームの操作', async() =>{
    wrapper.vm.editActivities  = [
      {
        date: "2025/1/1",
        target_time: 3,
        actual_time: 0,
        status: "success"
      }
    ];
    // 初期値
    expect(wrapper.vm.selectedActivities.length).toBe(0);
    // 選択
    wrapper.find("[data-testid='is-selected-actual-0']").trigger("click");
    expect(wrapper.vm.selectedActivities.length).toBe(1);
    // 解除
    wrapper.find("[data-testid='is-selected-actual-0']").trigger("click");
    expect(wrapper.vm.selectedActivities.length).toBe(0);
    // 実績入力
    const timeField = wrapper.find("[data-testid='actual-time-row-0']");
    await timeField.setValue(3);
    expect(timeField.element.value).toEqual("3");
  });

  it("全てを選択/解除", async() =>{
    // 初期設定
    const editActivities = [
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
    wrapper.vm.pendingActivities = editActivities;
    expect(wrapper.vm.selectedActivities).toEqual([]);
    // 全て選択をクリック
    wrapper.find("[data-testid='select-all-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    expect(wrapper.vm.selectedActivities).toEqual(editActivities);
    // 選択を解除
    wrapper.find("[data-testid='reset-selected-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    expect(wrapper.vm.selectedActivities).toEqual([]);
  });

  it("変更分全てを選択/解除", async() =>{
    // 選択ボタンをクリックできないことを確認(変更がないため選択対象なし)
    const submitButton = wrapper.find("[data-testid='select-edited-activities']");
    expect(submitButton.attributes("disabled"));
    // 変更してから再度選択
    const timeField = wrapper.find("[data-testid='actual-time-row-0']");
    const newValue = "5";
    await timeField.setValue(newValue);
    expect(timeField.element.value).toEqual(newValue);
    expect(submitButton.attributes("disabled")).toBeUndefined(); // disabled属性がなくなっていることを確認
    // 変更を元に戻す
    wrapper.find("[data-testid='reset-edited-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    expect(timeField.element.value).toEqual("3");
    expect(wrapper.vm.selectedActivities).toEqual([]);
  })

  it('成功', async() =>{
      const expectedMessage = "2025/1/1の活動時間を3時間に登録しました\n2025/1/2の活動時間を3.5時間に登録しました";

      const selectedActivities = [
        {
          date: "2025/1/1",
          actual_time: 3
        },
        {
          date: "2025/1/2",
          actual_time: 3.5
        }
      ];
      wrapper.vm.selectedActivities = selectedActivities;

      apiClient.put.mockResolvedValue({
        status: 200,
        data: { message: expectedMessage }
      });

      await wrapper.vm.onSubmit();

      expect(apiClient.put).toBeCalledWith(
        `activities/multi/actual`,
        {
          activities: selectedActivities
        }
      );
      expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })
});