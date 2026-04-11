import { describe, it, expect, vi, beforeEach } from 'vitest';
import ShowTodo from '@/views/ShowTodo.vue';
import { mountComponent } from './vitest.setup';
import { apiClient } from '@/views/api/client';
import { flushPromises } from '@vue/test-utils';

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

const mountShowTodo = async ({
  todosMock = createResolvedMock(defaultTodosData),
} = {}) => {
  if (todosMock.type === "reject") {
    apiClient.get.mockRejectedValueOnce(todosMock.value);
  } else {
    apiClient.get.mockResolvedValueOnce(todosMock.value);
    }

  const wrapper = mountComponent(ShowTodo);
  await flushPromises();
  return wrapper;
};


describe('フィルターなし', () => {
    let wrapper;

    beforeEach(() => {
      vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
      }
    );

    it("データあり", async() =>{
      wrapper = await mountShowTodo();
      expect(apiClient.get).toBeCalledWith(
        "todos",
      );

      expect(wrapper.vm.todos).toEqual(defaultTodosData);
    });

    it("データなし", async() =>{
      const expectedMessage = "登録された情報はありません";
      wrapper = await mountShowTodo({
        todosMock: createRejectedMock(expectedMessage)
      });
      expect(apiClient.get).toBeCalledWith(
        "todos",            
      )
      expect(wrapper.vm.todoMsg).toBe(expectedMessage);
  });
});

describe('フィルターの操作', ()=>{
  let wrapper;

  beforeEach(() => {
      vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
      wrapper = mountComponent(ShowTodo);
      }
  );

  it("ステータスを選択", async() =>{
    // すべてに変更
    wrapper.vm.statusFilter = "すべて";
    expect(wrapper.vm.statusFilter).toEqual("すべて");
    // 未完了に変更
    wrapper.vm.statusFilter = "未完了";
    expect(wrapper.vm.statusFilter).toEqual("未完了");
    // 完了に変更
    wrapper.vm.statusFilter = "完了";
    expect(wrapper.vm.statusFilter).toEqual("完了");
  });

  it("期限(以前)を入力", async() =>{
    wrapper.vm.startDue = "2025-1-1";
    expect(wrapper.vm.startDue).toEqual("2025-1-1");
  });

  it("期限(以降)を入力", async() =>{
    wrapper.vm.endDue = "2025-1-1";
    expect(wrapper.vm.endDue).toEqual("2025-1-1");
  });

  it("タイトルを入力", async() =>{
    wrapper.vm.title = "title";
    expect(wrapper.vm.title).toEqual("title");
  });

  it("フィルターをリセット", async() =>{
    wrapper.vm.statusFilter = "完了";
    wrapper.vm.startDue = "2025-1-1";
    wrapper.vm.endDue = "2025-1-2";
    wrapper.vm.title = "title";
    // リセット
    await wrapper.find("[data-testid='reset']").trigger("click");
    expect(wrapper.vm.statusFilter).toEqual("");
    expect(wrapper.vm.startDue).toEqual("");
    expect(wrapper.vm.endDue).toEqual("");
    expect(wrapper.vm.title).toEqual("");
  });
});

describe('ステータスでフィルター', ()=>{
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
  );

  it("完了", async() =>{
    wrapper = await mountShowTodo();

    // フィルター適用前
    expect(wrapper.vm.todos).toEqual(defaultTodosData);

    // フィルター適用
    apiClient.get.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    wrapper.vm.statusFilter = "true";
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(apiClient.get).toBeCalledWith(
      "todos?status=true",
    );
    expect(wrapper.vm.todos).toEqual([defaultTodosData[0]]);
  });

  it("未完了", async() =>{
    wrapper = await mountShowTodo();

    // フィルター適用前
    expect(wrapper.vm.todos).toEqual(defaultTodosData);

    // フィルター適用
    apiClient.get.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[1]]
    });
    wrapper.vm.statusFilter = "false";
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(apiClient.get).toBeCalledWith(
      "todos?status=false",
    );
    expect(wrapper.vm.todos).toEqual([defaultTodosData[1]]);
  });
});

describe('期限(以前)でフィルター', ()=>{
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
  );

  it("データあり", async() =>{
    wrapper = await mountShowTodo();

    // フィルター適用前
    expect(wrapper.vm.todos).toEqual(defaultTodosData);
    
    // フィルター適用
    apiClient.get.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    wrapper.vm.startDue = "2025-1-1";
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(apiClient.get).toBeCalledWith(
      "todos?start_due=2025-1-1",
    );
    expect(wrapper.vm.todos).toEqual([defaultTodosData[0]]);
  });
});

describe('期限(以降)でフィルター', ()=>{
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
  );

  it("データあり", async() =>{
    wrapper = await mountShowTodo();

    // フィルター適用前
    expect(wrapper.vm.todos).toEqual(defaultTodosData);
    
    // フィルター適用
    apiClient.get.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[1]]
    });
    wrapper.vm.endDue = "2025-1-2";
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(apiClient.get).toBeCalledWith(
      "todos?end_due=2025-1-2",
    );
    expect(wrapper.vm.todos).toEqual([defaultTodosData[1]]);
  });
});

describe('タイトル名でフィルター', ()=>{
  let wrapper;

  beforeEach(() => {
    vi.resetAllMocks() //呼び出し履歴と実装両方をリセットし、モックを初期状態に戻す
    }
  );

  it("データあり", async() =>{
    wrapper = await mountShowTodo();

    // フィルター適用前
    expect(wrapper.vm.todos).toEqual(defaultTodosData);

    // フィルター適用
    apiClient.get.mockResolvedValue({
      status: 200,
      data: [defaultTodosData[0]]
    });
    wrapper.vm.title = "title1";
    await wrapper.find("[data-testid='apply']").trigger("click");
    expect(apiClient.get).toBeCalledWith(
      "todos?title=title1",
    );
    expect(wrapper.vm.todos).toEqual([defaultTodosData[0]]);
  });
});
