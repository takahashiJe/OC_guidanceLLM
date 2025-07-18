<template>
  <div class="p-4 bg-white">
    <div class="max-w-4xl mx-auto">
      <div class="flex items-center bg-[#f0f4f9] rounded-full p-2">
        <textarea
          ref="textarea"
          v-model="newMessage"
          @input="adjustTextareaHeight"
          @keydown.enter.prevent="handleEnter"
          placeholder="メッセージを入力..."
          class="flex-1 bg-transparent border-none focus:ring-0 resize-none p-2 text-base text-gray-800 placeholder-gray-500"
          rows="1"
        ></textarea>
        <button
          @click="handleSendMessage"
          :disabled="props.isSending || newMessage.trim() === ''"
          class="w-10 h-10 rounded-full flex items-center justify-center transition-colors"
          :class="props.isSending || newMessage.trim() === '' ? 'bg-gray-300' : 'bg-blue-500 hover:bg-blue-600'"
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

// ★★★ newMessage変数をここで定義 ★★★
const newMessage = ref('');
const textarea = ref(null);

// テキストエリアの高さ自動調整
const adjustTextareaHeight = () => {
  const el = textarea.value;
  if (el) {
    el.style.height = 'auto';
    el.style.height = `${el.scrollHeight}px`;
  }
};

// Enterキーが押された時の処理
const handleEnter = (event) => {
  if (event.shiftKey) return; // Shift+Enterなら改行
  handleSendMessage();
};

// メッセージ送信処理
const handleSendMessage = () => {
  if (props.isSending || newMessage.value.trim() === '') return;
  
  emit('sendMessage', newMessage.value.trim());
  newMessage.value = ''; // 入力フィールドをクリア
  
  nextTick(() => {
    adjustTextareaHeight(); // クリア後に高さをリセット
  });
};

// newMessageの変更を監視して高さを調整
watch(newMessage, adjustTextareaHeight);
</script>