<template>
  <div class="p-4 bg-white border-t border-gray-200 sticky bottom-0 z-10 shadow-lg rounded-t-xl">
    <div class="flex items-center space-x-3">
      <textarea
        v-model="messageText"
        @keydown.enter.prevent="handleEnter"
        :disabled="isSending"
        rows="1"
        placeholder="メッセージを入力してください..."
        class="flex-1 resize-none overflow-hidden px-4 py-2 border border-gray-300 rounded-full focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 text-sm sm:text-base transition-all duration-200 leading-tight"
        style="max-height: 120px;"
        @input="adjustTextareaHeight"
        ref="textarea"
      ></textarea>
      <button
        @click="handleSendMessage"
        :disabled="isSending || !messageText.trim()"
        class="flex-shrink-0 bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-md transition duration-200 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24">
          <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
        </svg>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, nextTick } from 'vue';

const props = defineProps({
  isSending: {
    type: Boolean,
    default: false,
  },
});

const emit = defineEmits(['sendMessage']);

const messageText = ref('');
const textarea = ref(null); // textarea要素への参照

// Enterキーが押された時の処理 (Shift+Enterで改行)
const handleEnter = (event) => {
  if (!event.shiftKey) {
    event.preventDefault(); // デフォルトの改行動作をキャンセル
    handleSendMessage();
  }
};

// メッセージ送信処理
const handleSendMessage = () => {
  if (!messageText.value.trim() || props.isSending) {
    return;
  }
  emit('sendMessage', messageText.value.trim());
  messageText.value = ''; // 入力フィールドをクリア
  nextTick(() => {
    adjustTextareaHeight(); // クリア後に高さをリセット
  });
};

// テキストエリアの高さ自動調整
const adjustTextareaHeight = () => {
  if (textarea.value) {
    textarea.value.style.height = 'auto'; // 一度高さをリセット
    textarea.value.style.height = textarea.value.scrollHeight + 'px'; // scrollHeightに合わせて高さを設定
  }
};

// messageTextの変更を監視して高さを調整
watch(messageText, () => {
  nextTick(() => {
    adjustTextareaHeight();
  });
});

// isSendingがfalseになったら（送信完了したら）入力フィールドをリセット
watch(() => props.isSending, (newVal, oldVal) => {
  if (oldVal && !newVal) {
    // 送信が完了した時
    nextTick(() => {
      adjustTextareaHeight();
    });
  }
});
</script>

<style scoped>
/* Tailwind CSS handles most styling */
</style>
