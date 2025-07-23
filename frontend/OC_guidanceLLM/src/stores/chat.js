import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';
import apiClient from '../services/api';

export const useChatStore = defineStore('chat', {
  state: () => ({
    messages: [],
    // 要件: stateの初期化時にlocalStorageからsessionIdを読み込む
    sessionId: localStorage.getItem('sessionId'),
    isLoading: false,
    errorMessage: null,
  }),

  actions: {
    /**
     * 要件: アプリケーション起動時にセッションを初期化するアクション
     */
    async initSession() {
      // sessionIdが存在する場合のみ履歴の読み込みを試みる
      if (this.sessionId) {
        await this.loadHistory();
      }
    },

    /**
     * 要件: バックエンドから指定されたセッションIDの会話履歴を読み込むアクション
     */
    async loadHistory() {
      if (!this.sessionId) return;
      this.isLoading = true;
      this.errorMessage = null;
      try {
        const response = await apiClient.get(`/chat/history/${this.sessionId}`);
        const loadedMessages = [];
        // 取得した履歴をmessages配列に整形して格納
        response.data.forEach(turn => {
          loadedMessages.push({ id: uuidv4(), sender: 'user', content: turn.human_message });
          loadedMessages.push({ id: uuidv4(), sender: 'ai', content: turn.ai_message });
        });
        this.messages = loadedMessages;
      } catch (error) {
        console.error('[loadHistory] 履歴の読み込みに失敗しました:', error);
        // 履歴の取得に失敗した場合（例: サーバーからセッションが見つからない）、セッション情報をクリア
        localStorage.removeItem('sessionId');
        this.sessionId = null;
        this.messages = [];
        this.errorMessage = '過去の会話の読み込みに失敗しました。新しい会話を開始してください。';
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 要件: 新しい会話を開始するアクション
     */
    startNewSession() {
      // 新しいユニークなIDを生成
      const newSessionId = uuidv4();
      this.messages = [];
      this.sessionId = newSessionId;
      this.isLoading = false;
      this.errorMessage = null;
      // 新しいIDをlocalStorageに保存
      localStorage.setItem('sessionId', newSessionId);
    },

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
        const initialResponse = await apiClient.post('/chat', {
          message: messageText,
          session_id: this.sessionId,
        });
        const { task_id } = initialResponse.data;

        this.pollForResult(task_id, aiPlaceholder.id);

      } catch (error) {
        console.error('Error sending message:', error);
        this.addMessage({
          sender: 'system',
          content: 'メッセージの送信中にエラーが発生しました。',
        });
        // ★ エラーを再スローしてインターセプターに処理を渡す
        throw error; 
      } finally {
        this.isSending = false;
        this.currentTaskId = null;
      }
    },

    pollForResult(taskId, placeholderId) {
      const interval = setInterval(async () => {
        try {
          const statusResponse = await apiClient.get(`/chat/results/${taskId}`);
          const { status, ai_message } = statusResponse.data;

          if (status === 'SUCCESS' || status === 'FAILURE') {
            clearInterval(interval);
            this.isLoading = false;
            
            const finalMessage = status === 'SUCCESS' ? ai_message : 'エラー: 応答の生成に失敗しました。';
            
            const message = this.messages.find(m => m.id === placeholderId);
            if (message) {
              message.content = finalMessage;
              message.isPending = false;
            }
          }
        } catch (error) {
          clearInterval(interval);
          this.handleSendError(error, placeholderId);
        }
      }, 2000);
    },

    handleSendError(error, placeholderId) {
      const errorDetail = error.response?.data?.detail || error.message || 'メッセージの送信中にエラーが発生しました。';
      
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