import { describe, expect, it } from "vitest";
import {
  validateUsername,
  validatePassword,
  checkPassword,
  validateEmail,
} from "@/views/utils/userValidation";

describe("", () => {
  it.each([
    ["3文字未満", "aa"],
    ["16文字を超える", "aaaaaaaaaaaaaaaaa"],
  ])("ユーザー名が%sの場合は無効になる", (_, username) => {
    const result = validateUsername(username);

    expect(result.valid).toBe(false);
    expect(result.message).toBe("ユーザー名は3文字以上16文字以下にして下さい");
  });
});

describe("validatePassword", () => {
  it.each([
    ["8文字未満", "aaaaaaa", "8文字以上16文字以下"],
    ["16文字を超える", "aaaaaaaaaaaaaaaaa", "8文字以上16文字以下"],
    ["大文字なし", "newp@ssword1", "大文字"],
    ["小文字なし", "NEWP@SSWORD1", "小文字"],
    ["数字なし", "NewP@ssword", "数字"],
    ["記号なし", "NewPassword1", "記号"],
  ])("%sの場合は無効になる", (_, password, expectedMessage) => {
    const result = validatePassword(password);

    expect(result.valid).toBe(false);
    expect(result.message).toContain(expectedMessage);
  });

  it("すべての条件を満たす場合は有効になる", () => {
    const result = validatePassword("newP@ssword1");

    expect(result.valid).toBe(true);
  });
});

describe("checkPassword", () => {
  it("パスワードが一致する", () => {
    const result = checkPassword("Newp@ssword1", "Newp@ssword1");

    expect(result.valid).toBe(true);
  });

  it("パスワードが一致しない", () => {
    const result = checkPassword("Newp@ssword1", "not-equal");

    expect(result.valid).toBe(false);
    expect(result.message).toBe("パスワードが一致しません");
  });
});

describe("validateEmail", () => {
  it("正しい形式", () => {
    const result = validateEmail("user1@example.com");

    expect(result.valid).toBe(true);
  });

  it("@がない", () => {
    const result = validateEmail("user1example.com");

    expect(result.valid).toBe(false);
    expect(result.message).toBe("メールアドレスの形式で入力して下さい");
  });

  it("@で終わっている", () => {
    const result = validateEmail("user1@");

    expect(result.valid).toBe(false);
    expect(result.message).toBe("メールアドレスの形式で入力して下さい");
  });
});
