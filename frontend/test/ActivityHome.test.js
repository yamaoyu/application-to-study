import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActivityHome from '@/views/ActivityHome.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';

describe('選択した日の活動登録状況確認', () => {
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ActivityHome);
    }
  );

  it('データがある', async() => {
    const today = new Date();
    const expectedYear = today.getFullYear();
    const expectedMonth = `${today.getMonth()+1}`.padStart(2, '0');
    const expectedDate = `${today.getDate()}`.padStart(2, '0');
    
    const expectedData = {
        date: `${expectedYear}-${expectedMonth}-${expectedDate}`,
        target_time: 3,
        actual_time: 0,
        status: "pending",
        bonus: 0,
        penalty: 0.38
    };

    apiClient.get.mockResolvedValue({
        status: 200,
        data: expectedData
    });

    // activityResに定義される
    await wrapper.vm.renewActivities();
    expect(wrapper.vm.activityRes.data).toEqual(expectedData);
    expect(apiClient.get).toBeCalledWith(
        `activities/${expectedYear}/${expectedMonth}/${expectedDate}`
    );
    expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(expectedData.target_time));
    expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(expectedData.actual_time));
    expect(wrapper.find("[data-testid='show-status']").text()).toEqual("未確定");
  });

  it('データがない', async() => {
    const expectedMessage = "2025-1-1の活動記録は未登録です";
    apiClient.get.mockRejectedValue({
      response: {
        status: 404,
        data: {
          detail: expectedMessage
        }
      }
    });
    await wrapper.vm.renewActivities();
    expect(wrapper.find("[data-testid='pendingMsg']").text()).toEqual(expectedMessage);
  });
});


describe('タブの切り替え', ()=>{
  let wrapper;

  beforeEach(() =>{
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ActivityHome);
    }
  );

  it('操作タイプ(目標、実績、終了)の切り替え', async() =>{
    // 目標→実績
    expect(wrapper.vm.activeTab).toEqual('target');
    wrapper.find("[data-testid='actual']").trigger('click');
    expect(wrapper.vm.activeTab).toEqual('actual');
    // 実績→終了
    wrapper.find("[data-testid='finish']").trigger('click');
    expect(wrapper.vm.activeTab).toEqual('finish');
    // 終了→目標
    wrapper.find("[data-testid='target']").trigger('click');
    expect(wrapper.vm.activeTab).toEqual('target');
  });
});
