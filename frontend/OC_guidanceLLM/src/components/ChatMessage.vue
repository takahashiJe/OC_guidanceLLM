<!-- components/ChatMessage.vue -->
<template>
  <!-- メッセージの配置を送信者に応じて変更 (右寄せ/左寄せ) -->
  <div :class="['flex items-start gap-3', messageContainerClass]">
    <!-- AIのアバター (左側) -->
    <div v-if="sender === 'ai'" class="flex-shrink-0">
      <img src="https://placehold.co/40x40/007bff/ffffff?text=AI" alt="AI Avatar" class="w-10 h-10 rounded-full shadow-md">
    </div>

    <!-- メッセージバブル -->
    <div :class="['p-3 rounded-xl shadow-md max-w-[80%] text-sm sm:text-base relative', bubbleClass]">
      <!-- 送信者の名前を表示 (AIのみ) -->
      <div v-if="sender === 'ai'" class="font-bold text-blue-800 mb-1">AIアシスタント</div>
      <!-- ユーザーの名前は省略 (LINE風) -->
      
      <!-- メッセージ内容を表示 (pre-wrapで改行を保持し、break-wordsで長い単語も改行) -->
      <p class="whitespace-pre-wrap break-words">{{ content }}</p>
      
      <!-- AIの応答が保留中の場合にローディング表示 -->
      <div v-if="isPending" class="mt-1 text-xs text-gray-500 flex items-center">
        <svg class="animate-spin h-4 w-4 mr-1 text-blue-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        思考中...
      </div>

      <!-- 吹き出しの「しっぽ」 (Tailwind CSSでは複雑なのでカスタムCSSで対応) -->
      <div :class="['bubble-tail', sender === 'user' ? 'user-tail' : 'ai-tail']"></div>
    </div>

    <!-- ユーザーのアバター (右側) -->
    <div v-if="sender === 'user'" class="flex-shrink-0">
      <img src="https://placehold.co/40x40/00b894/ffffff?text=You" alt="User Avatar" class="w-10 h-10 rounded-full shadow-md">
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
