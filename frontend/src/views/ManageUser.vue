<template>
  <h2 class="mb-5">ユーザー管理メニュー</h2>

  <!-- フィルターフォーム -->
  <div class="card mb-3">
    <div class="card-header bg-light">
      <h5 class="card-title mt-2 clickable" @click="toggleFormVisibility">
        ユーザーの絞り込み
        <span v-if="isFormVisible">▲</span>
        <span v-else>▼</span>
      </h5>
    </div>
    <div class="card-body collapse" :class="{ 'show': isFormVisible }">
      <div class="row g-2">
          <div class="col-md-6">
            <label class="form-label">作成日</label>
            <input v-model="createdAt" type="date" class="form-control" data-testid="created-at-filter">
          </div>
          <div class="col-md-6">
            <label class="form-label">最終ログイン</label>
            <input v-model="lastActiveAt" type="date" class="form-control" data-testid="last-active-at-filter">
          </div>
      </div>
      <div class="row g-2">
          <div class="col-md-6">
            <label class="form-label">ステータス</label>
            <select v-model="userStatus" class="form-select" data-testid="status-filter">
              <option value="">すべて</option>
              <option value="active">有効</option>
              <option value="suspended">停止済み</option>
            </select>
          </div>
          <div class="col-md-6">
            <label class="form-label">ロール</label>
            <select v-model="userRole" class="form-select" data-testid="role-filter">
              <option value="">すべて</option>
              <option value="admin">管理者</option>
              <option value="general">一般</option>
            </select>
          </div>
      </div>
      <div class="mt-3">
        <label>ユーザー名</label>
        <input v-model="username" type="text" class="form-control" data-testid="username-filter">
      </div>
      <div class="d-flex justify-content-end mt-3">
        <BButton variant="secondary" class="me-2" data-testid="reset" @click="resetFilter">条件リセット</BButton>
        <BButton variant="primary" data-testid="apply" @click="getUsers">フィルター適用</BButton>
      </div>
    </div>
  </div>
  <template v-if="Object.keys(users)">
    <div class="table-responsive">
      <table class="table table-striped">
        <thead class="table-dark">
          <tr>
            <th>名前</th>
            <th>作成日</th>
            <th>最終ログイン</th>
            <th>ロール</th>
            <th>ステータス</th>
            <th></th>
          </tr>
        </thead>
        <tbody v-for="(user, index) in users" :key="index">
          <tr data-testid="user-row">
            <td :data-testid="`user-${index}`">{{ user.username }}</td>
            <td>{{ formatJstDate(user.created_at) }}</td>
            <td>{{ formatJstDate(user.last_active_at) }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.status }}</td>
            <td>
              <div class="dropdown">
                <button
                  type="button"
                  class="btn btn-sm btn-light border"
                  data-bs-toggle="dropdown"
                  aria-expanded="false"
                  :aria-label="`${user.username}の操作`"
                  title="操作"
                >
                  ⋮
                </button>

                <ul class="dropdown-menu dropdown-menu-end">
                  <li>
                    <button class="dropdown-item" type="button" :data-testid="`change-role-${index}`"  @click="handleRoleChange(user)">
                      {{ user.role === "general" ? "管理者権限へ変更" : "一般権限へ変更" }}
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" type="button" :data-testid="`change-status-${index}`" @click="handleStatusChange(user)">
                      {{ user.status === "active" ? "停止する" : "有効化する" }}
                    </button>
                  </li>
                  <li>
                    <button class="dropdown-item" type="button" :data-testid="`reset-password-${index}`" @click="confirmPasswordReset(user)">
                      パスワードリセット
                    </button>
                  </li>
                </ul>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  <div v-if="message" class="container d-flex flex-column align-items-center">
    <p class="mt-3 col-8 alert" :class="isSuccess ? 'alert-success' : 'alert-warning'" data-testid="message">{{ message }}</p>
  </div>

  <BModal
    v-model="showPasswordResetModal"
    title="パスワードリセット確認"
    cancel-title="キャンセル"
    data-testid="modal-show"
    @ok="handlePasswordReset()"
  >
    <p v-if="selectedUser">
      {{ selectedUser.username }} のパスワードをリセットします。よろしいですか？
    </p>
  </BModal>
</template>
  
<script lang="ts">

import { onMounted, ref } from 'vue';
import { useGetUsersList, useChangeRole, useChangeStatus, useResetPassword } from './composables/useManageUser';
import { BButton, BModal } from 'bootstrap-vue-next';
import { UserItem } from './types/admin';

export default {
  components: {
    BButton,
    BModal
  },

  setup() {
    const message = ref<string>("");
    const showPasswordResetModal = ref<boolean>(false);
    const selectedUser = ref<UserItem | null>();
    const isSuccess = ref<boolean>(false);
    const {
        getUsers,
        users,
        userStatus,
        userRole,
        lastActiveAt,
        createdAt,
        username
    } = useGetUsersList(message, isSuccess);
    const { changeRole } = useChangeRole(message, isSuccess);
    const { changeStatus } = useChangeStatus(message, isSuccess);
    const { resetPassword } = useResetPassword(message, isSuccess);

    const formatJstDate = (value?: string | null) => {
      if (!value) return "-";

      return new Intl.DateTimeFormat("ja-JP", {
        timeZone: "Asia/Tokyo",
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
      }).format(new Date(value));
    };

    const isFormVisible = ref<boolean>(false);

    const toggleFormVisibility = () => {
      isFormVisible.value = !isFormVisible.value;
    };

    const handleRoleChange = async (user: UserItem) => {
      await changeRole(user.role, user.username);
      await getUsers();
    }

    const handleStatusChange = async (user: UserItem) => {
      await changeStatus(user.status, user.username);
      await getUsers();
    };

    const handlePasswordReset = async () => {
      if (!selectedUser.value) return;
      await resetPassword(selectedUser.value.username);
      selectedUser.value = null;
      showPasswordResetModal.value = false;
      await getUsers();
    }

    const confirmPasswordReset = async (user: UserItem) => {
      showPasswordResetModal.value = true;
      selectedUser.value = user;
    }

    const resetFilter = () => {
      userStatus.value = "";
      userRole.value = "";
      lastActiveAt.value = "";
      createdAt.value = "";
      username.value = "";
    };

    onMounted( async()=>{
      await getUsers();
    });

    return {
      getUsers,
      handleRoleChange,
      handleStatusChange,
      handlePasswordReset,
      confirmPasswordReset,
      users,
      message,
      isSuccess,
      showPasswordResetModal,
      selectedUser,
      userStatus,
      userRole,
      lastActiveAt,
      createdAt,
      username,
      isFormVisible,
      formatJstDate,
      toggleFormVisibility,
      resetFilter
    }
  }
}
</script>
