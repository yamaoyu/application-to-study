<template>
<h3>全期間の活動実績</h3>
<div v-if="message" class="message">
    <p v-if="message" class="message">{{ message }}</p>
</div>
<div class="container p-4" v-if="response">
    <div class="row justify-content-center mb-4">
        <div class="col-8 ">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">合計</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(response)" class="h3 fw-bold text-center">{{ response.data.total_income }}</span>
            万円
            </div>
        </div>
        </div>
    </div>
    <div class="row">
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">月収</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold">{{ response.data.total_salary }}</span>
            <span class="small">万円</span>
            </div>
        </div>
        </div>
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">ボーナス+ペナルティ</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span :class="getAdjustmentColors(response)" class="h3 fw-bold">{{ response.data.pay_adjustment }}</span>
            <span class="small">万円</span>
            </div>
        </div>
        </div>
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">ボーナス</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-success">{{ response.data.total_bonus }}</span>
            <span class="small">万円</span>
            </div>
        </div>
        </div>
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">ペナルティ</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-danger">{{ response.data.total_penalty }}</span>
            <span class="small">万円</span>
            </div>
        </div>
        </div>
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">達成日数</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-success">{{ response.data.success_days }}</span>
            <span class="small">日</span>
            </div>
        </div>
        </div>
        <div class="col-6">
        <div class="bg-white p-4 rounded shadow">
            <h3 class="small">未達成日数</h3>
            <div class="d-flex align-items-baseline justify-content-center">
            <span class="h3 fw-bold text-danger">{{ response.data.fail_days }}</span>
            <span class="small">日</span>
            </div>
        </div>
        </div>
    </div>
</div>
</template>

<script>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import { getStatusColors, getAdjustmentColors } from './lib/index';

export default {
setup() {
    const message = ref("")
    const router = useRouter()
    const response = ref()
    const authStore = useAuthStore()

    onMounted( async() =>{
    try{
        const url = process.env.VUE_APP_BACKEND_URL + 'activities/total';
        response.value = await axios.get(url,
                                        {headers: {Authorization: authStore.getAuthHeader}})
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
                message.value = error.response.data.detail;
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
        response,
        getStatusColors,
        getAdjustmentColors
        }
     } 
    }

</script>