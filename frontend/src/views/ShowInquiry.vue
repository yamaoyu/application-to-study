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
import { onMounted } from 'vue';
import { useGetInquiries } from './composables/useInquiry';

export default{
    setup() {
        const BOOL_TO_STATUS = { "true":"確認済", "false":"未確認" };
        const { inquiries, message, fetchInquries } = useGetInquiries();

        onMounted( async()=>{
            await fetchInquries();
        });

        return {
            inquiries,
            message,
            BOOL_TO_STATUS,
            message,
            fetchInquries
        }
    }
}

</script>