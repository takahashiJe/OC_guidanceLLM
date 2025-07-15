<!-- components/ChatMessages.vue -->
<template>
  <!-- overflow-y-auto でスクロール可能にし、flex-1 で残りの高さを占める -->
  <div class="flex-1 overflow-y-auto p-4 space-y-4 pt-20 pb-20">
    <!-- 各メッセージをChatMessageコンポーネントでレンダリング -->
    <ChatMessage
      v-for="message in messages"
      :key="message.id"
      :sender="message.sender"
      :content="message.content"
      :is-pending="message.isPending"
      :id="message.id"
    />
    <!-- メッセージリストの最下部へのスクロールアンカー -->
    <div ref="messagesEnd" class="h-0" />
  </div>
</template>

<script setup>
import { nextTick, watch, ref } from 'vue'; // Vueのリアクティブ機能とDOM更新後の処理をインポート
import ChatMessage from './ChatMessage.vue'; // 単一メッセージコンポーネントをインポート

// 親コンポーネントから'messages'プロップを受け取る
const props = defineProps({
  messages: {
    type: Array,
    required: true,
  },
});

// メッセージリストの最下部要素への参照
const messagesEnd = ref(null); 

// 'messages'プロップの変更を監視し、変更があったら自動スクロールを実行
watch(
  () => props.messages, 
  () => {
    // DOMが更新された後にスクロールを実行するためにnextTickを使用
    nextTick(() => {
      if (messagesEnd.value) {
        messagesEnd.value.scrollIntoView({ behavior: 'smooth' }); // スムーズスクロール
      }
    });
  }, 
  { deep: true } // 配列内のオブジェクトの変更も監視するためにdeepオプションをtrueに設定
);
</script>

<style scoped>
/* Tailwind CSS handles most styling */
</style>
