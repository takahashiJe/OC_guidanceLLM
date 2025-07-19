<template>
  <div class="flex flex-col h-full bg-noise overflow-hidden">
    
    <main class="flex-1 flex flex-col justify-center items-center p-6 sm:p-8">
      <div class="w-full max-w-md text-center">
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900 h-24">
          <span class="whitespace-pre-wrap">{{ displayedTitle }}</span>
          <span class="blinking-cursor"></span>
        </h1>
      </div>
    </main>

    <footer class="w-full bg-black rounded-t-3xl p-6 sm:p-8 shrink-0">
      <div class="w-full max-w-md mx-auto space-y-4">
        <div v-if="authStore.errorMessage" class="bg-red-900/50 border border-red-500/50 text-red-300 p-4 rounded-xl text-sm" role="alert">
          <p>{{ authStore.errorMessage }}</p>
        </div>
        
        <LoginForm v-if="!isRegisterMode" @submit="handleLogin" :is-loading="authStore.isLoading" />
        <RegistrationForm v-else @submit="handleRegister" :is-loading="authStore.isLoading" />

        <button
          @click="toggleMode"
          :disabled="authStore.isLoading"
          class="w-full flex justify-center py-3.5 px-4 rounded-xl text-base font-semibold transition-colors duration-300
                 bg-zinc-800 text-white
                 hover:bg-zinc-700"
        >
          {{ isRegisterMode ? 'ログインはこちら' : '新規登録' }}
        </button>
      </div>
    </footer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useAuthStore } from '../stores/auth';
import LoginForm from '../components/LoginForm.vue';
import RegistrationForm from '../components/RegistrationForm.vue';

const authStore = useAuthStore();
const isRegisterMode = ref(false);

// ★★★ ここからアニメーション用のコード ★★★

// 1. 表示させたいフレーズの配列
const phrases = [
  'APU-NaviAIが，ここからの一歩をつなげる',
  '知りたいことがあるなら，聞いてみればいい',
  'このキャンパスの今を，案内する',
  '見えていなかったものが，APU-NaviAIで見えてくる',
  '一緒に歩けば，きっと見つかる',
  'APU-NaviAIが，情報のすべてを静かに届ける',
  '歩くほどに，見えてくる',
  'キャンパスの魅力は，歩いて知るものだ．その背中を，そっと押す存在がいる',
  'すべてを詰め込まない，必要なだけを届ける',
  '一緒に回れば，ちょっと未来が近づいてくる'
];
const displayedTitle = ref('');
const phraseIndex = ref(0);
const charIndex = ref(0);
const isDeleting = ref(false);

const typeEffect = () => {
  const currentPhrase = phrases[phraseIndex.value];
  let typingSpeed = isDeleting.value ? 75 : 150; // 削除時は少し速く

  if (isDeleting.value) {
    // 文字を削除
    displayedTitle.value = currentPhrase.substring(0, charIndex.value - 1);
    charIndex.value--;
  } else {
    // 文字を追加
    displayedTitle.value = currentPhrase.substring(0, charIndex.value + 1);
    charIndex.value++;
  }

  // フレーズの最後までタイピングしたら、削除モードに切り替え
  if (!isDeleting.value && charIndex.value === currentPhrase.length) {
    typingSpeed = 2000; // フレーズ表示後の待機時間
    isDeleting.value = true;
  } 
  // フレーズを全て削除したら、次のフレーズへ
  else if (isDeleting.value && charIndex.value === 0) {
    isDeleting.value = false;
    phraseIndex.value = (phraseIndex.value + 1) % phrases.length;
    typingSpeed = 500; // 次のフレーズまでの待機時間
  }
  
  setTimeout(typeEffect, typingSpeed);
};

onMounted(() => {
  typeEffect();
});

// ★★★ ここまでアニメーション用のコード ★★★


const handleLogin = async (credentials) => {
  await authStore.login(credentials);
};
const handleRegister = async (details) => {
  await authStore.register(details);
  if (!authStore.errorMessage) {
    isRegisterMode.value = false;
  }
};
const toggleMode = () => {
  isRegisterMode.value = !isRegisterMode.value;
  authStore.errorMessage = null;
};
</script>

<style scoped>
.blinking-cursor {
  display: inline-block;
  width: 4px;
  height: 2.5rem; /* h1のフォントサイズに合わせる */
  background-color: #1f2937;
  margin-left: 8px;
  animation: blink 1s step-end infinite;
  vertical-align: bottom;
}

@keyframes blink {
  from, to {
    background-color: transparent;
  }
  50% {
    background-color: #1f2937;
  }
}
</style>