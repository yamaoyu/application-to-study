import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActivityInfo from '@/views/ActivityInfo.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedGet = vi.mocked(apiClient.get);

const expectedTotalIncome = "30";
const expectedSalary = "25";
const expectedPayAdjustment = "5";
const expectedBonus = "10";
const expectedPenalty = "5";
const expectedSuccessDays = "2";
const expectedFailDays = "1";
const expectedActivities = [
  { date: '2025-1-1', target_time: 5, actual_time: 5, status: 'success' },
  { date: '2025-1-2', target_time: 5, actual_time: 0, status: 'failure' },
  { date: '2025-1-3', target_time: 5, actual_time: 5, status: 'success' }
];

const defaultMonthlyActivities = {
  total_income: expectedTotalIncome,
  salary: expectedSalary,
  pay_adjustment: expectedPayAdjustment,
  bonus: expectedBonus,
  penalty: expectedPenalty,
  success_days: expectedSuccessDays,
  fail_days: expectedFailDays,
  activity_list: expectedActivities
};

const createResolvedMock = (data: Record<string, any>, status = 200): mock => ({
  type: "resolve",
  value: {
    status: status,
    data: data
  }
});

const createRejectedMock = (detail: string, status = 404): mock => ({
  type: "reject",
  value: {
    response: {
      status,
      data: {
        detail: detail
      }
    }
  }
});

type mock =
  | { type: 'resolve'; value: { status: number; data: Record<string, any> } }
  | { type: 'reject'; value: { response: { status: number; data: { detail: string } } } };

const mountActivityInfo = async ({
  activitiesMock = createResolvedMock(defaultMonthlyActivities)
}: { activitiesMock?: mock } = {}) => {
  if (activitiesMock.type === "reject") {
    mockedGet.mockRejectedValueOnce(activitiesMock.value);
  } else {
    mockedGet.mockResolvedValueOnce(activitiesMock.value);
  }

  const wrapper = mountComponent(ActivityInfo);
  await flushPromises();
  return wrapper;
}

describe('月ごとのアクティビティ情報の表示', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ActivityInfo);
  }
  );

  it('データがある', async () => {
    wrapper = await mountActivityInfo();
    // アクティビティ情報の件数と1件目の内容を確認
    const rows = wrapper.findAll('[data-testid="monthly-activity-row"]');
    expect(rows).toHaveLength(expectedActivities.length);
    expect(rows[0].find('[data-testid="activity-date-0"]').text()).toBe(expectedActivities[0].date);
    expect(rows[0].find('[data-testid="activity-target-time-0"]').text()).toBe(`${expectedActivities[0].target_time}時間`);
    expect(rows[0].find('[data-testid="activity-actual-time-0"]').text()).toBe(`${expectedActivities[0].actual_time}時間`);
    expect(rows[0].find('[data-testid="activity-status-0"]').text()).toBe("達成");
    // 給料情報の表示も確認
    expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
    expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
    expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
    expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
    expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
    expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
    expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
  });

  it('データがない', async () => {
    const expectedMessage = "2025年1月の活動は登録されていません"
    mockedGet.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: expectedMessage }
      }
    });
    wrapper = await mountActivityInfo({
      activitiesMock: createRejectedMock(expectedMessage)
    });
    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  })
});

describe('年ごとのアクティビティ情報の表示', () => {
  let wrapper: VueWrapper;

  const expectedTotalIncome = "30";
  const expectedSalary = "25";
  const expectedPayAdjustment = "5";
  const expectedBonus = "10";
  const expectedPenalty = "5";
  const expectedSuccessDays = "2";
  const expectedFailDays = "1";
  const expectedMonthlyinfo = {
    jan:
    {
      salary: 25,
      bonus: 10,
      penalty: 5,
      success_days: 2,
      fail_days: 1
    }
  }; // 1月のみのデータがある

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it('データがある', async () => {
    wrapper = await mountActivityInfo();
    // タブ変更後用のモック
    mockedGet.mockResolvedValue({
      status: 200,
      data: {
        total_income: expectedTotalIncome,
        salary: expectedSalary,
        pay_adjustment: expectedPayAdjustment,
        bonus: expectedBonus,
        penalty: expectedPenalty,
        success_days: expectedSuccessDays,
        fail_days: expectedFailDays,
        monthly_info: expectedMonthlyinfo
      }
    });
    // タブを変更
    await wrapper.find("[data-testid='tab-yearly']").trigger('click');
    await flushPromises();

    // アクティビティ情報の件数を確認
    const rows = wrapper.findAll('[data-testid="year-activity-row"]');

    // 1月のデータが正しく表示されているか確認
    expect(rows[0].find('[data-testid="activity-salary-jan"]').text()).toBe(`${expectedMonthlyinfo.jan.salary}万円`);
    expect(rows[0].find('[data-testid="activity-bonus-jan"]').text()).toBe(`${expectedMonthlyinfo.jan.bonus}万円`);
    expect(rows[0].find('[data-testid="activity-penalty-jan"]').text()).toBe(`${expectedMonthlyinfo.jan.penalty}万円`);
    expect(rows[0].find('[data-testid="activity-success-days-jan"]').text()).toBe(`${expectedMonthlyinfo.jan.success_days}日`);
    expect(rows[0].find('[data-testid="activity-fail-days-jan"]').text()).toBe(`${expectedMonthlyinfo.jan.fail_days}日`);

    expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
    expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
    expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
    expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
    expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
    expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
    expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
  });

  it('データがない', async () => {
    wrapper = await mountActivityInfo();
    const expectedMessage = "2025年の活動は登録されていません"
    mockedGet.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: expectedMessage }
      }
    });
    // タブを変更
    await wrapper.find("[data-testid='tab-yearly']").trigger("click");
    await flushPromises();

    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  })
})

describe('全期間のアクティビティ情報の表示', async () => {
  let wrapper: VueWrapper;

  const expectedTotalIncome = "30";
  const expectedSalary = "25";
  const expectedPayAdjustment = "5";
  const expectedBonus = "10";
  const expectedPenalty = "5";
  const expectedSuccessDays = "2";
  const expectedFailDays = "1";

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it('データがある', async () => {
    wrapper = await mountActivityInfo();

    mockedGet.mockResolvedValue({
      status: 200,
      data: {
        total_income: expectedTotalIncome,
        salary: expectedSalary,
        pay_adjustment: expectedPayAdjustment,
        bonus: expectedBonus,
        penalty: expectedPenalty,
        success_days: expectedSuccessDays,
        fail_days: expectedFailDays
      }
    });
    // タブを変更
    await wrapper.find("[data-testid='tab-all']").trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
    expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
    expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
    expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
    expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
    expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
    expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
  })

  it('データがない', async () => {
    wrapper = await mountActivityInfo();

    const expectedMessage = "活動は登録されていません"
    mockedGet.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: expectedMessage }
      }
    });
    // タブを変更
    await wrapper.find("[data-testid='tab-yearly']").trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  })
});
