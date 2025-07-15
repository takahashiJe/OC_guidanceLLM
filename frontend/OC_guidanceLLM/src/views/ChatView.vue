    <!-- views/ChatView.vue -->
    <template>
      <div class="flex flex-col h-screen bg-gray-50">
        <!-- チャットヘッダー -->
        <ChatHeader @logout="handleLogout" />

        <!-- メッセージ表示エリア -->
        <ChatMessages :messages="chatStore.messages" />

        <!-- エラーメッセージ表示 -->
        <div v-if="chatStore.errorMessage" class="bg-red-100 border border-red-400 text-red-700 px-4 py-2 rounded-md mx-4 mb-2 text-sm text-center">
          {{ chatStore.errorMessage }}
        </div>

        <!-- メッセージ入力エリア -->
        <ChatInput @sendMessage="handleSendMessage" :is-sending="chatStore.isSending" />
      </div>
    </template>

    <script setup>
    import { onMounted, watch } from 'vue'; // Vueのライフサイクルフックとリアクティブな監視機能をインポート
    import { useChatStore } from '../stores/chat'; // チャットストアをインポート
    import { useAuthStore } from '../stores/auth'; // 認証ストアをインポート

    import ChatHeader from '../components/ChatHeader.vue'; // チャットヘッダーコンポーネントをインポート
    import ChatMessages from '../components/ChatMessages.vue'; // メッセージ表示コンポーネントをインポート
    import ChatInput from '../components/ChatInput.vue'; // メッセージ入力コンポーネントをインポート

    // Piniaストアのインスタンスを取得
    const chatStore = useChatStore();
    const authStore = useAuthStore();

    // コンポーネントがマウントされた時に実行される処理
    onMounted(() => {
      console.log('ChatView.vue mounted. Current session ID:', chatStore.sessionId);
      // 必要であれば、ここで過去のチャット履歴をロードするロジックを追加できます
    });

    /**
     * ChatInputコンポーネントからのメッセージ送信イベントを処理します。
     * @param {string} messageText - ユーザーが入力したメッセージテキスト
     */
    const handleSendMessage = async (messageText) => {
      console.log('ChatView: Handling send message:', messageText);
      await chatStore.sendMessage(messageText, chatStore.sessionId, authStore.accessToken);
    };

    /**
     * ChatHeaderコンポーネントからのログアウトイベントを処理します。
     */
    const handleLogout = () => {
      console.log('ChatView: Handling logout request.');
      authStore.logout(); // 認証ストアのログアウトアクションを呼び出す
      // ログアウト後のリダイレクトはApp.vueのウォッチャーが処理します
    };

    // オプション: ログアウト時にチャット履歴をクリアしたい場合
    watch(() => authStore.isLoggedIn, (newVal) => {
      if (!newVal) {
        chatStore.clearSession(); // ログアウトしたらチャットセッションもクリア
      }
    });
    </script>

    <style scoped>
    /* Scoped styles for ChatView.vue if needed */
    </style>
    