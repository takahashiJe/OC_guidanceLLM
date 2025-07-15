<!-- App.vue -->
<template>
  <div class="min-h-screen bg-gray-100 flex flex-col">
    <!-- router-view は現在のルートに対応するコンポーネントをレンダリングします -->
    <router-view />
  </div>
</template>

<script setup>
import { onMounted, watch } from 'vue'; // Vueのライフサイクルフックとリアクティブな監視機能をインポート
import { useRouter } from 'vue-router'; // Vue Routerのルーターインスタンスを取得するためのフックをインポート
import { useAuthStore } from './stores/auth'; // 認証状態を管理するPiniaストアをインポート (後で作成)
import { useChatStore } from './stores/chat'; // チャットセッションを管理するPiniaストアをインポート (後で作成)

// Piniaストアのインスタンスを取得
const authStore = useAuthStore();
const chatStore = useChatStore();
const router = useRouter(); // Vue Routerのルーターインスタンスを取得

// コンポーネントがマウントされた時に実行される処理
onMounted(() => {
  console.log('App.vue mounted. Initializing authentication and chat session.');
  authStore.initAuth(); // 認証状態を初期化（localStorageからトークンを読み込むなど）
  chatStore.initSession(); // チャットセッションを初期化（localStorageからセッションIDを読み込むなど）
});

// authStore.isLoggedIn の変更を監視
// ログイン状態に応じて適切なルートにリダイレクトします
watch(() => authStore.isLoggedIn, (newVal) => {
  if (newVal) {
    // ログイン済みであれば、チャット画面にリダイレクト
    console.log('User logged in. Redirecting to /chat');
    router.push('/chat');
  } else {
    // ログアウト状態であれば、ログイン画面にリダイレクト
    console.log('User logged out. Redirecting to /login');
    router.push('/login');
  }
}, { immediate: true }); // コンポーネントマウント時にも即座にウォッチャーを実行
</script>

<style>
/* Tailwind CSS を使用するため、ここでは基本的なスタイルのみ */
/* main.css で Tailwind CSS をインポートします */
</style>
