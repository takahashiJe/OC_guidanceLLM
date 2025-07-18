<template>
  <div class="flex flex-col h-screen bg-white overflow-hidden">
    
    <main class="flex-1 flex flex-col justify-center items-center p-6 sm:p-8">
      <div class="w-full max-w-md text-center">
        <h1 class="text-4xl sm:text-5xl font-bold text-gray-900">
          {{ displayedTitle }}
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

const fullTitle = '発明しましょう';
const displayedTitle = ref('');

onMounted(() => {
  let index = 0;
  const interval = setInterval(() => {
    if (index < fullTitle.length) {
      displayedTitle.value += fullTitle[index];
      index++;
    } else {
      clearInterval(interval);
    }
  }, 150);
});

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
  width: 1.25rem;
  height: 2.5rem;
  background-color: #1f2937;
  margin-left: 0.5rem;
  border-radius: 9999px;
  animation: blink 1.2s infinite;
  vertical-align: middle;
}

@keyframes blink {
  0%, 100% { opacity: 1; }
  50% { opacity: 0; }
}
</style>