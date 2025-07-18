<template>
  <div :class="layoutClasses">
    <div class="h-screen w-screen hidden lg:grid lg:grid-cols-[auto_1fr]">
      <Sidebar v-if="!isAuthRoute" />
      <main class="overflow-y-auto">
        <RouterView />
      </main>
    </div>

    <div class="h-screen w-screen flex flex-col lg:hidden">
      <header v-if="!isAuthRoute" class="p-2 border-b flex items-center justify-between shrink-0 bg-white z-10">
        <button @click="isSidebarOpen = true" class="p-2 rounded-full hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-700">APU-NaviAI</h1>
        <img src="@/assets/app-icon.png" alt="App Icon" class="w-8 h-8 rounded-full">
      </header>

      <main :class="mainContentClasses">
        <RouterView />
      </main>
      
      <transition name="fade">
        <div 
          v-if="isSidebarOpen" 
          @click="isSidebarOpen = false" 
          class="fixed inset-0 bg-black bg-opacity-50 z-40"
        ></div>
      </transition>
      <transition name="slide-left">
        <div v-if="isSidebarOpen" class="fixed top-0 left-0 w-3/4 max-w-sm h-full bg-[#f0f4f9] shadow-xl z-50">
          <Sidebar @close="isSidebarOpen = false" />
        </div>
      </transition>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue';

const isSidebarOpen = ref(false);
const route = useRoute();

// ★★★ ここを修正 ★★★
// 現在のルートが認証関連（ログインまたは新規登録）かどうかを判定します。
const isAuthRoute = computed(() => {
  // `route.name` を使って判定します。ルーター設定での名前が 'Login' または 'Register' の場合に true となります。
  return route.name === 'Login' || route.name === 'Register';
});
// ★★★ ここまで修正 ★★★

const layoutClasses = computed(() => ({
  'h-screen': true,
  'overflow-hidden': isAuthRoute.value,
}));

const mainContentClasses = computed(() => ({
  'flex-1': true,
  'overflow-y-auto': !isAuthRoute.value,
}));

</script>

<style scoped>
/* 背景のフェードイン・フェードアウト */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* サイドバーのスライドイン・スライドアウト */
.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.3s ease-in-out;
}
.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>