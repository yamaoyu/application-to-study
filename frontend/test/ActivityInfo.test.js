import { describe, it, expect, vi, beforeEach } from 'vitest'
import ActivityInfo from '@/views/ActivityInfo.vue'
import { mountComponent } from './vitest.setup';
import axios from 'axios';

describe('月ごとのアクティビティ情報の表示', () => {
    let wrapper;

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

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ActivityInfo);
        }
    );
    
    it('データがある', async () => {
        // タブを変更
        wrapper.vm.activeTab = 'monthly';

        axios.get.mockResolvedValue({
            status: 200,
            data: {
                total_income: expectedTotalIncome,
                salary: expectedSalary,
                pay_adjustment: expectedPayAdjustment,
                bonus: expectedBonus,
                penalty: expectedPenalty,
                success_days: expectedSuccessDays,
                fail_days: expectedFailDays,
                activity_list: expectedActivities
            }
        });
        await wrapper.vm.getMonthlyInfo();

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
        // タブを変更
        wrapper.vm.activeTab = 'monthly';
        
        const expectedMessage = "2025年1月の活動は登録されていません"
        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: { detail: expectedMessage }
            }
        });
        await wrapper.vm.getMonthlyInfo();

        expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
    })
});

describe('年ごとのアクティビティ情報の表示', async() =>{
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
        wrapper = mountComponent(ActivityInfo);
        }
    );

    it('データがある', async () => {
        // タブを変更
        wrapper.vm.activeTab = 'yearly';

        axios.get.mockResolvedValue({
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
        await wrapper.vm.getYearlyInfo();

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
        // タブを変更
        wrapper.vm.activeTab = 'yearly';

        const expectedMessage = "2025年の活動は登録されていません"
        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: { detail: expectedMessage }
            }
        });
        await wrapper.vm.getYearlyInfo();

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
        wrapper = mountComponent(ActivityInfo);
        }
    );

    it('データがある', async() =>{
        // タブを変更
        wrapper.vm.activeTab = 'all';

        axios.get.mockResolvedValue({
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
        await wrapper.vm.getAllActivities();

        expect(wrapper.find('[data-testid="total-income"]').text()).toEqual(expectedTotalIncome);
        expect(wrapper.find('[data-testid="salary"]').text()).toEqual(expectedSalary);
        expect(wrapper.find('[data-testid="pay-adjustment"]').text()).toEqual(expectedPayAdjustment);
        expect(wrapper.find('[data-testid="bonus"]').text()).toEqual(expectedBonus);
        expect(wrapper.find('[data-testid="penalty"]').text()).toEqual(expectedPenalty);
        expect(wrapper.find('[data-testid="success-days"]').text()).toEqual(expectedSuccessDays);
        expect(wrapper.find('[data-testid="fail-days"]').text()).toEqual(expectedFailDays);
    })

    it('データがない', async() =>{
        // タブを変更
        wrapper.vm.activeTab = 'all';

        const expectedMessage = "活動は登録されていません"
        axios.get.mockRejectedValue({
            response: {
                status: 404,
                data: { detail: expectedMessage }
            }
        });
        await wrapper.vm.getAllActivities();

        expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
    })
})