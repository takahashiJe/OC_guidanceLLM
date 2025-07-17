<template>
  <aside class="bg-[#f0f4f9] w-64 p-4 flex flex-col">
    <button
      @click="startNewChat"
      class="flex items-center justify-between w-full bg-blue-100 hover:bg-blue-200 text-blue-800 font-semibold py-2 px-4 rounded-full transition-colors duration-200"
    >
      <span>新しい会話</span>
      <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
        <path d="M17.414 2.586a2 2 0 00-2.828 0L7 10.172V13h2.828l7.586-7.586a2 2 0 000-2.828z" />
        <path fill-rule="evenodd" d="M2 6a2 2 0 012-2h4a1 1 0 010 2H4v10h10v-4a1 1 0 112 0v4a2 2 0 01-2 2H4a2 2 0 01-2-2V6z" clip-rule="evenodd" />
      </svg>
    </button>

    <div class="mt-8">
      <h3 class="text-sm font-semibold text-gray-500 px-4">最近の会話</h3>
      <div class="mt-2">
        </div>
    </div>
  </aside>
</template>

<script setup>
import { useChatStore } from '../stores/chat';

const chatStore = useChatStore();

const startNewChat = () => {
  chatStore.startNewSession();
};
</script>