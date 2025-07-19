<template>
  <aside class="bg-white w-full h-full p-4 flex flex-col border-r border-gray-200">
    <div class="flex items-center space-x-3 shrink-0 mb-6">
      <button
        @click="$emit('close')"
        class="lg:hidden flex items-center justify-center w-8 h-8 bg-white rounded-full shadow text-gray-600 hover:bg-gray-100 transition-colors"
        aria-label="サイドバーを閉じる"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2.5">
          <path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" />
        </svg>
      </button>
      <h2 class="font-bold text-lg text-gray-800">メニュー</h2>
    </div>

    <div class="flex-1 flex flex-col space-y-4">
      <button
        @click="showConfirmation"
        class="flex items-center justify-between w-full bg-gray-100 hover:bg-gray-200 text-gray-800 font-semibold py-2 px-4 rounded-full transition-colors duration-200"
      >
        <span>チャットを新規作成</span>
        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
          <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
          <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
        </svg>
      </button>
    </div>

    <div class="shrink-0">
      <button
        @click="handleLogout"
        class="flex items-center space-x-3 w-full text-left text-gray-600 hover:bg-gray-100 py-2 px-4 rounded-lg transition-colors duration-200"
      >
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
        </svg>
        <span class="font-semibold">ログアウト</span>
      </button>
    </div>
  </aside>

  <transition name="modal-fade">
    <div v-if="isConfirmingNewChat" class="fixed inset-0 z-50 flex items-center justify-center">
      <div @click="cancelNewChat" class="absolute inset-0 bg-white/70 backdrop-blur-sm"></div>
      
      <div class="relative bg-white rounded-2xl shadow-xl p-6 sm:p-8 w-11/12 max-w-md text-center">
        <h3 class="text-lg font-bold text-gray-800 mb-4">チャットを新規作成</h3>
        <p class="text-gray-600 mb-6">
          現在の会話の履歴は全て消えます。本当に新規作成しますか？
        </p>
        <div class="flex justify-center space-x-4">
          <button @click="confirmNewChat" class="w-full bg-zinc-800 hover:bg-zinc-700 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors duration-200">
            はい、作成します
          </button>
          <button @click="cancelNewChat" class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2.5 px-6 rounded-lg transition-colors duration-200">
            いいえ
          </button>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup>
import { ref } from 'vue';
import { useChatStore } from '../stores/chat';
import { useAuthStore } from '../stores/auth';
import { useRouter } from 'vue-router';

const emit = defineEmits(['close']);
const chatStore = useChatStore();
const authStore = useAuthStore();
const router = useRouter();

// 確認モーダルの表示状態を管理
const isConfirmingNewChat = ref(false);

// モーダルを表示する
const showConfirmation = () => {
  isConfirmingNewChat.value = true;
};

// 「はい」が押されたときの処理
const confirmNewChat = () => {
  chatStore.startNewSession();
  isConfirmingNewChat.value = false; // モーダルを閉じる
  emit('close'); // サイドバーを閉じる
};

// 「いいえ」または背景がクリックされたときの処理
const cancelNewChat = () => {
  isConfirmingNewChat.value = false; // モーダルを閉じる
};

const handleLogout = () => {
  emit('close');
  authStore.logout();
  router.push('/login');
};
</script>

<style scoped>
.modal-fade-enter-active,
.modal-fade-leave-active {
  transition: opacity 0.3s ease;
}

.modal-fade-enter-from,
.modal-fade-leave-to {
  opacity: 0;
}
</style>