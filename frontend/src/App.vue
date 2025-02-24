<template>
  <head>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons/font/bootstrap-icons.css" rel="stylesheet">
  </head>
  <nav class="navbar navbar-expand-lg bd-navbar fixed-top bg-dark navbar-dark" v-if="this.$route.name != 'Login' && this.$route.name != 'RegisterUser'">
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
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              活動登録
            </a>
            <ul class="dropdown-menu">
              <li class="dropdown-item">
                <router-link class="nav-link" style="color: black;" to="/register/target">目標時間</router-link>
              </li>
              <li class="dropdown-item">
                <router-link class="nav-link" style="color: black;" to="/register/actual">活動時間</router-link>
              </li>
              <li class="dropdown-item">
                <router-link class="nav-link" style="color: black;" to="/finish/activity">活動終了</router-link>
              </li>
            </ul>            
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register/salary">月収登録</router-link>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register/todo">Todo登録</router-link>
          </li>
          <li class="nav-item dropdown">
            <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
              実績確認
            </a>
            <ul class="dropdown-menu">
              <li class="dropdown-item"><router-link class="nav-link" style="color: black;" to="/view/month-activities">月別</router-link></li>
              <li class="dropdown-item"><router-link class="nav-link" style="color: black;" to="/view/all-activities">全期間</router-link></li>
            </ul>
          </li>
          <li class="nav-item">
            <router-link class="nav-link" to="/register/inquiry">問い合わせ</router-link>
          </li>
          <li class="nav-item">
            <a class="nav-link" type="button" @click="logout()">ログアウト</a>
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
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            活動登録
          </a>
          <ul class="dropdown-menu" data-bs-dismiss="offcanvas">
            <li class="dropdown-item">
              <router-link class="nav-link" style="color: black;" to="/register/target">目標時間</router-link>
            </li>
            <li class="dropdown-item">
              <router-link class="nav-link" style="color: black;" to="/register/actual">活動時間</router-link>
            </li>
            <li class="dropdown-item">
              <router-link class="nav-link" style="color: black;" to="/finish/activity">活動終了</router-link>
            </li>
          </ul>            
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/salary">月収登録</router-link>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/todo">Todo登録</router-link>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" href="#" role="button" data-bs-toggle="dropdown" aria-expanded="false">
            実績確認
          </a>
          <ul class="dropdown-menu" data-bs-dismiss="offcanvas">
            <li class="dropdown-item"><router-link class="nav-link" style="color: black;" to="/view/month-activities">月別</router-link></li>
            <li class="dropdown-item"><router-link class="nav-link" style="color: black;" to="/view/all-activities">全期間</router-link></li>
          </ul>
        </li>
        <li class="nav-item" data-bs-dismiss="offcanvas">
          <router-link class="nav-link" to="/register/inquiry">問い合わせ</router-link>
        </li>
        <li class="nav-item">
          <a class="nav-link" type="button" @click="logout()">ログアウト</a>
        </li>
      </ul>
    </div>
  </nav>
  <p v-if="logout_msg" class="logout_msg">{{ logout_msg }}</p>
  <BContainer>
    <router-view></router-view>
  </BContainer>
</template>

<script>
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { BContainer } from 'bootstrap-vue-next';

export default {
  components: {
    BContainer,
  },

  setup() {
    const router = useRouter()
    const authStore = useAuthStore()
    const logout_msg = ref("")

    const logout = async() =>{
      try{
        // デバイス情報を取得 HTTPSにするまでの一時的な対応としてplatform(非推奨)を使用
        const device = navigator.platform || "unknown";
        const logout_url = process.env.VUE_APP_BACKEND_URL + 'logout'
        const logout_res = await axios.post(logout_url, 
              {
                device: device
              },
              {
                headers: {Authorization: authStore.getAuthHeader},
                withCredentials: true
              }
        )
        if (logout_res.status===200){
          authStore.clearAuthData()
          router.push(
                  {"path":"/login",
                    "query":{message:"ログアウトしました"}
                  })
        }
      } catch(logout_err){
        if (logout_err.response){
            switch (logout_err.response.status){
              case 401:
                router.push(
                  {"path":"/login",
                    "query":{message:"再度ログインしてください"}
                  })
                break;
              case 404:
              case 500:
                logout_msg.value = logout_err.response.data.detail;
                break;
              default:
                logout_msg.value = "ログアウトに失敗しました";}
          } else if (logout_err.request){
            logout_msg.value =  "リクエストがサーバーに到達できませんでした"
          } else {
            logout_msg.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
          }
      }
    }
    
    return {
      logout_msg,
      logout
    }
  }
}
</script>

<style>
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
