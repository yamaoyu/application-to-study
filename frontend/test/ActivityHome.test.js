import { describe, it, expect, vi, beforeEach } from 'vitest';
import ActivityHome from '@/views/ActivityHome.vue';
import { mountComponent } from './vitest.setup';
import axios from 'axios';
import { flushPromises } from '@vue/test-utils';

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

        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        // activityResに定義される
        await wrapper.vm.renewActivity();
        expect(wrapper.vm.activityRes.data).toEqual(expectedData);

        expect(axios.get).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}`,
            {
                "headers": {
                    "Authorization": "登録なし",
                },
            },
        );

        expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(expectedData.target_time));
        expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(expectedData.actual_time));
        expect(wrapper.find("[data-testid='show-status']").text()).toEqual("未確定");
    });

    it('活動実績のデータがない', async() => {
        const expectedMessage = "2025-1-1の活動記録は未登録です";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.renewActivity();
        expect(wrapper.find("[data-testid='checkMsg']").text()).toEqual(expectedMessage);
    });
});


describe('タブの切り替え', ()=>{
    let wrapper;

    beforeEach(() =>{
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('登録タイプ(個別か一括)の切り替え', async() =>{
        // 初期値は個別であることを確認
        expect(wrapper.vm.registerType).toEqual('single');
        // 一括に切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        // 個別に切り替え
        wrapper.find("[data-testid='single']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('single');
    });

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
})

describe('目標時間の登録(個別)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('成功', async() => {
        await wrapper.find("[data-testid='submit-single-target']").trigger('submit');
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();

        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = `${today.getMonth()+1}`;
        const expectedDate = `${today.getDate()}`;
        const date = `${expectedYear}-${expectedMonth}-${expectedDate}`;

        const target_time = 3;
        wrapper.find("[data-testid='target-time']").setValue(target_time);
        const expectedData = {
            date: date,
            target_time: target_time,
            actual_time: 0,
            status: "pending",
            message: `${date}の目標時間を${target_time}に設定しました`
        };

        axios.post.mockResolvedValue({
            status: 201,
            data: expectedData
        });

        // todo再取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        await wrapper.vm.submitTarget();

        expect(axios.post).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}/target`,
            {
                target_time: target_time,
            },
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(expectedData.target_time));
        expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(expectedData.actual_time));
        expect(wrapper.find("[data-testid='show-status']").text()).toEqual("未確定");
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedData.message);
    });

    it('既に登録済みで失敗', async() => {
        const expectedMessage = "2025-1-1の目標時間は既に登録済みです";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.renewActivity();
        expect(wrapper.find("[data-testid='checkMsg']").text()).toEqual(expectedMessage);
    });
});

describe('実績時間の登録(個別)', () =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );


    it('成功', async() => {
        // タブの切り替え
        wrapper.find("[data-testid='actual']").trigger('click');
        expect(wrapper.vm.activeTab).toEqual('actual');

        await wrapper.find("[data-testid='submit-single-actual']").trigger('submit');
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();

        // リクエスト送信
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = `${today.getMonth()+1}`;
        const expectedDate = `${today.getDate()}`;
        const date = `${expectedYear}-${expectedMonth}-${expectedDate}`;

        const actual_time = 3;
        wrapper.find("[data-testid='actual-time']").setValue(actual_time);
        const expectedData = {
            date: date,
            target_time: 3,
            actual_time: actual_time,
            status: "pending",
            message: `${date}の目標時間を${actual_time}に設定しました`
        };

        axios.put.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        // todo再取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        await wrapper.vm.submitActual();

        expect(axios.put).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}/actual`,
            {
                actual_time: actual_time,
            },
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(expectedData.target_time));
        expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(expectedData.actual_time));
        expect(wrapper.find("[data-testid='show-status']").text()).toEqual("未確定");
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedData.message);
    });
})

describe('活動の終了(個別)', () =>{
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('成功', async() => {
        // タブの切り替え
        wrapper.find("[data-testid='finish']").trigger('click');
        expect(wrapper.vm.activeTab).toEqual('finish');

        await wrapper.find("[data-testid='finish-single']").trigger('submit');
        // モーダルが表示されることを確認
        const modal = document.body.querySelector("[data-testid='modal-show']");
        expect(modal).not.toBeNull();

        // リクエスト送信
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = `${today.getMonth()+1}`;
        const expectedDate = `${today.getDate()}`;
        const date = `${expectedYear}-${expectedMonth}-${expectedDate}`;

        const expectedData = {
            date: date,
            target_time: 3,
            actual_time: 3,
            status: "success",
            message: "目標達成！0.5万円(5000円)ボーナス追加！"
        };

        axios.put.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        // todo再取得処理のモック
        axios.get.mockResolvedValue({
            status: 200,
            data: expectedData
        });

        await wrapper.vm.finishActivity();

        expect(axios.put).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/${expectedYear}/${expectedMonth}/${expectedDate}/finish`,
            {},
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='show-target-time']").text()).toEqual(String(expectedData.target_time));
        expect(wrapper.find("[data-testid='show-actual-time']").text()).toEqual(String(expectedData.actual_time));
        expect(wrapper.find("[data-testid='show-status']").text()).toEqual("達成");
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedData.message);
    });

    it('既に終了済みで失敗', async() => {
        const expectedMessage = "2025-1-1の実績は終了済みです";

        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });

        await wrapper.vm.renewActivity();
        expect(wrapper.find("[data-testid='checkMsg']").text()).toEqual(expectedMessage);
    });
})

describe('目標時間の登録(一括)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('フォームの操作', async() =>{
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('target');
        // 初期値
        expect(wrapper.vm.targetActivities.length).toBe(1);
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
        wrapper.find("[data-testid='multi']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('target');
        await flushPromises(); // html要素が変わるため変更を待つ 
        
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

        axios.post.mockResolvedValue({
            status: 201,
            data: { message: expectedMessage }
        });

        await wrapper.vm.submitMultiTarget();

        expect(axios.post).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/multi/target`,
            {
                activities: targetActivities
            },
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    })
});


describe('実績時間の登録(一括)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('フォームの操作', async() =>{
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        wrapper.find("[data-testid='actual']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('actual');
        wrapper.vm.editActivities = [
            {
                date: "2025/1/1",
                target_time: 3,
                actual_time: 0,
                status: "success"
            }
        ];
        await flushPromises(); // html要素が変わるため変更を待つ 
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
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        wrapper.find("[data-testid='actual']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('actual');
        await flushPromises(); // html要素が変わるため変更を待つ
        console.log(wrapper.vm.pendingActivities)
        console.log(wrapper.vm.editActivities);
        console.log(wrapper.vm.selectedActivities)
        // 初期値確認
        expect(wrapper.vm.selectedActivities).toEqual([]);
        // 全て選択
        wrapper.find("[data-testid='toggle-all-activities']").trigger("click");
        expect(wrapper.vm.selectedActivities).toEqual(editActivities);
        // 全て解除
        wrapper.find("[data-testid='toggle-all-activities']").trigger("click");
        expect(wrapper.vm.selectedActivities).toEqual([]);
    })

    it('成功', async() =>{
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        wrapper.find("[data-testid='actual']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('actual');
        await flushPromises(); // html要素が変わるため変更を待つ 
        
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

        axios.put.mockResolvedValue({
            status: 200,
            data: { message: expectedMessage }
        });

        await wrapper.vm.submitMultiActual();

        expect(axios.put).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/multi/actual`,
            {
                activities: selectedActivities
            },
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    })
});


describe('活動の終了(一括)', () => {
    let wrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityHome);
        }
    );

    it('フォームの操作', async() =>{
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        wrapper.find("[data-testid='finish']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('finish');
        wrapper.vm.pendingActivities = [
            {
                date: "2025/1/1",
                target_time: 3,
                actual_time: 3,
                status: "success"
            }
        ]
        await flushPromises(); // html要素が変わるため変更を待つ 
        // 初期値
        expect(wrapper.vm.selectedActivities.length).toBe(0);
        // 選択
        wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
        expect(wrapper.vm.selectedActivities.length).toBe(1);
        // 解除
        wrapper.find("[data-testid='is-selected-finish-0']").trigger("click");
        expect(wrapper.vm.selectedActivities.length).toBe(0);
    })

    it('成功', async() =>{
        // タブの切り替え
        wrapper.find("[data-testid='multi']").trigger('click');
        wrapper.find("[data-testid='finish']").trigger('click');
        expect(wrapper.vm.registerType).toEqual('multi');
        expect(wrapper.vm.activeTab).toEqual('finish');
        await flushPromises(); // html要素が変わるため変更を待つ 
        
        const expectedMessage = "ボーナス-ペナルティ：0.3万円(3000円)\nボーナス：0.5万円(5000円)\nペナルティ：0.2万円(2000円)\n2025/1/1の活動を終了:ボーナス0.5万円(5000円)\n2025/1/2の活動を終了ペナルティ0.2万円(2000円)";

        const selectedDates = [
            {
                date: "2025/1/1"
            },
            {
                date: "2025/1/2"
            }
        ];
        wrapper.vm.selectedActivities = selectedDates;

        axios.put.mockResolvedValue({
            status: 200,
            data: { message: expectedMessage }
        });

        await wrapper.vm.finishMultiActivities();

        expect(axios.put).toBeCalledWith(
            process.env.VITE_BACKEND_URL + `activities/multi/finish`,
            {
                dates: selectedDates
            },
            {
                "headers": {
                "Authorization": "登録なし",
                },
            }
        );
        expect(wrapper.find("[data-testid='reqMsg']").text()).toEqual(expectedMessage);
    })
});