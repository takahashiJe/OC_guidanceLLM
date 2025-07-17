<template>
  <div class="h-screen w-screen bg-white flex">
    
    <Sidebar class="hidden lg:flex" />

    <main class="flex-1 flex flex-col h-full overflow-hidden">
      
      <div class="lg:hidden p-4 border-b shrink-0">
        <h1 class="text-lg font-semibold">AI Chat</h1>
      </div>
      
      <div class="flex-1 relative">
        <RouterView class="absolute inset-0" />
      </div>
    </main>
  </div>
</template>

<script setup>
import { onMounted } from 'vue';
import { useAuthStore } from './stores/auth';
import { useChatStore } from './stores/chat';
import Sidebar from './components/Sidebar.vue';
import { RouterView } from 'vue-router';

const authStore = useAuthStore();
const chatStore = useChatStore();

// コンポーネントがマウントされたとき（＝アプリ起動時）に実行
onMounted(() => {
  console.log('App.vue mounted. Initializing session and checking token.');
  
  // 能動的にトークンの有効性をチェック
  authStore.checkTokenValidity();

  // ログインしている場合のみチャットセッションを初期化
  if (authStore.isAuthenticated) {
    chatStore.initSession();
  }
});

// ★★★ ログイン状態を監視していたwatchブロックを削除 ★★★
// ナビゲーションはrouter/index.jsのナビゲーションガードが担当するため不要
</script>

<style>
/* main.cssでTailwind CSSをインポート */
</style>