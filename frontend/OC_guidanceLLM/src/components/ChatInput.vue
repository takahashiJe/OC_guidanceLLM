<template>
  <div class="p-4 bg-white">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center bg-[#f0f4f9] rounded-full p-2">
        <textarea
          ref="textarea"
          v-model="newMessage"
          @keydown.enter.prevent="handleEnter"
          placeholder="メッセージを入力..."
          class="flex-1 bg-transparent border-none focus:ring-0 resize-none p-2 text-base text-gray-800 placeholder-gray-500"
          rows="1"
        ></textarea>
        <button
          @click="handleSendMessage"
          :disabled="isSending || newMessage.trim() === ''"
          class="w-10 h-10 rounded-full flex items-center justify-center transition-colors"
          :class="isSending || newMessage.trim() === '' ? 'bg-gray-300' : 'bg-blue-500 hover:bg-blue-600'"
        >
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-white" viewBox="0 0 20 20" fill="currentColor">
            <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.428A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
          </svg>
        </button>
      </div>
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
