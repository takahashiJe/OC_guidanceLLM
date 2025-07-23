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

    <div class="flex-1 flex flex-col space-y-4 overflow-y-auto">
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

      <div class="pt-4 space-y-4">
        <div>
          <h3 class="px-2 text-sm font-semibold text-gray-500">試してみよう</h3>
          <div class="mt-2 space-y-1">
            <button v-for="prompt in suggestedPrompts" :key="prompt" @click="sendSuggestedPrompt(prompt)"
              class="w-full text-left flex items-center gap-3 px-3 py-2 text-sm font-medium text-gray-700 rounded-lg hover:bg-gray-100 transition-colors duration-200"
            >
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <span>{{ prompt }}</span>
            </button>
          </div>
        </div>
        <div>
            <div class="p-3 rounded-lg bg-indigo-50 border border-indigo-200 text-xs text-indigo-800 leading-relaxed">
              <p class="font-semibold mb-1">※作者より</p>
              <p>APU-NaviAIについて聞くと「”話せる”AIとして開発されました」のように答えることがありますが，時間がなくて音声対話機能はつけれませんでした．すみません．</p>
            </div>
        </div>
      </div>
      </div>

    <div class="shrink-0 pt-4">
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
        <p class="text-gray-600 mb-6">現在の会話の履歴は全て消えます。本当に新規作成しますか？</p>
        <div class="flex justify-center space-x-4">
          <button @click="confirmNewChat" class="w-full bg-zinc-800 hover:bg-zinc-700 text-white font-semibold py-2.5 px-6 rounded-lg transition-colors duration-200">はい、作成します</button>
          <button @click="cancelNewChat" class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2.5 px-6 rounded-lg transition-colors duration-200">いいえ</button>
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

const isConfirmingNewChat = ref(false);

const showConfirmation = () => {
  isConfirmingNewChat.value = true;
};

const confirmNewChat = () => {
  chatStore.startNewSession();
  isConfirmingNewChat.value = false;
  emit('close');
};

const cancelNewChat = () => {
  isConfirmingNewChat.value = false;
};

const handleLogout = () => {
  emit('close');
  authStore.logout();
  router.push('/login');
};

// ★★★ ここからが追加箇所 ★★★
const suggestedPrompts = [
  'カフェテリアではどんな出展がある？',
  '今，山口研ではどんな出展を行なっている？',
  'APU-NaviAIの名前の由来は？'
];

const sendSuggestedPrompt = (prompt) => {
  chatStore.sendMessage(prompt);
  // モバイル表示の際にサイドバーを閉じる
  emit('close');
};
// ★★★ ここまでが追加箇所 ★★★

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