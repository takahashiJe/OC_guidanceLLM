<template>
  <div class="h-screen w-screen hidden lg:grid lg:grid-cols-[auto_1fr]">
    <Sidebar />
    <main class="overflow-y-auto">
      <RouterView />
    </main>
  </div>

  <div class="h-screen w-screen flex flex-col lg:hidden">
    <header class="p-2 border-b flex items-center justify-between shrink-0 bg-white z-10">
      <button @click="isSidebarOpen = true" class="p-2 rounded-full hover:bg-gray-100">
        <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6 text-gray-600" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
          <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>
      <h1 class="text-lg font-semibold text-gray-700">APU-Compass</h1>
      <img src="@/assets/app-icon.png" alt="App Icon" class="w-8 h-8 rounded-full">
    </header>

    <main class="flex-1 overflow-y-auto">
      <RouterView />
    </main>
    
    <div v-if="isSidebarOpen" class="fixed inset-0 z-40">
      <div @click="isSidebarOpen = false" class="absolute inset-0 bg-black opacity-50"></div>
      <div class="relative w-3/4 max-w-sm h-full bg-[#f0f4f9] shadow-xl">
        <Sidebar @close="isSidebarOpen = false" />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Sidebar from './components/Sidebar.vue';
import { RouterView } from 'vue-router';

const isSidebarOpen = ref(false);
</script>