<!-- components/LoadingIndicator.vue -->
<template>
  <!-- v-ifで表示/非表示を制御。fixed inset-0 で画面全体を覆う -->
  <div v-if="isVisible" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
    <div class="flex flex-col items-center p-6 bg-white rounded-lg shadow-xl">
      <!-- スピナーSVGアイコン -->
      <svg class="animate-spin h-10 w-10 text-blue-600 mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
        <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
        <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
      </svg>
      <!-- 表示メッセージ -->
      <p class="text-gray-800 text-lg font-semibold">{{ message }}</p>
    </div>
  </div>
</template>

<script setup>
// 親コンポーネントからプロップスを受け取る
const props = defineProps({
  isVisible: {
    type: Boolean,
    default: false, // ローディングインジケーターの表示/非表示を制御
  },
  message: {
    type: String,
    default: '処理中...', // 表示するメッセージ
  },
});
</script>

<style scoped>
/* Tailwind CSS handles most styling */
</style>
