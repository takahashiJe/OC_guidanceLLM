<template>
  <div class="py-4 px-4 md:px-8">
    <div
      v-if="sender === 'user'"
      class="flex justify-end"
    >
      <div class="max-w-xl">
        <div class="px-4 py-3 rounded-2xl bg-blue-100 text-blue-900 rounded-br-none shadow-sm">
          <p class="text-base leading-relaxed whitespace-pre-wrap">
            {{ content }}
          </p>
        </div>
      </div>
    </div>

    <div v-else class="max-w-4xl mx-auto">
      
      <div v-if="isPending || isAnimating" class="flex items-center gap-4">
        <div class="relative w-8 h-8">
          <svg class="absolute top-0 left-0 w-full h-full animate-gemini-spinner-container" viewBox="0 0 24 24"><defs><linearGradient :id="gradientId" x1="0%" y1="0%" x2="100%" y2="100%"><stop offset="0%" stop-color="#FF8A65" /><stop offset="50%" stop-color="#FFEB3B" /><stop offset="100%" stop-color="#69F0AE" /></linearGradient></defs><circle cx="12" cy="12" r="11" fill="none" stroke-width="2" class="stroke-gray-200" opacity="0.3"></circle><circle cx="12" cy="12" r="11" fill="none" :stroke="`url(#${gradientId})`" stroke-width="2" class="animate-gemini-spinner-arc" stroke-linecap="round" stroke-dasharray="69.115"></circle></svg>
          <div class="absolute inset-0 flex items-center justify-center"><img src="/app-icon.png" alt="App Icon" class="w-5 h-5 rounded-full animate-icon-rotate" style="transform-origin: 50% 50%;"></div>
        </div>
        <p class="text-base text-gray-600">お待ちください...</p>
      </div>

      <div v-if="!isPending">
        <div class="w-8 h-8 flex items-center justify-start shrink-0">
          <img v-if="!isAnimating" src="/app-icon.png" alt="App Icon" class="w-6 h-6 rounded-full">
        </div>
        <div class="pt-2">
          <p v-if="shouldAnimate" class="text-base text-gray-800 leading-relaxed whitespace-pre-wrap">
            <span v-for="(char, index) in content.split('')" :key="index" class="fade-in-up" :style="{ animationDelay: `${index * 0.02}s` }">
              {{ char }}
            </span>
          </p>
          <p v-else class="text-base text-gray-800 leading-relaxed whitespace-pre-wrap">
            {{ content }}
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, watch } from 'vue';

const gradientId = `spinner-gradient-${Math.random().toString(36).substring(2, 9)}`;

const props = defineProps({
  sender: { type: String, required: true },
  content: { type: String, required: true },
  isPending: { type: Boolean, default: false },
});

const shouldAnimate = ref(false);
const isAnimating = ref(false);

if (props.sender === 'ai') {
  watch(() => props.isPending, (newValue, oldValue) => {
    if (oldValue === true && newValue === false && props.content) {
      shouldAnimate.value = true;
      isAnimating.value = true;
      const animationDuration = props.content.length * 20 + 500;
      setTimeout(() => {
        isAnimating.value = false;
      }, animationDuration);
    }
  }, { immediate: true });
}
</script>

<style scoped>
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}
.fade-in-up {
  display: inline-block;
  opacity: 0;
  animation: fadeInUp 0.5s forwards;
}
</style>