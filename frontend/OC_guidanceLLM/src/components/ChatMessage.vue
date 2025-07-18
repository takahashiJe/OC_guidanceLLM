<template>
  <div class="py-4 px-4 md:px-8">
    <div class="flex items-start gap-4 max-w-4xl mx-auto">
      <div 
        class="w-8 h-8 rounded-full flex items-center justify-center text-white font-bold shrink-0"
        :class="sender === 'user' ? 'bg-blue-500' : 'bg-gradient-to-br from-purple-500 to-indigo-600'"
      >
        {{ sender === 'user' ? 'U' : 'G' }}
      </div>
      
      <div class="flex-1 pt-1">
        <div v-if="isPending" class="flex items-center space-x-2">
           <svg class="animate-spin h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
           </svg>
           <span class="text-gray-500">AIが思考中...</span>
        </div>
        <p v-else class="text-base text-gray-800 leading-relaxed whitespace-pre-wrap">
          {{ content }}
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
defineProps({
  sender: {
    type: String,
    required: true,
  },
  content: {
    type: String,
    required: true,
  },
  isPending: {
    type: Boolean,
    default: false,
  },
});
</script>