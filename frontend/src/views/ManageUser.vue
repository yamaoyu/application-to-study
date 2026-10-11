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
            <input v-model="createdAt" type="date" class="form-control" data-testid="start-due">
          </div>
          <div class="col-md-6">
            <label class="form-label">最終ログイン</label>
            <input v-model="lastActiveAt" type="date" class="form-control" data-testid="end-due">
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
            <select v-model="userRole" class="form-select" data-testid="status-filter">
              <option value="">すべて</option>
              <option value="admin">管理者</option>
              <option value="general">一般</option>
            </select>
          </div>
      </div>
      <div class="mt-3">
        <label>ユーザー名</label>
        <input v-model="username" type="text" class="form-control" data-testid="title">
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
          </tr>
        </thead>
        <tbody v-for="(user, name) in users" :key="name">
          <tr>
            <td :data-testid="`user-${name}`">{{ user.username }}</td>
            <td>{{ formatJstDate(user.created_at) }}</td>
            <td>{{ formatJstDate(user.last_active_at) }}</td>
            <td>{{ user.role }}</td>
            <td>{{ user.status }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </template>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="mt-3 col-8" data-testid="message">{{ message }}</p>
  </div>
</template>
  
<script lang="ts">

import { onMounted, ref } from 'vue';
import { useGetUsersList } from './composables/useManageUser';
import { BButton } from 'bootstrap-vue-next';

export default {
  components: {
    BButton
  },

  setup() {
    const {
        getUsers,
        users,
        userStatus,
        userRole,
        lastActiveAt,
        createdAt,
        username,
        message
    } = useGetUsersList();

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
      users,
      message,
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
