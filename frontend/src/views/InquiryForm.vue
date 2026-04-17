<template>
  <form @submit.prevent="sendRequest" class="container d-flex flex-column align-items-center">
    <div class="mt-3 col-8">
      <p class="fw-bold">カテゴリ</p>
      <div class="mt-2">
        <label class="me-2">
          <input type="radio" value="要望" v-model="category" data-testid="request" required>要望
        </label>
        <label class="me-2">
          <input type="radio" value="エラー報告" v-model="category" data-testid="error" required>エラー報告
        </label>
        <label class="me-2">
          <input type="radio" value="その他" v-model="category" data-testid="other" required>その他
        </label>
      </div>
    </div>
    <div class="mt-3 col-8">
      <label class="fw-bold">詳細(最大256文字):</label>
      <textarea id="detail" maxlength="256" v-model="detail" class="form-control mt-2" data-testid="detail" required></textarea>
    </div>
    <button type="submit" class="btn btn-outline-secondary mt-3" data-testid="submit-button">送信</button>
  </form>
  <div class="container d-flex flex-column align-items-center">
    <p v-if="message" class="col-8 mt-3" :class="getResponseAlert(statusCode)" data-testid="message">{{ message }}</p>
  </div>
</template>
  
  <script>
  import { useSendInquiry } from './composables/useInquiry';
  import { getResponseAlert } from './utils/ui';
  
  export default {
    setup() {
      const { category, detail, statusCode, message, sendRequest } = useSendInquiry();
  
      return {
        category,
        detail,
        message,
        statusCode,
        getResponseAlert,
        sendRequest
      }
    }
  }
  </script>