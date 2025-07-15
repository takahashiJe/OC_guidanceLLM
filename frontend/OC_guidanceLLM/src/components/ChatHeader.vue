<!-- components/ChatHeader.vue -->
<template>
  <header class="bg-gradient-to-r from-blue-600 to-indigo-700 text-white p-4 shadow-md flex items-center justify-between sticky top-0 z-10 rounded-b-xl">
    <h1 class="text-xl sm:text-2xl font-bold">秋田県立大学AIアシスタント</h1>
    <button
      @click="emit('logout')"
      class="bg-red-500 hover:bg-red-600 text-white font-semibold py-1 px-3 rounded-lg text-sm transition duration-200 shadow-md"
    >
      ログアウト
    </button>
  </header>
</template>

<script setup>
// 親コンポーネントに'logout'イベントを通知するためのemit関数を定義
const emit = defineEmits(['logout']); 
</script>

<style scoped>
/* Tailwind CSS handles most styling */
</style>
