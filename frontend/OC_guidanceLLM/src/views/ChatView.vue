<template>
  <div class="w-full h-full flex flex-col bg-white">

    <div class="flex-1 overflow-y-auto">
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
import { onMounted } from 'vue'; // ★ onMounted をインポート
import { useChatStore } from '../stores/chat';
import ChatMessages from '../components/ChatMessages.vue';
import ChatInput from '../components/ChatInput.vue';

const chatStore = useChatStore();

const handleSendMessage = async (messageText) => {
  await chatStore.sendMessage(messageText);
};

// ★ このコンポーネントがマウントされた時にセッションを初期化する
onMounted(() => {
  // メッセージが空の場合のみ履歴の読み込みを試みる
  // これにより、他の画面から戻ってきた際に不要な再読み込みを防ぐ
  if (chatStore.messages.length === 0) {
    chatStore.initSession();
  }
});
</script>