<!-- views/AuthView.vue -->
<template>
  <div class="flex flex-col items-center justify-center min-h-screen bg-gradient-to-br from-blue-500 to-indigo-600 p-4 sm:p-6">
    <div class="w-full max-w-md bg-white rounded-xl shadow-2xl p-6 sm:p-8 space-y-6">
      <h1 class="text-3xl sm:text-4xl font-extrabold text-center text-gray-800 mb-6">
        AIアシスタントへようこそ
      </h1>

      <!-- 認証フォームのコンテナ -->
      <div class="space-y-4">
        <!-- エラーメッセージ表示 -->
        <div v-if="authStore.errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded-md text-sm text-center" role="alert">
          {{ authStore.errorMessage }}
        </div>

        <!-- ログインフォームまたは登録フォームを表示 -->
        <LoginForm v-if="!isRegisterMode" @submit="handleLogin" :is-loading="authStore.isLoading" />
        <RegistrationForm v-else @submit="handleRegister" :is-loading="authStore.isLoading" />
      </div>

      <!-- フォーム切り替えボタン -->
      <div class="text-center mt-6">
        <button
          @click="toggleMode"
          :disabled="authStore.isLoading"
          class="text-blue-600 hover:text-blue-800 font-semibold transition-colors duration-200 text-sm sm:text-base"
        >
          {{ isRegisterMode ? 'アカウントをお持ちの方はこちら (ログイン)' : 'アカウントをお持ちでない方はこちら (新規登録)' }}
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'; // リアクティブな状態を管理するためのrefをインポート
import { useAuthStore } from '../stores/auth'; // 認証ストアをインポート
import LoginForm from '../components/LoginForm.vue'; // ログインフォームコンポーネントをインポート (後で実装)
import RegistrationForm from '../components/RegistrationForm.vue'; // 登録フォームコンポーネントをインポート (後で実装)

// Piniaストアのインスタンスを取得
const authStore = useAuthStore();

// ログインモードと登録モードを切り替えるためのリアクティブな状態
const isRegisterMode = ref(false);

/**
 * ログインフォームからの送信イベントを処理します。
 * @param {Object} credentials - ユーザーの認証情報
 */
const handleLogin = async (credentials) => {
  console.log('AuthView: Handling login submit.');
  await authStore.login(credentials);
  // ログイン後のリダイレクトはApp.vueのウォッチャーが処理します
};

/**
 * 登録フォームからの送信イベントを処理します。
 * @param {Object} details - ユーザーの登録情報
 */
const handleRegister = async (details) => {
  console.log('AuthView: Handling register submit.');
  await authStore.register(details);
  // 登録後のリダイレクトはApp.vueのウォッチャーが処理します
};

/**
 * ログイン/登録フォームの表示モードを切り替えます。
 */
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value;
  authStore.errorMessage = null; // モード切り替え時にエラーメッセージをクリア
  console.log('AuthView: Toggling form mode to register:', isRegisterMode.value);
};
</script>

<style scoped>
/* Scoped styles for AuthView.vue if needed, but Tailwind handles most */
</style>
