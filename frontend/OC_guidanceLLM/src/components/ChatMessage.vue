<!-- components/ChatMessage.vue -->
<template>
  <div class="py-4 px-4 md:px-8">
    <div class="flex items-start gap-4 max-w-4xl mx-auto">
      <div 
        class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold"
        :class="message.sender === 'user' ? 'bg-blue-500' : 'bg-gradient-to-br from-purple-500 to-indigo-600'"
      >
        {{ message.sender === 'user' ? 'U' : 'G' }}
      </div>
      
      <div class="flex-1 pt-1">
        <p class="text-base text-gray-800 leading-relaxed whitespace-pre-wrap">
          {{ message.content }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, watch } from 'vue';

const props = defineProps({
  sender: {
    type: String,
    required: true,
    validator: (value) => ['user', 'ai'].includes(value),
  },
  content: {
    type: String,
    required: true,
  },
  isPending: {
    type: Boolean,
    default: false,
  },
  id: {
    type: String,
    default: 'N/A',
  },
});

// デバッグログ
watch(() => props.content, (newContent) => {
  console.log(`ChatMessage: Received content for ${props.sender} message (ID: ${props.id || 'N/A'}):`, newContent);
}, { immediate: true });

// 送信者に基づいてメッセージコンテナのフレックス配置クラスを算出
const messageContainerClass = computed(() => {
  return props.sender === 'user' ? 'justify-end ml-auto' : 'justify-start mr-auto';
});

// 送信者に基づいて吹き出しの背景色と角丸クラスを算出
const bubbleClass = computed(() => {
  return props.sender === 'user'
    ? 'bg-[#E0FFD9] text-gray-800 rounded-br-none' // LINEの緑色に近い
    : 'bg-white text-gray-800 rounded-bl-none'; // LINEの白色に近い
});
</script>

<style scoped>
/* 吹き出しの「しっぽ」のためのカスタムCSS */
.bubble-tail {
  position: absolute;
  width: 0;
  height: 0;
  border-style: solid;
}

/* ユーザー側のしっぽ (右下) */
.user-tail {
  border-width: 0 0 10px 10px; /* 上右下左 */
  border-color: transparent transparent transparent #E0FFD9;
  bottom: 0;
  right: -9px; /* 吹き出しの角に合わせる */
}

/* AI側のしっぽ (左下) */
.ai-tail {
  border-width: 0 10px 10px 0; /* 上右下左 */
  border-color: transparent #FFFFFF transparent transparent;
  bottom: 0;
  left: -9px; /* 吹き出しの角に合わせる */
}

/* AIが思考中のスピナーの色をLINEの緑に合わせる */
.ai-tail + .mt-1 svg {
  color: #00B894; /* LINEの緑 */
}
</style>
