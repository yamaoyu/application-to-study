import { describe, it, expect, vi, beforeEach } from 'vitest';
import ShowTodo from '@/views/ShowTodo.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises, VueWrapper, DOMWrapper } from '@vue/test-utils';

const mockedGet = vi.mocked(apiClient.get);

const defaultTodosData = [
  {
    detail: "test detail1",
    due: "2025-1-1",
    status: true,
    title: "test title1",
    todo_id: 1,
    username: "test"
  },
  {
    detail: "test detail2",
    due: "2025-1-2",
    status: false,
    title: "test title2",
    todo_id: 2,
    username: "test"
  },
];

type TodosMock =
  | { type: 'resolve'; value: { status: number; data: Record<string, any> } }
  | { type: 'reject'; value: { response: { status: number; data: { detail: string } } } };

const createResolvedMock = (data: Record<string, any>, status = 200) => ({
  type: "resolve",
  value: {
    status: status,
    data: data
  }
} as const);

const createRejectedMock = (detail: string, status = 404) => ({
  type: "reject",
  value: {
    response: {
      status,
      data: {
        detail: detail
      }
    }
  }
} as const);

const mountShowTodo = async ({
  todosMock = createResolvedMock(defaultTodosData),
}: { todosMock?: TodosMock } = {}) => {
  if (todosMock.type === "reject") {
    mockedGet.mockRejectedValueOnce(todosMock.value);
  } else {
    mockedGet.mockResolvedValueOnce(todosMock.value);
  }

  const wrapper = mountComponent(ShowTodo);
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
    wrapper = await mountShowTodo();
    expect(mockedGet).toBeCalledWith(
      "todos",
    );
    const rows = wrapper.findAll('[data-testid="todo-row"]');
    expect(rows).toHaveLength(defaultTodosData.length);
  });

  it("データなし", async () => {
    const expectedMessage = "登録された情報はありません";
    wrapper = await mountShowTodo({
      todosMock: createRejectedMock(expectedMessage)
    });
    expect(mockedGet).toBeCalledWith(
      "todos",
    )
    expect(wrapper.find('[data-testid="message"]').text()).toBe(expectedMessage);
  });
});

describe('フィルターの操作', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    wrapper = mountComponent(ShowTodo);
  }
  );

  it("ステータスを選択", async () => {
    // すべてに変更
    const statusSelect = wrapper.find('[data-testid="status-filter"]') as DOMWrapper<HTMLSelectElement>;
    await statusSelect.setValue("");
    expect(statusSelect.element.value).toEqual("");
    // 未完了に変更
    await statusSelect.setValue("false");
    expect(statusSelect.element.value).toEqual("false");
    // 完了に変更
    await statusSelect.setValue("true");
    expect(statusSelect.element.value).toEqual("true");
  });

  it("期限(以前)を入力", async () => {
    const startDueInput = wrapper.find('[data-testid="start-due"]') as DOMWrapper<HTMLInputElement>;
    await startDueInput.setValue("2025-01-01");
    expect(startDueInput.element.value).toEqual("2025-01-01");
  });

  it("期限(以降)を入力", async () => {
    const endDueInput = wrapper.find('[data-testid="end-due"]') as DOMWrapper<HTMLInputElement>;
    await endDueInput.setValue("2025-01-01");
    expect(endDueInput.element.value).toEqual("2025-01-01");
  });

  it("タイトルを入力", async () => {
    const titleInput = wrapper.find('[data-testid="title"]') as DOMWrapper<HTMLInputElement>;
    await titleInput.setValue("title");
    expect(titleInput.element.value).toEqual("title");
  });

  it("フィルターをリセット", async () => {
    const statusSelect = wrapper.find('[data-testid="status-filter"]') as DOMWrapper<HTMLSelectElement>;
    const startDueInput = wrapper.find('[data-testid="start-due"]') as DOMWrapper<HTMLInputElement>;
    const endDueInput = wrapper.find('[data-testid="end-due"]') as DOMWrapper<HTMLInputElement>;
    const titleInput = wrapper.find('[data-testid="title"]') as DOMWrapper<HTMLInputElement>;

    // フィルターを変更
    await statusSelect.setValue("false");
    await startDueInput.setValue("2025-01-01");
    await endDueInput.setValue("2025-01-02");
    await titleInput.setValue("title");
    // リセット
    await wrapper.find("[data-testid='reset']").trigger("click");
    expect(statusSelect.element.value).toEqual("");
    expect(startDueInput.element.value).toEqual("");
    expect(endDueInput.element.value).toEqual("");
    expect(titleInput.element.value).toEqual("");
  });
});

describe('ステータスでフィルター', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it("完了", async () => {
    wrapper = await mountShowTodo();

    // フィルター適用前
    const rows = wrapper.findAll('[data-testid="todo-row"]');
    expect(rows).toHaveLength(defaultTodosData.length);

    // フィルター適用
    mockedGet.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    const statusSelect = wrapper.find('[data-testid="status-filter"]') as DOMWrapper<HTMLSelectElement>;
    await statusSelect.setValue("true");
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(mockedGet).toBeCalledWith(
      "todos?status=true",
    );
    const newRows = wrapper.findAll('[data-testid="todo-row"]');
    expect(newRows).toHaveLength(1);
  });

  it("未完了", async () => {
    wrapper = await mountShowTodo();

    // フィルター適用前
    const rows = wrapper.findAll('[data-testid="todo-row"]');
    expect(rows).toHaveLength(defaultTodosData.length);

    // フィルター適用
    mockedGet.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[1]]
    });
    const statusSelect = wrapper.find('[data-testid="status-filter"]') as DOMWrapper<HTMLSelectElement>;
    await statusSelect.setValue("false");
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(mockedGet).toBeCalledWith(
      "todos?status=false",
    );
    const newRows = wrapper.findAll('[data-testid="todo-row"]');
    expect(newRows).toHaveLength(1);
  });
});

describe('期限(以前)でフィルター', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it("データあり", async () => {
    wrapper = await mountShowTodo();

    // フィルター適用前
    const rows = wrapper.findAll('[data-testid="todo-row"]');
    expect(rows).toHaveLength(defaultTodosData.length);

    // フィルター適用
    mockedGet.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    const startDueInput = wrapper.find('[data-testid="start-due"]') as DOMWrapper<HTMLInputElement>;
    await startDueInput.setValue("2025-01-01");
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(mockedGet).toBeCalledWith(
      "todos?start_due=2025-01-01",
    );
    const newRows = wrapper.findAll('[data-testid="todo-row"]');
    expect(newRows).toHaveLength(1);
  });
});

describe('期限(以降)でフィルター', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it("データあり", async () => {
    wrapper = await mountShowTodo();

    // フィルター適用前
    const rows = wrapper.findAll('[data-testid="todo-row"]');
    expect(rows).toHaveLength(defaultTodosData.length);

    // フィルター適用
    mockedGet.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[1]]
    });
    const endDueInput = wrapper.find('[data-testid="end-due"]') as DOMWrapper<HTMLInputElement>;
    await endDueInput.setValue("2025-01-02");
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(mockedGet).toBeCalledWith(
      "todos?end_due=2025-01-02",
    );
    const newRows = wrapper.findAll('[data-testid="todo-row"]');
    expect(newRows).toHaveLength(1);
  });
});

describe('タイトル名でフィルター', () => {
  let wrapper: VueWrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
  }
  );

  it("データあり", async () => {
    wrapper = await mountShowTodo();

    // フィルター適用前    expect(rows).toHaveLength(defaultTodosData.length);    expect(rows).toHaveLength(defaultTodosData.length);    expect(rows).toHaveLength(defaultTodosData.length);    expect(rows).toHaveLength(defaultTodosData.length);

    // フィルター適用
    mockedGet.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    const titleInput = wrapper.find('[data-testid="title"]') as DOMWrapper<HTMLInputElement>;
    titleInput.setValue("title1");
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(mockedGet).toBeCalledWith(
      "todos?title=title1",
    );
    const newRows = wrapper.findAll('[data-testid="todo-row"]');
    expect(newRows).toHaveLength(1);
  });
});
