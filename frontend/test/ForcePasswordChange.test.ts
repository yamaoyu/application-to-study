import { describe, it, expect, vi, beforeEach } from "vitest";
import ForcePasswordChange from "@/views/ForcePasswordChange.vue";
import { mountComponent, mockRouterReplace } from "./vitest.setup";
import { apiClient } from "@/views/api/client";
import { VueWrapper } from "@vue/test-utils";

const mockedPatch = vi.mocked(apiClient.patch);

describe("パスワード変更リクエストを送信", () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks(); //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ForcePasswordChange);
  });

  it("パスワードを変更に成功", async () => {
    // 新しいパスワード
    const newPassForm = wrapper.find('[data-testid="newPassword"]');
    const newPassword = "newP@ssword1";
    await newPassForm.setValue(newPassword);

    // パスワード確認
    const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
    const newPasswordCheck = "newP@ssword1";
    await passCheckForm.setValue(newPasswordCheck);
    mockedPatch.mockResolvedValue({
      status: 200,
      data: {},
    });
    await wrapper
      .find('[data-testid="password-change-button"]')
      .trigger("submit");

    expect(mockedPatch).toHaveBeenCalledTimes(1);
    expect(mockRouterReplace).toHaveBeenCalledWith({
      name: "Login",
      query: {
        message:
          "パスワードを変更しました。新しいパスワードでログインしてください",
      },
    });
  });
});

describe("フォームの確認", () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks(); //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ForcePasswordChange);
  });

  it("パスワードが一致しないとリクエストが送信されない", async () => {
    // 新しいパスワード
    const newPassForm = wrapper.find('[data-testid="newPassword"]');
    const newPassword = "newP@ssword1";
    await newPassForm.setValue(newPassword);

    // パスワード確認
    const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
    const newPasswordCheck = "not-equal";
    await passCheckForm.setValue(newPasswordCheck);

    await wrapper
      .find('[data-testid="password-change-button"]')
      .trigger("submit");
    expect(mockedPatch).toHaveBeenCalledTimes(0);
  });

  it("パスワードが条件を満たさないとリクエストが送信されない", async () => {
    // 新しいパスワード
    const newPassForm = wrapper.find('[data-testid="newPassword"]');
    const newPassword = "newP@ssword"; //数字が含まれない
    await newPassForm.setValue(newPassword);

    // パスワード確認
    const passCheckForm = wrapper.find('[data-testid="newPasswordCheck"]');
    const newPasswordCheck = "newP@ssword";
    await passCheckForm.setValue(newPasswordCheck);

    await wrapper
      .find('[data-testid="password-change-button"]')
      .trigger("submit");
    expect(mockedPatch).toHaveBeenCalledTimes(0);
  });
});
