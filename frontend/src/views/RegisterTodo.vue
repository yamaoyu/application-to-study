<template>
  <h3>Todoの登録</h3>
  <form @submit.prevent="regitserTodos">
    <table class="table table-striped table-responsive">
      <thead class="table-dark">
        <tr>
            <th style="width: 5%;">No.</th>
            <th>内容</th>
            <th>期限</th>
            <th style="width: 8%;"></th>
            <th style="width: 8%;"></th>
        </tr>
      </thead>
      <tbody>
        <tr v-for="(todo, index) in todos" :key="index">
            <td class="text-center align-middle">{{ index + 1 }}</td>
            <td class="text-center align-middle todo-title" @click="openModal(todo, 'show')">{{ todo.title }}</td>
            <td class="text-center align-middle">{{ todo.due }}</td>
            <td>
              <input class="btn btn-outline-primary btn-sm" type="button" value="編集" @click="openModal(todo, 'edit')">
            </td>
            <td>
              <input class="btn btn-outline-danger btn-sm" type="button" value="削除" :data-testid="`del-todo-${index}`" @click="openModal(todo, 'delete')">
            </td>
        </tr>
        <tr class="table-secondary">
          <td colspan="5" class="text-center">
            <button 
              type="button" 
              class="btn btn-outline-primary"
              @click="openModal(todo, 'create')"
              :disabled="todos.length>=10"
              data-testid="add-todo"
            >
              + Todoを追加
            </button>
          </td>
        </tr>
      </tbody>
    </table>
    <button 
      type="submit" 
      class="btn btn-outline-secondary mt-3"
      :disabled="todos.length === 0||todos.length>=10"
      data-testid="submit-todo">登録
    </button>
  </form>
  <div class="container d-flex justify-content-center">
    <p v-if="message" class="mt-3 col-8" :class="getResponseAlert(statusCode)" data-testid="message">{{ message }}</p>
  </div>

  <BModal 
    v-model="showModal" 
    :title="modalTitle" 
    ok-title="OK" 
    cancel-title="閉じる" 
    @ok="closeModal(todos)"
    :ok-disabled="!validateTodo(todoAction, todo)"
    data-testid="modal-show"
  >
    <div v-if="todoAction==='show'||todoAction==='delete'">
      <div class="todo-detail">
          <p><strong>期限:</strong> {{ todo.due }}</p>
          <p><strong>タイトル:</strong>{{ todo.title }}</p>
          <p v-if="todo.detail"><strong>詳細:</strong> {{ todo.detail }}</p>
          <p v-else class="text-muted">Todoの詳細はありません</p>
      </div>
      <div v-if="todoAction==='delete'" style="color: red;">
        このTodoをリストから削除します
      </div>
    </div>
    <div v-else-if="todoAction==='edit'||todoAction==='create'">
      <div class="input-group">
          <label class="mt-3">
            タイトル
            <span :style="{ color: todo.title ? 'black' : 'red' }">*</span>
          </label>
          <div class="container d-flex justify-content-center">
            <div class="input-group">
                <input
                v-model="todo.title"
                class="form-control"
                :placeholder=todo.title
                maxlength="32"
                @input="titleError = !todo.title"
                data-testid="title"
                />
                <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
                {{ (todo.title || '').length }}/32
                </small>
            </div>
          <div v-if="titleError" style="color: red;">タイトルを入力してください</div>
        </div>
      </div>
      <div class="input-group mt-3">
        <span>詳細</span>
        <div class="container d-flex justify-content-center">
          <div class="input-group">
            <textarea
              v-model="todo.detail"
              class="form-control"
              :placeholder=todo.detail
              maxlength="200"
              rows="3"
              data-testid="detail"
              >
            </textarea>
            <small class="form-text text-muted position-absolute" style="right: 8px; bottom: -20px;">
              {{ (todo.detail || '').length }}/200
            </small>
          </div>
        </div>
      </div>
      <div class="input-group mt-3">
        <label>
          期限
          <span :style="{ color: todo.due ? 'black' : 'red' }">*</span>
        </label>
        <div class="container d-flex justify-content-center">
          <div class="input-group">
              <input
              type="date"
              v-model="todo.due"
              class="form-control col-2"
              :min="today"
              @input="dueError = !todo.due"
              data-testid="due"
              />
          </div>
        </div>
        <div v-if="dueError" style="color: red;">期限を入力してください</div>
      </div>
    </div>
  </BModal>
</template>

<script>
import { ref, watch } from 'vue';
import { getToday } from './utils/date';
import { getResponseAlert } from './utils/ui';
import { useRegisterTodos } from './composables/useTodo';
import { validateTodo } from './utils/todoValidation';
import { BModal } from 'bootstrap-vue-next';
import { useTodoModal } from './composables/useTodoModal';

export default {
  components:{
    BModal
  },

  setup() {
    const titleError = ref(""); // todo編集時、タイトルに入力がない場合のメッセージを表示
    const dueError = ref(""); // todo編集時、期限に入力がない場合のメッセージを表示
    const today = getToday();
    const { showModal, modalTitle, todoAction, todo, openModal, closeModal } = useTodoModal();
    const { todos, message, statusCode, regitserTodos } = useRegisterTodos();

    watch(() => todos.value.length, () => {
      if (todos.value.length>=10){
        message.value = "一度に登録できるのは10件までです";
      } else if (message.value==="一度に登録できるのは10件までです") {
        message.value = "";
      }
    });

    return {
      message,
      todo,
      todos,
      todoAction,
      statusCode,
      showModal,
      modalTitle,
      titleError,
      dueError,
      today,
      regitserTodos,
      getResponseAlert,
      openModal,
      validateTodo,
      closeModal
    }
  }
}
</script>