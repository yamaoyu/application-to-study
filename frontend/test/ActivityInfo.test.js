import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActivityInfo from '@/views/ActivityInfo.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

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

const createResolvedMock = (data, status = 200) => ({
  type: "resolve",
  value: { 
    status: status, 
    data: data 
  }
});

const createRejectedMock = (detail, status = 404) => ({
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

const mountActivityInfo = async({
  activitiesMock = createResolvedMock(defaultMonthlyActivities)
} = {}) => {
  if (activitiesMock.type==="reject") {
    apiClient.get.mockRejectedValueOnce(activitiesMock.value);
  } else {
    apiClient.get.mockResolvedValueOnce(activitiesMock.value);
  }

  const wrapper = mountComponent(ActivityInfo);
  await flushPromises();
  return wrapper;
} 

describe('月ごとのアクティビティ情報の表示', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityInfo);
        }
    );
    
    it('データがある', async () => {
      wrapper = await mountActivityInfo();
      expect(wrapper.vm.activities).toEqual(expectedActivities);
      expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
      expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
      expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
      expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
      expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
      expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
      expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
    });

    it('データがない', async() =>{
        const expectedMessage = "2025年1月の活動は登録されていません"
        apiClient.get.mockRejectedValue({
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

describe('年ごとのアクティビティ情報の表示', () =>{
  let wrapper;

  const expectedTotalIncome = "30";
  const expectedSalary = "25";
  const expectedPayAdjustment = "5";
  const expectedBonus = "10";
  const expectedPenalty = "5";
  const expectedSuccessDays = "2";
  const expectedFailDays = "1";
  const expectedMonthlyinfo = [
    { jan : 
        {
          salary: 25,
          pay_adjustment: 5,
          bonus: 10,
          penalty: 5,
          success_days: 2,
          fail_days: 1
        } 
    }
  ]; // 1月のみのデータがある

  beforeEach(() => {
      vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
      }
  );

  it('データがある', async () => {
    wrapper = await mountActivityInfo();
    // タブ変更後用のモック
    apiClient.get.mockResolvedValue({
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
    wrapper.find("[data-testid='tab-yearly']").trigger('click');
    await flushPromises();

    expect(wrapper.vm.activities).toEqual(expectedMonthlyinfo);
    expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
    expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
    expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
    expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
    expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
    expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
    expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
  });

  it('データがない', async() =>{
    wrapper = await mountActivityInfo();
    const expectedMessage = "2025年の活動は登録されていません"
    apiClient.get.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: expectedMessage }
      }
    });
    // タブを変更
    wrapper.find("[data-testid='tab-yearly']").trigger("click");
    await flushPromises();

    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  })
})

describe('全期間のアクティビティ情報の表示', async() =>{
  let wrapper;

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

  it('データがある', async() =>{
    wrapper = await mountActivityInfo();

    apiClient.get.mockResolvedValue({
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
    wrapper.find("[data-testid='tab-all']").trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
    expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
    expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
    expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
    expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
    expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
    expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
  })

  it('データがない', async() =>{
    wrapper = await mountActivityInfo();

    const expectedMessage = "活動は登録されていません"
    apiClient.get.mockRejectedValue({
      response: {
        status: 404,
        data: { detail: expectedMessage }
      }
    });
    // タブを変更
    wrapper.find("[data-testid='tab-yearly']").trigger('click');
    await flushPromises();

    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  })
});
