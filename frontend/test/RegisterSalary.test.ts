import { describe, it, expect, vi, beforeEach } from 'vitest';
import RegisterSalary from '@/views/RegisterSalary.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedPost = vi.mocked(apiClient.post);
const mockedGet = vi.mocked(apiClient.get);


describe('月の入力', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(RegisterSalary);
    }
    );

    it('デフォルト値の確認', async () => {
        const today = new Date();
        const expectedYear = today.getFullYear();
        const expectedMonth = `${today.getMonth() + 1}`.padStart(2, '0');
        const selectedMonth = wrapper.find('[data-testid="selected-month"]').element as HTMLInputElement;
        expect(selectedMonth.value).toEqual(`${expectedYear}-${expectedMonth}`);
    });

    it('前年にする', async () => {
        const today = new Date();
        const expectedYear = `${today.getFullYear() - 1}`;
        const expectedMonth = `${today.getMonth() + 1}`.padStart(2, '0');
        await wrapper.find('[data-testid="previousYear"]').trigger('click');
        const selectedMonth = wrapper.find('[data-testid="selected-month"]').element as HTMLInputElement;
        expect(selectedMonth.value).toEqual(`${expectedYear}-${expectedMonth}`);
    })

    it('前月にする', async () => {
        const today = new Date();
        let expectedYear = `${today.getFullYear()}`;
        let expectedMonth = `${today.getMonth()}`.padStart(2, '0');
        if (expectedMonth === "00") {
            expectedYear = `${today.getFullYear() - 1}`;
            expectedMonth = "12";
        }
        await wrapper.find('[data-testid="previousMonth"]').trigger('click');
        const selectedMonth = wrapper.find('[data-testid="selected-month"]').element as HTMLInputElement;
        expect(selectedMonth.value).toEqual(`${expectedYear}-${expectedMonth}`);
    })

    it('翌年にする', async () => {
        const selectedMonth = wrapper.find('[data-testid="selected-month"]').element as HTMLInputElement;
        const [year, month] = selectedMonth.value.split('-').map(Number);
        let newDate = new Date(year + 1, month);
        const newSelectedMonth = newDate.toISOString().slice(0, 7);
        await wrapper.find('[data-testid="nextYear"]').trigger('click');
        expect(selectedMonth.value).toEqual(`${newSelectedMonth}`);
    })

    it('翌月にする', async () => {
        const selectedMonth = wrapper.find('[data-testid="selected-month"]').element as HTMLInputElement;
        const [year, month] = selectedMonth.value.split('-').map(Number);
        let newDate = new Date(year, month + 1);
        const newSelectedMonth = newDate.toISOString().slice(0, 7);
        await wrapper.find('[data-testid="nextMonth"]').trigger('click');
        expect(selectedMonth.value).toEqual(`${newSelectedMonth}`);
    })
});

describe('月収の入力', () => {
    let wrapper: VueWrapper;
    // 取得する月の設定(前月)
    const date = new Date();
    let expectedYear = date.getFullYear();
    let expectedMonth = date.getMonth();
    if (date.getMonth() == 0) {
        expectedYear = date.getFullYear() - 1
        expectedMonth = 12
    };

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('-10万', async () => {
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue('20');
        await flushPromises();
        expect(incomeForm.element.value).toEqual('20');
        await wrapper.find("[data-testid='minus10']").trigger('click');
        expect(incomeForm.element.value).toEqual('10');
    });

    it('-5万', async () => {
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue('20');
        await flushPromises();
        expect(incomeForm.element.value).toEqual('20');
        await wrapper.find("[data-testid='minus5']").trigger('click');
        expect(incomeForm.element.value).toEqual('15');
    });

    it('+5万', async () => {
        // 初期値取得
        mockedGet.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: "2025-1の月収は未登録です"
                }
            }
        });
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        // データ入力
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue('5');
        await wrapper.find("[data-testid='plus5']").trigger('click');
        expect(incomeForm.element.value).toEqual('10');
    });

    it('+10万', async () => {
        // 初期値取得
        mockedGet.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: "2025-1の月収は未登録です"
                }
            }
        });
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        // データ入力
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue('5');
        await wrapper.find("[data-testid='plus10']").trigger('click');
        expect(incomeForm.element.value).toEqual('15');
    });

});

describe('デフォルト値の確認', () => {
    let wrapper: VueWrapper;
    // 取得する月の設定(前月)
    const date = new Date();
    let expectedYear = date.getFullYear();
    let expectedMonth = date.getMonth();
    if (date.getMonth() == 0) {
        expectedYear = date.getFullYear() - 1
        expectedMonth = 12
    };

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('前年度の年収あり', async () => {
        const expectedData = {
            month_info: {
                salary: 25,
                total_bonus: 0.38,
                total_penalty: 0
            },
            total_income: 25.38,
            pay_adjustment: 0.38
        };

        mockedGet.mockResolvedValue({
            status: 200,
            data: expectedData
        });
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        expect(mockedGet).toBeCalledWith(
            `incomes/${expectedYear}/${expectedMonth}`,
        );
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue(expectedData["month_info"].salary.toString());
        expect(incomeForm.element.value).toEqual(expectedData["month_info"].salary.toString());
    });

    it('前年度の年収なし', async () => {
        mockedGet.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: "2025-1の月収は未登録です"
                }
            }
        });
        wrapper = mountComponent(RegisterSalary);
        await flushPromises();
        expect(mockedGet).toBeCalledWith(
            `incomes/${expectedYear}/${expectedMonth}`,
        );
        const incomeForm = wrapper.find("[data-testid='income-form']") as DOMWrapper<HTMLInputElement>;
        incomeForm.setValue('5');
        expect(incomeForm.element.value).toEqual('5');
    });
});

describe('登録処理', async () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('月収登録に成功', async () => {
        const expectedMessage = "2025-1の月収:25万円"

        mockedPost.mockResolvedValue({
            status: 201,
            data: {
                message: expectedMessage
            }
        });
        wrapper = mountComponent(RegisterSalary);

        await wrapper.find('[data-testid="submit"]').trigger('submit');
        expect(wrapper.find('[data-testid="register-msg"]').text()).toEqual(expectedMessage);
    });

    it('既に登録済み', async () => {
        const expectedMessage = "その月の月収は既に登録されています"

        mockedPost.mockRejectedValue({
            response: {
                status: 404,
                data: {
                    detail: expectedMessage
                }
            }
        });
        wrapper = mountComponent(RegisterSalary);

        await wrapper.find('[data-testid="submit"]').trigger('submit');
        expect(wrapper.find('[data-testid="register-msg"]').text()).toEqual(expectedMessage);
    });
});