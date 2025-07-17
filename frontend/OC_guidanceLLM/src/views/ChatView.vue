<template>
  <div class="w-full h-full flex flex-col bg-white">

    <div class="flex-1 overflow-y-auto">
      <ChatMessages :messages="chatStore.messages" />
    </div>

    <div v-if="chatStore.errorMessage" class="shrink-0 bg-red-100 border-t border-red-200 text-red-700 px-4 py-2 text-sm">
      {{ chatStore.errorMessage }}
    </div>

    <div class="shrink-0">
      <ChatInput @sendMessage="handleSendMessage" :is-sending="chatStore.isLoading" />
    </div>
  </div>
</template>

<script setup>
import { useChatStore } from '../stores/chat';
import ChatMessages from '../components/ChatMessages.vue';
import ChatInput from '../components/ChatInput.vue';

const chatStore = useChatStore();

const handleSendMessage = async (messageText) => {
  await chatStore.sendMessage(messageText);
};
</script>