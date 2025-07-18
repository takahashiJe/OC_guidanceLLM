import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';
import apiClient from '../services/api';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    sessionId: localStorage.getItem('sessionId'),
    isLoading: false,
    errorMessage: null,
  }),

  actions: {
    async initSession() {
      if (this.sessionId) {
        await this.loadHistory();
      }
    },

    async loadHistory() {
      if (!this.sessionId) return;
      this.isLoading = true;
      try {
        const response = await apiClient.get(`/chat/history/${this.sessionId}`);
        const loadedMessages = [];
        response.data.forEach(turn => {
          loadedMessages.push({ id: uuidv4(), sender: 'user', content: turn.human_message });
          loadedMessages.push({ id: uuidv4(), sender: 'ai', content: turn.ai_message });
        });
        this.messages = loadedMessages;
      } catch (error) {
        console.error('[loadHistory] 履歴の読み込みに失敗しました:', error);
        localStorage.removeItem('sessionId');
        this.sessionId = null;
        this.messages = [];
        this.errorMessage = '過去の会話の読み込みに失敗しました。';
      } finally {
        this.isLoading = false;
      }
    },

    startNewSession() {
      const newSessionId = uuidv4();
      this.messages = [];
      this.sessionId = newSessionId;
      this.isLoading = false;
      this.errorMessage = null;
      localStorage.setItem('sessionId', newSessionId);
    },

    /**
     * ★★★ ここからが修正のポイント ★★★
     */
    async sendMessage(messageText) {
      if (this.isLoading || !messageText.trim()) return;

      if (!this.sessionId) {
        this.startNewSession();
      }
      
      this.isLoading = true;
      this.errorMessage = null;
      
      const userMessage = { id: uuidv4(), sender: 'user', content: messageText };
      this.messages.push(userMessage);

      const aiPlaceholder = { id: uuidv4(), sender: 'ai', content: '', isPending: true };
      this.messages.push(aiPlaceholder);
      
      try {
        // 1. 最初のPOSTリクエストを送信
        const initialResponse = await apiClient.post('/chat', {
          message: messageText,
          session_id: this.sessionId,
        });
        const { task_id } = initialResponse.data;

        // 2. 受け取ったtask_idを使ってポーリングを開始
        this.pollForResult(task_id, aiPlaceholder.id);

      } catch (error) {
        // 3. 最初のPOSTリクエストが失敗した場合のエラー処理
        this.handleSendError(error, aiPlaceholder.id);
      }
    },

    /**
     * AIの応答をポーリングするアクション
     */
    pollForResult(taskId, placeholderId) {
      const interval = setInterval(async () => {
        try {
          const statusResponse = await apiClient.get(`/chat/results/${taskId}`);
          const { status, ai_message } = statusResponse.data;

          if (status === 'SUCCESS' || status === 'FAILURE') {
            clearInterval(interval); // ポーリングを停止
            this.isLoading = false;   // ローディング状態を解除
            
            const finalMessage = status === 'SUCCESS' ? ai_message : 'エラー: 応答の生成に失敗しました。';
            
            // プレースホルダーのメッセージを最終的な応答に更新
            const message = this.messages.find(m => m.id === placeholderId);
            if (message) {
              message.content = finalMessage;
              message.isPending = false;
            }
          }
          // statusが'PENDING'の場合は何もしない（次のインターバルで再試行）

        } catch (error) {
          clearInterval(interval); // エラー発生時もポーリングを停止
          this.handleSendError(error, placeholderId);
        }
      }, 2000); // 2秒間隔でポーリング
    },

    /**
     * 送信エラーを処理するための共通アクション
     */
    handleSendError(error, placeholderId) {
      const errorDetail = error.response?.data?.detail || error.message || 'メッセージの送信中にエラーが発生しました。';
      
      // プレースホルダーをエラーメッセージに更新
      const message = this.messages.find(m => m.id === placeholderId);
      if (message) {
        message.content = `エラー: ${errorDetail}`;
        message.isPending = false;
      }
      
      this.errorMessage = errorDetail;
      this.isLoading = false;
    }
  },
});