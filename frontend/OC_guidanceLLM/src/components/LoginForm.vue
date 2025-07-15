<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <div>
      <label for="username" class="block text-sm font-medium text-gray-700">ユーザー名</label>
      <input
        type="text"
        id="username"
        v-model="username"
        :disabled="isLoading"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      />
    </div>
    <div>
      <label for="password" class="block text-sm font-medium text-gray-700">パスワード</label>
      <input
        type="password"
        id="password"
        v-model="password"
        :disabled="isLoading"
        required
        class="mt-1 block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm"
      />
    </div>
    <button
      type="submit"
      :disabled="isLoading"
      class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition duration-200"
    >
      <span v-if="isLoading" class="flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        ログイン中...
      </span>
      <span v-else>ログイン</span>
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';

// 親コンポーネントからisLoading propを受け取る
const props = defineProps({
  isLoading: {
    type: Boolean,
    default: false,
  },
});

// イベントを親コンポーネントにemitするための関数
const emit = defineEmits(['submit']);

const username = ref('');
const password = ref('');

const handleSubmit = () => {
  // 実際のバリデーションロジックを追加可能
  if (!username.value || !password.value) {
    alert('ユーザー名とパスワードを入力してください。'); // 実際はカスタムモーダルを使用
    return;
  }
  emit('submit', { username: username.value, password: password.value });
};
</script>

<style scoped>
/* Scoped styles for LoginForm.vue if needed, but Tailwind handles most */
</style>
