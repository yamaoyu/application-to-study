<template>
    <div class="container">
        <h2 class="mb-4">問い合わせ一覧</h2>
        <template v-if="inquiries.length">
            <table class="table table-striped table-responsive">
                <thead class="table-dark">
                    <tr>
                        <th style="width: 5%;">No.</th>
                        <th>カテゴリ</th>
                        <th>内容</th>
                        <th>問い合わせ日</th>
                        <th>ステータス</th>
                    </tr>
                </thead>
                <tbody v-for="(inquiry, index) in inquiries" :key="index">
                    <tr>
                        <td class="text-center align-middle" :data-testid="`index-${index}`">{{ index + 1 }}</td>
                        <td class="text-center align-middle inquiry-title" :data-testid="`category-${index}`">{{ inquiry.category }}</td>
                        <td class="text-center align-middle" :data-testid="`detail-${index}`">{{ inquiry.detail }}</td>
                        <td class="text-center align-middle" :data-testid="`date-${index}`">{{ inquiry.date }}</td>
                        <td class="text-center align-middle fw-bold" :class="inquiry.is_checked===true ? 'text-success' : 'text-danger' " :data-testid="`is_checked-${index}`">{{ BOOL_TO_STATUS[inquiry.is_checked] }}</td>
                    </tr>
                </tbody>
            </table>
        </template>

        <div v-if="!inquiries.length" class="alert alert-warning" data-testid="message">
            {{ message }}
        </div>
    </div>
</template>

<script>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/store/authenticate';
import axios from 'axios';
import { jwtDecode } from 'jwt-decode';
import { commonError, verifyRefreshToken } from './lib'

export default{
    setup() {
        const inquiries = ref([]);
        const router = useRouter();
        const authStore = useAuthStore();
        const message = ref("");
        const { handleError } = commonError(message, router);
        const BOOL_TO_STATUS = { "true":"確認済", "false":"未確認" };

        const sendRequest = async() =>{
            const url = import.meta.env.VITE_BACKEND_URL + 'inquiries';
            const response = await axios.get(url,
                                            {headers: {Authorization: authStore.getAuthHeader}})
            inquiries.value = response.data;
        };

        const getInquiries = async() =>{
            try{
                await sendRequest();
            } catch (error){
                if (error.response?.status === 403) {
                    message.value = error.response.data.detail;
                } else if (error.response?.status === 401) {
                    try {
                        // リフレッシュトークンを検証して新しいアクセストークンを取得
                        const tokenResponse = await verifyRefreshToken();
                            // 新しいアクセストークンをストアに保存
                            await authStore.setAuthData(
                            tokenResponse.data.access_token,
                            tokenResponse.data.token_type,
                            jwtDecode(tokenResponse.data.access_token).exp
                        );
                        // 再度リクエストを送信
                        await sendRequestForInquiries();
                    } catch (refreshError) {
                        router.push({
                        path: "/login",
                        query: { message: "再度ログインしてください" }
                        });
                    }            
                } else {
                    handleError(error)
                }
            }
        };

        onMounted( async()=>{
            await getInquiries();
        });

        return {
            inquiries,
            message,
            BOOL_TO_STATUS,
            message,
            getInquiries
        }
    }
}

</script>