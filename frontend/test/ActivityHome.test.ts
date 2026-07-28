import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActivityHome from '@/views/ActivityHome.vue';
import TargetTab from '@/views/TargetTab.vue';
import ActualTab from '@/views/ActualTab.vue';
import FinishTab from '@/views/FinishTab.vue';
import { mountComponent, mockRouterPush } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedGet = vi.mocked(apiClient.get);

const today = new Date();
const expectedYear = today.getFullYear();
const expectedMonth = `${today.getMonth() + 1}`;
const expectedDate = `${today.getDate()}`;

const defaultActivityData = {
  date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
  target_time: 3,
  actual_time: 0,
  status: "pending",
  bonus: 0,
  penalty: 0.38
};

const defaultIncomeData = {
  base_income: 25.0,
  total_income: 25.38,
  pay_adjustment: 0.38
};

const createResolvedMock = (data: Record<string, any>, status = 200): mock => ({
  type: "resolve",
  value: {
    status: status,
    data: data
  }
});

const createRejectedMock = (code: string, status = 404): mock => ({
  type: "reject",
  value: {
    response: {
      status,
      data: {
        code: code
      }
    }
  }
});

type mock =
  | { type: 'resolve'; value: { status: number; data: Record<string, any> } }
  | { type: 'reject'; value: { response: { status: number; data: { code: string } } } };


const mountActivityHome = async ({
  activityMock = createResolvedMock(defaultActivityData),
  pendingMock = createResolvedMock(defaultActivityData),
  incomeMock = createResolvedMock(defaultIncomeData),
}: { activityMock?: mock, pendingMock?: mock, incomeMock?: mock } = {}) => {
  [activityMock, pendingMock, incomeMock].forEach((mock) => {
    if (mock.type === "reject") {
      mockedGet.mockRejectedValueOnce(mock.value);
    } else {
      mockedGet.mockResolvedValueOnce(mock.value);
    }
  });

  const wrapper = mountComponent(ActivityHome);
  await flushPromises();
  return wrapper;
}

describe('選択した日の活動登録状況確認', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ActivityHome);
  }
  );

  it('データがある', async () => {
    const wrapper = await mountActivityHome();
    // activityResに定義される
    expect(mockedGet).toBeCalledWith(
      `activities/${expectedYear}/${expectedMonth}/${expectedDate}`
    );
    expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(defaultActivityData.target_time));
    expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(defaultActivityData.actual_time));
    expect(wrapper.find("[data-testid='show-status']").text()).toEqual("未確定");
  });

  it('データがない', async () => {
    const wrapper = await mountActivityHome({
      activityMock: createRejectedMock("ACTIVITY_NOT_FOUND"),
      pendingMock: createRejectedMock("ACTIVITY_NOT_FOUND")
    });
    expect(wrapper.find("[data-testid='checkMsg']").text()).toEqual("活動が登録されていません");
  });
});


describe('タブの切り替え', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it('操作タイプ(目標、実績、終了)の切り替え', async () => {
    const wrapper = await mountActivityHome();
    expect(wrapper.findComponent(TargetTab).exists()).toBe(true);
    expect(wrapper.findComponent(ActualTab).exists()).toBe(false);
    expect(wrapper.findComponent(FinishTab).exists()).toBe(false);
    // 目標→実績
    await wrapper.find("[data-testid='actual']").trigger('click');
    expect(wrapper.findComponent(TargetTab).exists()).toBe(false);
    expect(wrapper.findComponent(ActualTab).exists()).toBe(true);
    expect(wrapper.findComponent(FinishTab).exists()).toBe(false);
    // 実績→終了
    await wrapper.find("[data-testid='finish']").trigger('click');
    expect(wrapper.findComponent(TargetTab).exists()).toBe(false);
    expect(wrapper.findComponent(ActualTab).exists()).toBe(false);
    expect(wrapper.findComponent(FinishTab).exists()).toBe(true);
    // 終了→目標
    await wrapper.find("[data-testid='target']").trigger('click');
    expect(wrapper.findComponent(TargetTab).exists()).toBe(true);
    expect(wrapper.findComponent(ActualTab).exists()).toBe(false);
    expect(wrapper.findComponent(FinishTab).exists()).toBe(false);
  });
});

describe('月収の登録状況に応じたリダイレクト', async () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  });

  it('月収の登録がある→月収登録ページにリダイレクトしない', async () => {
    const wrapper = await mountActivityHome();
    // 月収登録ページにリダイレクトせず、活動登録ページの内容が表示される
    expect(wrapper.find("[data-testid='target']").exists()).toBe(true);
    expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(defaultActivityData.target_time));
  });

  it('月収の登録がない→月収登録ページにリダイレクト', async () => {
    await mountActivityHome({
      incomeMock: createRejectedMock("SALARY_NOT_FOUND")
    });

    expect(mockRouterPush).toHaveBeenCalledWith({
      path: '/register/salary',
      query: {
        incomeMsg: "月収が登録されていません。先に月収を登録してください"
      }
    });
  });
})
