<template>
  <form @submit.prevent="handleSubmit" class="space-y-4">
    <div class="relative">
      <input
        type="text"
        id="login-username"
        v-model="username"
        placeholder="ユーザー名"
        :disabled="isLoading"
        required
        class="block w-full px-5 py-3.5 bg-zinc-800 border-transparent rounded-xl text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-white"
      />
    </div>

    <div class="relative">
      <input
        type="password"
        id="login-password"
        v-model="password"
        placeholder="パスワード"
        :disabled="isLoading"
        required
        class="block w-full px-5 py-3.5 bg-zinc-800 border-transparent rounded-xl text-white placeholder-zinc-400 focus:outline-none focus:ring-2 focus:ring-white"
      />
    </div>

    <button
      type="submit"
      :disabled="isLoading"
      class="w-full flex justify-center py-3.5 px-4 rounded-xl text-base font-semibold transition-colors duration-300
             bg-zinc-800 text-white
             hover:bg-zinc-700"
    >
      <span v-if="isLoading" class="flex items-center">
        <svg class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle><path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path></svg>
        処理中...
      </span>
      <span v-else>ログイン</span>
    </button>
  </form>
</template>

<script setup>
import { ref } from 'vue';

const props = defineProps({
  isLoading: { type: Boolean, default: false },
});
const emit = defineEmits(['submit']);

const username = ref('');
const password = ref('');

const handleSubmit = () => {
  if (!username.value || !password.value) return;
  emit('submit', { username: username.value, password: password.value });
};
</script>