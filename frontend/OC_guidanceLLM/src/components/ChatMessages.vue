<template>
  <div class="p-4 space-y-6">
    <ChatMessage
      v-for="message in messages"
      :key="message.id"
      :sender="message.sender"
      :content="message.content"
      :is-pending="message.isPending"
    />
  </div>
</template>

<script setup>
import ChatMessage from './ChatMessage.vue';

// 親コンポーネント(ChatView.vue)から 'messages' という名前の配列を受け取ることを定義
defineProps({
  messages: {
    type: Array,
    required: true,
  },
});
</script>