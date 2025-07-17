// stores/chat.js
import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';
import apiClient from '../services/api';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: null,
    isLoading: false, // 送信中と履歴読み込み中を兼ねる
    errorMessage: null,
  }),

  actions: {
    // addMessage, initSession, loadHistory, startNewSession アクションは変更なし
    addMessage(message) {
      this.messages.push(message);
    },
    // ...

    /**
     * メッセージ送信アクションの修正
     */
    async sendMessage(messageText) {
      if (this.isLoading || !messageText.trim()) return;

      if (!this.sessionId) {
        this.startNewSession();
      }

      this.isLoading = true; // ★ ここで true になる
      this.errorMessage = null;

      const userMessage = { sender: 'user', content: messageText, id: uuidv4() };
      this.addMessage(userMessage);

      const aiPlaceholder = { sender: 'ai', content: 'AIが思考中...', id: uuidv4(), isPending: true };
      this.addMessage(aiPlaceholder);
      
      try {
        const initialResponse = await apiClient.post('/chat', {
          message: messageText,
          session_id: this.sessionId,
        });
        
        const { task_id } = initialResponse.data;

        // ポーリング処理
        const poll = async () => {
          try {
            const statusResponse = await apiClient.get(`/chat/results/${task_id}`);
            const { status, ai_message, detail } = statusResponse.data;

            if (status === 'SUCCESS') {
              this.updatePendingMessage(aiPlaceholder.id, ai_message);
              this.isLoading = false; // ★ 成功時に false に戻す
            } else if (status === 'FAILURE') {
              const errorDetail = detail || '不明なエラーが発生しました。';
              this.updatePendingMessage(aiPlaceholder.id, `エラー: ${errorDetail}`);
              this.errorMessage = errorDetail;
              this.isLoading = false; // ★ 失敗時にも false に戻す
            } else {
              // PENDINGの場合は1秒後に再試行
              setTimeout(poll, 1000);
            }
          } catch(pollError) {
             console.error("ポーリング中にエラーが発生しました:", pollError);
             this.errorMessage = "AIからの応答取得に失敗しました。";
             this.isLoading = false; // ★ ポーリング自体のエラーでも false に戻す
          }
        };
        // 最初のポーリングを開始
        setTimeout(poll, 1000);

      } catch (error) {
        // 最初のPOSTリクエストが失敗した場合のエラーハンドリング
        const errorDetail = error.response?.data?.detail || error.message || 'メッセージの送信に失敗しました。';
        this.updatePendingMessage(aiPlaceholder.id, `エラー: ${errorDetail}`);
        this.errorMessage = errorDetail;
        this.isLoading = false; // ★ ここでも false に戻す
      }
    },
    
    updatePendingMessage(id, newContent) {
        const message = this.messages.find(m => m.id === id);
        if (message) {
            message.content = newContent;
            message.isPending = false;
        }
    },
  },
});