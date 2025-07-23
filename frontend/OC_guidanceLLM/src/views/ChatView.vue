<template>
  <div class="w-full h-full flex flex-col bg-noise">
    <div class="flex-1 overflow-y-auto" ref="messagesContainer">
      <ChatMessages :messages="chatStore.messages" />
    </div>
    <div class="shrink-0">
      <div v-if="chatStore.errorMessage" class="bg-red-100 border-t border-red-200 text-red-700 px-4 py-2 text-sm">
        {{ chatStore.errorMessage }}
      </div>
      <ChatInput @sendMessage="handleSendMessage" :is-sending="chatStore.isLoading" />
    </div>
  </div>
</template>

<script setup>
import { onMounted, ref, watch, nextTick } from 'vue';
import { useChatStore } from '../stores/chat';
import ChatMessages from '../components/ChatMessages.vue';
import ChatInput from '../components/ChatInput.vue';

const chatStore = useChatStore();
const messagesContainer = ref(null);

const handleSendMessage = async (messageText) => {
  await chatStore.sendMessage(messageText);
};

// Function to scroll to the bottom of the messages container
const scrollToBottom = () => {
  nextTick(() => {
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
    }
  });
};

// Watch for changes in the number of messages and scroll to bottom
watch(() => chatStore.messages.length, () => {
  scrollToBottom();
});

// When the component is first mounted
onMounted(() => {
  if (chatStore.messages.length === 0) {
    chatStore.initSession();
  }
  scrollToBottom(); // Also scroll to bottom on initial load
});
</script>