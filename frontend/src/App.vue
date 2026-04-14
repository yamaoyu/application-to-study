<template>
  <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
  </head>
  <nav class="navbar navbar-expand-lg bd-navbar fixed-top bg-dark navbar-dark" v-if="(!MENU_SHOW_ROUTES.includes(this.$route.name))">
    <div class="container-fluid">
      <ul class="navbar-nav me-2" style="color: white;">
        <li class="nav-item" v-if="$router.currentRoute.value.name != 'Home'">
          <router-link class="nav-link bi-house" to="/home">HOME</router-link>
        </li>
      </ul>
      <button class="navbar-toggler" type="button" data-bs-toggle="offcanvas" data-bs-target="#offcanvasNavbar" aria-controls="offcanvasNavbar" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse">
        <ul class="navbar-nav me-auto mb-2 mb-lg-0">  
          <li class="nav-item">
            <router-link class="nav-link" to="/register/salary">月収登録</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register/activity">活動記録</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/view/activity/">実績確認</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register/todo">Todo登録</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/view/todo">Todo確認</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/user/info">ユーザー情報</router-link>
          </li>
          <li class="nav-item" v-if="!isAdmin">
            <router-link class="nav-link" to="/register/inquiry">問い合わせ</router-link>
          </li>
          <li class="nav-item" v-if="isAdmin">
            <router-link class="nav-link" to="/show/inquiry">問い合わせ確認</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" type="button" @click="userLogout()">ログアウト</a>
          </li>
        </ul>
      </div>
    </div>
    <!-- 小さい画面用メニュー -->
    <div class="offcanvas offcanvas-start bg-dark" id="offcanvasNavbar">
      <div class="offcanvas-header" style="color: white;">
          <h5 class="offcanvas-title">MENU</h5>
      </div>
      <ul class="offcanvas-body" style="color: white;">
        <li class="nav-item" v-if="$router.currentRoute.value.name != 'Home'" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/home">ホーム</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/salary">月収登録</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/activity/">活動記録</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/view/activity/">実績確認</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/todo">Todo登録</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/view/todo">Todo確認</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/user/info">ユーザー情報</router-link>
        </li>
        <li class="nav-item" v-if="!isAdmin" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/inquiry">問い合わせ</router-link>
        </li>
        <li class="nav-item" v-if="isAdmin" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/show/inquiry">問い合わせ確認</router-link>
        </li>
        <li class="nav-item">
          <a class="nav-link" type="button" @click="userLogout()">ログアウト</a>
        </li>
      </ul>
    </div>
  </nav>
  <p v-if="message" class="message">{{ message }}</p>
  <br>
  <BContainer>
    <router-view></router-view>
  </BContainer>
</template>

<script>
import { computed } from 'vue';
import { BContainer } from 'bootstrap-vue-next';
import { useLogout } from './views/composables/useAuth';

export default {
  components: {
    BContainer,
  },

  setup() {
    const { message, userLogout, roleStore } = useLogout();
    const MENU_SHOW_ROUTES = ["Login", "RegisterUser"];
    const isAdmin = computed(() => {
      return roleStore.getRole === "admin"
    });;

    return {
      message,
      userLogout,
      MENU_SHOW_ROUTES,
      isAdmin
    }
  }
}
</script>

<style>
div {
  white-space: pre-wrap;
}

.custom-navbar {
  background-color: navy;
  color: white;
}

#app {
  font-family: Avenir, Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  text-align: center;
  color: #2c3e50;
  margin-top: 60px;
}

@media (min-width: 992px) { /* lgサイズ以上 (PC表示) */
    #offcanvasNavbar {
        display: none !important;
    }
}

</style>
