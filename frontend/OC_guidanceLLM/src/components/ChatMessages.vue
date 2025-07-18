<template>
  <div class="p-4 space-y-4">
    <ChatMessage
      v-for="message in messages"
      :key="message.id"
      v-bind="message"
    />
    
    <div ref="messagesEndRef" />
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';
import ChatMessage from './ChatMessage.vue';

const props = defineProps({
  messages: {
    type: Array,
    required: true,
  },
});

const messagesEndRef = ref(null);

watch(
  () => props.messages.length,
  () => {
    nextTick(() => {
      messagesEndRef.value?.scrollIntoView({ behavior: 'smooth' });
    });
  }
);
</script>