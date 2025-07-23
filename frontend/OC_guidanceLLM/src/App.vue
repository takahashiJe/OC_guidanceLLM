<template>
  <div class="h-screen w-screen bg-white" :class="{ 'overflow-hidden': isAuthRoute }">
    <div class="hidden lg:block fixed top-0 left-0 h-full w-[260px] z-20">
      <Sidebar v-if="!isAuthRoute" />
    </div>
    <div class="h-full flex flex-col" :class="{ 'lg:pl-[260px]': !isAuthRoute }">
      <header v-if="!isAuthRoute" class="p-2 border-b flex items-center justify-between shrink-0 bg-white z-10 lg:hidden">
        <button @click="isSidebarOpen = true" class="p-2 rounded-full hover:bg-gray-100">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" /></svg>
        </button>
        <h1 class="text-lg font-semibold text-gray-700">APU-NaviAI</h1>
        <button @click="isAboutModalOpen = true" class="p-1 rounded-full hover:bg-gray-100 transition-colors" title="このアプリについて">
          <img src="/app-icon.png" alt="App Icon" class="w-8 h-8 rounded-full">
        </button>
      </header>
      <main class="flex-1" :class="{ 'overflow-y-auto': !isAuthRoute }">
        <RouterView />
      </main>
    </div>

    <transition name="fade"><div v-if="isSidebarOpen" @click="isSidebarOpen = false" class="fixed inset-0 bg-black bg-opacity-50 z-40 lg:hidden"></div></transition>
    <transition name="slide-left"><div v-if="isSidebarOpen" class="fixed top-0 left-0 w-3/4 max-w-sm h-full bg-white shadow-xl z-50 lg:hidden"><Sidebar @close="isSidebarOpen = false" /></div></transition>

    <transition name="modal-fade">
      <div v-if="isAboutModalOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
        <div @click="isAboutModalOpen = false" class="absolute inset-0 bg-black/40 backdrop-blur-sm"></div>
        <div class="relative bg-white rounded-2xl shadow-xl p-6 sm:p-8 w-full max-w-md text-center">
          <h3 class="text-xl font-bold text-gray-800 mb-2">APU-NaviAIについて</h3>
          <p class="text-gray-600 mb-6 leading-relaxed">このAPU-NaviAIは，経営システム工学科<br>サイバーフィジカルシステム研究室（山口研）によって制作されました．</p>
          <a href="https://www.cps.akita-pu.ac.jp/" target="_blank" rel="noopener noreferrer" class="inline-block w-full mb-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition-colors duration-200">研究室のサイトを見る</a>
          <button @click="isAboutModalOpen = false" class="w-full bg-gray-200 hover:bg-gray-300 text-gray-800 font-semibold py-2.5 px-6 rounded-lg transition-colors duration-200">閉じる</button>
        </div>
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
const isAboutModalOpen = ref(false);

const isAuthRoute = computed(() => {
  return route.name === 'Login' || route.name === 'Register';
});
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
.slide-left-enter-active, .slide-left-leave-active { transition: transform 0.3s ease-in-out; }
.slide-left-enter-from, .slide-left-leave-to { transform: translateX(-100%); }
.modal-fade-enter-active, .modal-fade-leave-active { transition: opacity 0.3s ease; }
.modal-fade-enter-active .relative, .modal-fade-leave-active .relative { transition: transform 0.3s ease, opacity 0.3s ease; }
.modal-fade-enter-from, .modal-fade-leave-to { opacity: 0; }
.modal-fade-enter-from .relative, .modal-fade-leave-to .relative { transform: scale(0.95); opacity: 0; }
</style>