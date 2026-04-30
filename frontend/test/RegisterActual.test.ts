import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActualTab from '@/views/ActualTab.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper, DOMWrapper } from '@vue/test-utils';

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

describe('実績時間の登録(一括)', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す

    wrapper = mountComponent(ActualTab, {
      props: {
        pendingActivities: pendingActivities
      }
    });
  });

  it('フォームの操作', async () => {
    const firstRow = wrapper.find("[data-testid='is-selected-actual-0']");
    const firstCheckbox = firstRow.find("input");
    const submitButton = wrapper.find("[data-testid='submit-multi-actual']");
    const resetButton = wrapper.find("[data-testid='reset-selected-activities']");
    const row = wrapper.findAll("tbody tr")[0];

    // 初期状態
    expect((firstCheckbox.element as HTMLInputElement).checked).toBe(false);
    expect(row.classes()).not.toContain("table-active");
    expect(submitButton.attributes("disabled")).toBeDefined();
    expect(resetButton.attributes("disabled")).toBeDefined();

    // 選択
    await firstRow.trigger("click");
    expect((firstCheckbox.element as HTMLInputElement).checked).toBe(true);
    expect(row.classes()).toContain("table-active");
    expect(submitButton.attributes("disabled")).toBeUndefined();
    expect(resetButton.attributes("disabled")).toBeUndefined();

    // 解除
    await firstRow.trigger("click");
    expect((firstCheckbox.element as HTMLInputElement).checked).toBe(false);
    expect(row.classes()).not.toContain("table-active");
    expect(submitButton.attributes("disabled")).toBeDefined();
    expect(resetButton.attributes("disabled")).toBeDefined();

    // 実績入力
    const timeField = wrapper.find("[data-testid='actual-time-row-0']");
    await timeField.setValue("3");
    expect((timeField.element as HTMLInputElement).value).toBe("3");
  });


  it("全てを選択/解除", async () => {
    // デフォルトの状態
    const defaultCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const defaultCheckedCount = defaultCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;
    expect(defaultCheckedCount).toBe(0);

    // 全て選択をクリック
    wrapper.find("[data-testid='select-all-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    const checkboxes = wrapper.findAll('input[type="checkbox"]');
    const checkedCount = checkboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(checkedCount).toBe(pendingActivities.length);
    // 選択を解除
    wrapper.find("[data-testid='reset-selected-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    const newCheckboxes = wrapper.findAll('input[type="checkbox"]');
    const newCheckedCount = newCheckboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(newCheckedCount).toBe(0);
  });

  it("変更分全てを選択/解除", async () => {
    // 選択ボタンをクリックできないことを確認(変更がないため選択対象なし)
    const submitButton = wrapper.find("[data-testid='select-edited-activities']");
    expect(submitButton.attributes("disabled"));
    // 変更してから再度選択
    const timeField = wrapper.find("[data-testid='actual-time-row-0']") as DOMWrapper<HTMLInputElement>;
    const newValue = "5";
    await timeField.setValue(newValue);
    expect(timeField.element.value).toEqual(newValue);
    expect(submitButton.attributes("disabled")).toBeUndefined(); // disabled属性がなくなっていることを確認
    // 変更を元に戻す
    wrapper.find("[data-testid='reset-edited-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ
    expect(timeField.element.value).toEqual("3"); const checkboxes = wrapper.findAll('input[type="checkbox"]');
    const checkedCount = checkboxes.filter(
      (checkbox) => (checkbox.element as HTMLInputElement).checked
    ).length;

    expect(checkedCount).toBe(0);
  })

  it('成功', async () => {
    const expectedMessage = "2025/1/1の活動時間を3時間に登録しました\n2025/1/2の活動時間を3.5時間に登録しました";

    mockedPut.mockResolvedValue({
      status: 200,
      data: { message: expectedMessage }
    });
    // 全て選択をクリック
    wrapper.find("[data-testid='select-all-activities']").trigger("click");
    await flushPromises(); // html要素が変わるため変更を待つ

    await wrapper.find("[data-testid='submit-multi-actual']").trigger("click");
    await flushPromises();

    // モーダルのOKボタンをクリック
    const bModal = wrapper.findComponent({ name: 'BModal' });
    await bModal.vm.$emit('ok');
    await flushPromises();

    expect(mockedPut).toBeCalledWith(
      `activities/multi/actual`,
      {
        activities: pendingActivities
      }
    );
    expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
  })
});