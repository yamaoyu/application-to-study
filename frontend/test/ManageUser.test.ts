import { describe, it, expect, vi, beforeEach } from 'vitest';
import ManageUser from '@/views/ManageUser.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper } from '@vue/test-utils';

const mockedGet = vi.mocked(apiClient.get);
const mockedPatch = vi.mocked(apiClient.patch)

const GENERAL_ACTIVE = "general-active"
const GENERAL_SUSPEND = "general-suspend"
const ADMIN_ACTIVE = "admin-active"
const ADMIN_SUSPEND = "admin-suspend"
const now = new Date();

const defaultUserData = [
    {
        username: GENERAL_ACTIVE,
        status: "active",
        role: "general",
        created_at: now,
        last_active_at: now,
    },
    {
        username: GENERAL_SUSPEND,
        status: "suspended",
        role: "general",
        created_at: now,
        last_active_at: now
    },
    {
        username: ADMIN_ACTIVE,
        status: "active",
        role: "admin",
        created_at: now,
        last_active_at: now
    },
    {
        username: ADMIN_SUSPEND,
        status: "suspended",
        role: "admin",
        created_at: now,
        last_active_at: now
    }
]


type UserData = typeof defaultUserData;

type UsersMock =
    | {
        type: 'resolve';
        value: {
            status: number;
            data: { users: UserData };
        }
    }
    | {
        type: 'reject';
        value: {
            response: {
                status: number;
                data: {
                    code: string;
                };
            }
        }
    };

const createResolvedMock = (users: UserData, status = 200) => ({
    type: "resolve",
    value: {
        status,
        data: { users: users }
    }
} as const);

const createRejectedMock = (code: string, status = 404) => ({
    type: "reject",
    value: {
        response: {
            status,
            data: {
                code
            }
        }
    }
} as const);

const mountManageUser = async (usersMock: UsersMock) => {
    if (usersMock.type === "reject") {
        mockedGet.mockRejectedValueOnce(usersMock.value);
    } else {
        mockedGet.mockResolvedValueOnce(usersMock.value);
    }

    const wrapper = mountComponent(ManageUser);
    await flushPromises();
    return wrapper;
};


describe('フィルターなし', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it("データあり", async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        );
        const rows = wrapper.findAll('[data-testid="user-row"]');
        expect(rows).toHaveLength(4);
    });

    it("データなし", async () => {
        // 実際はコンテナ起動時に管理者ユーザーが作成されるため、ユーザーが0になることはない
        const expectedMessage = "ユーザーが見つかりません";
        wrapper = await mountManageUser(createRejectedMock("USER_NOT_FOUND"));
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
        expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
    });
});

describe('フィルターの確認', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
        wrapper = mountComponent(ManageUser);
    }
    );

    it("ロールでフィルター(admin)", async () => {
        await wrapper.find('[data-testid="role-filter"]').setValue("admin");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": "admin",
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
    })

    it("ロールでフィルター(general)", async () => {
        await wrapper.find('[data-testid="role-filter"]').setValue("general");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": "general",
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
    })


    it("ステータスでフィルター(active)", async () => {
        await wrapper.find('[data-testid="status-filter"]').setValue("active");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": "active",
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
    })


    it("ステータスでフィルター(suspended)", async () => {
        await wrapper.find('[data-testid="status-filter"]').setValue("suspended");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": "suspended",
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
    })

    it("最終ログイン日でフィルター", async () => {
        await wrapper.find('[data-testid="last-active-at-filter"]').setValue("2026-10-01");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": undefined,
                    "last_active_at": "2026-10-01",
                    "created_at": undefined,
                    "username": undefined
                }
            }
        )
    })

    it("作成日でフィルター", async () => {
        await wrapper.find('[data-testid="created-at-filter"]').setValue("2026-10-01");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": "2026-10-01",
                    "username": undefined
                }
            }
        )
    })

    it("ユーザー名でフィルター", async () => {
        await wrapper.find('[data-testid="username-filter"]').setValue("aaaaa");
        await wrapper.find('[data-testid="apply"').trigger("click");
        expect(mockedGet).toBeCalledWith(
            "admin/users",
            {
                "params": {
                    "status": undefined,
                    "role": undefined,
                    "last_active_at": undefined,
                    "created_at": undefined,
                    "username": "aaaaa"
                }
            }
        )
    })
})

describe('ロール変更', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it("admin→general", async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        mockedPatch.mockResolvedValue({
            status: 200,
            data: {
                "username": ADMIN_SUSPEND,
                "role": "general"
            }
        });

        const roleChangeBtn = await wrapper.find('[data-testid="change-role-3"]');
        expect(roleChangeBtn.text()).toBe("一般権限へ変更");
        await roleChangeBtn.trigger("click");
        expect(mockedPatch).toHaveBeenCalledWith(
            `admin/users/${ADMIN_SUSPEND}/role`,
            {
                "role": "general"
            }
        );
    })

    it("general→admin", async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        mockedPatch.mockResolvedValue({
            status: 200,
            data: {
                "username": GENERAL_ACTIVE,
                "role": "admin"
            }
        });

        const roleChangeBtn = await wrapper.find('[data-testid="change-role-0"]');
        expect(roleChangeBtn.text()).toBe("管理者権限へ変更");
        await roleChangeBtn.trigger("click");
        expect(mockedPatch).toHaveBeenCalledWith(
            `admin/users/${GENERAL_ACTIVE}/role`,
            {
                "role": "admin"
            }
        );
    })
})


describe('ステータス変更', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it("active→suspended", async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        mockedPatch.mockResolvedValue({
            status: 200,
            data: {
                "username": GENERAL_ACTIVE,
                "status": "suspended"
            }
        });

        const roleChangeBtn = await wrapper.find('[data-testid="change-status-0"]');
        expect(roleChangeBtn.text()).toBe("停止する");
        await roleChangeBtn.trigger("click");
        expect(mockedPatch).toHaveBeenCalledWith(
            `admin/users/${GENERAL_ACTIVE}/status`,
            {
                "status": "suspended"
            }
        );
    })

    it("suspended→active", async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        mockedPatch.mockResolvedValue({
            status: 200,
            data: {
                "username": GENERAL_SUSPEND,
                "status": "active"
            }
        });

        const roleChangeBtn = await wrapper.find('[data-testid="change-status-1"]');
        expect(roleChangeBtn.text()).toBe("有効化する");
        await roleChangeBtn.trigger("click");
        expect(mockedPatch).toHaveBeenCalledWith(
            `admin/users/${GENERAL_SUSPEND}/status`,
            {
                "status": "active"
            }
        );
    })
})

describe('パスワードリセット', () => {
    let wrapper: VueWrapper;

    beforeEach(() => {
        vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
    );

    it('成功', async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        const newPassword = "PWRD%l5VLsmBPI%$";

        // パスワードリセットのモック
        mockedPatch.mockResolvedValue({
            status: 200,
            data: {
                "username": GENERAL_SUSPEND,
                "password": newPassword
            }
        });


        await wrapper.find("[data-testid='reset-password-1']").trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector('[data-testid="modal-show"]') as HTMLDivElement;
        expect(modal).not.toBeNull();
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await flushPromises();
        expect(bModal.props("title")).toBe("パスワードリセット確認");
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPatch).toHaveBeenCalledWith(
            `/admin/users/${GENERAL_SUSPEND}/password`
        )
        const expectedMessage = [
            "パスワードリセットに成功しました\nこの情報は一度しか表示されません",
            `ユーザー名: ${GENERAL_SUSPEND}`,
            `新しいパスワード: ${newPassword}`
        ].join("\n")
        expect(wrapper.find("[data-testid='message']").text()).toEqual(expectedMessage);
    })

    it('失敗', async () => {
        wrapper = await mountManageUser(createResolvedMock(defaultUserData));

        // パスワードリセットのモック
        mockedPatch.mockRejectedValue({
            response: {
                status: 403,
                data: {
                    code: "CANNOT_RESET_OWN_PASSWORD"
                }
            }
        });

        await wrapper.find("[data-testid='reset-password-1']").trigger("click");
        // モーダルが表示されることを確認
        const modal = document.body.querySelector('[data-testid="modal-show"]') as HTMLDivElement;
        expect(modal).not.toBeNull();
        const bModal = wrapper.findComponent({ name: 'BModal' });
        await flushPromises();
        expect(bModal.props("title")).toBe("パスワードリセット確認");
        await bModal.vm.$emit('ok');
        await flushPromises();
        expect(mockedPatch).toHaveBeenCalledWith(
            `/admin/users/${GENERAL_SUSPEND}/password`
        )

        expect(wrapper.find("[data-testid='message']").text()).toEqual("自分のパスワードはリセットできません");
    })
})
