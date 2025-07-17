<!-- components/ChatHeader.vue -->
<template>
  <header class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 shadow-md flex items-center justify-between sticky top-0 z-10 rounded-b-xl">
    <h1 class="text-xl sm:text-2xl font-bold">秋田県立大学AIアシスタント</h1>
    <button
        @click="startNewChat"
        class="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded-md mr-4 text-sm transition-colors"
        title="新しい会話を開始します"
      >
        新しい会話
      </button>
    <button
      @click="emit('logout')"
      class="bg-red-500 hover:bg-red-600 text-white font-semibold py-1 px-3 rounded-lg text-sm transition duration-200 shadow-md"
    >
      ログアウト
    </button>
  </header>
</template>

<script setup>
import { useChatStore } from '../stores/chat';
import { useAuthStore } from '../stores/auth';

const chatStore = useChatStore(); // ★ chatストアのインスタンスを取得
const authStore = useAuthStore();
// 親コンポーネントに'logout'イベントを通知するためのemit関数を定義
const emit = defineEmits(['logout']); 

/**
 * ★★★ 新しい会話を開始する関数を追加 ★★★
 */
const startNewChat = () => {
  // chat.jsストアのstartNewSessionアクションを呼び出す
  chatStore.startNewSession();
};

const handleLogout = () => {
  authStore.logout();
};
</script>

<style scoped>
/* Tailwind CSS handles most styling */
</style>
