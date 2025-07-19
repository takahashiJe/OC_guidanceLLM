<template>
  <div class="h-screen w-screen bg-white" :class="{ 'overflow-hidden': isAuthRoute }">
    <div class="hidden lg:block fixed top-0 left-0 h-full w-[260px] z-20">
      <Sidebar v-if="!isAuthRoute" />
    </div>

    <div class="h-full flex flex-col" :class="{ 'lg:pl-[260px]': !isAuthRoute }">
      
      <header v-if="!isAuthRoute" class="p-2 border-b flex items-center justify-between shrink-0 bg-white z-10 lg:hidden">
        <button @click="isSidebarOpen = true" class="p-2 rounded-full hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
          </svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-700">APU-NaviAI</h1>
        <img src="@/assets/app-icon.png" alt="App Icon" class="w-8 h-8 rounded-full">
      </header>

      <main class="flex-1 overflow-y-auto">
        <RouterView />
      </main>
    </div>

    <transition name="fade">
      <div 
        v-if="isSidebarOpen" 
        @click="isSidebarOpen = false" 
        class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"
      ></div>
    </transition>
    <transition name="slide-left">
      <div v-if="isSidebarOpen" class="fixed top-0 left-0 w-3/4 max-w-sm h-full bg-white shadow-xl z-50 lg:hidden">
        <Sidebar @close="isSidebarOpen = false" />
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import { RouterView, useRoute } from 'vue-router';
import Sidebar from './components/Sidebar.vue';

const isSidebarOpen = ref(false);
const route = useRoute();

const isAuthRoute = computed(() => {
  return route.name === 'Login' || route.name === 'Register';
});
</script>

<style scoped>
/* スタイルに変更はありません */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-left-enter-active,
.slide-left-leave-active {
  transition: transform 0.3s ease-in-out;
}
.slide-left-enter-from,
.slide-left-leave-to {
  transform: translateX(-100%);
}
</style>