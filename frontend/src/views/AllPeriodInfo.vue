<template>
<div style="white-space: pre-wrap;" v-if="message" class="message">
    <h3>全期間の活動実績</h3>
    <p v-if="message" class="message">{{ message }}</p>
</div>
<div>
    <router-link to="/register/salary">月収登録</router-link>
</div>
<div>
    <router-link to="/register/target">目標時間登録</router-link>
</div>
<div>
    <router-link to="/register/actual">活動時間登録</router-link>
</div>
<div>
    <router-link to="/finish/activity">活動を終了</router-link>
</div>
<div>
    <router-link to="/view/month-activities">月ごとの活動記録</router-link>
</div>
<div>
    <router-link to="/home">ホームへ戻る</router-link>
</div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import store from '@/store';

export default {
setup() {
    const message = ref("")
    const router = useRouter()
    const activities = ref([])


    onMounted( async() =>{
    try{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/total';
        const response = await axios.get(url,
                                        {headers: {Authorization: `${store.state.tokenType} ${store.state.accessToken}`}})
        if (response.status===200){
            message.value = [`合計:${response.data.total_income}万円\n`,
                            `内訳\n`,
                            `月収:${response.data.total_salary}万円\n`,
                            `ボーナス合計:${response.data.total_bonus}万円\n`,
                            `目標達成日数:${response.data.success_days}日\n`,
                            `目標未達成日数:${response.data.fail_days}日`].join('');
        }
    } catch (error){
        if (error.response){
          switch (error.response.status){
            case 401:
                router.push(
                    {"path":"/login",
                    "query":{message:"再度ログインしてください"}
                })
                break;
            case 422:
                message.value = error.response.data.error;
                break;
            case 500:
                message.value =  "情報の取得に失敗しました"
                break;
            default:
                message.value = error.response.data.detail;
          }
        } else if (error.request){
            message.value =  "リクエストがサーバーに到達できませんでした"
        } else {
            message.value =  "不明なエラーが発生しました。管理者にお問い合わせください"
        }
       }
      }
    )
    return {
        message,
        activities
        }
     } 
    }

</script>