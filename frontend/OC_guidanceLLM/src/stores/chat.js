// stores/chat.js
import { defineStore } from 'pinia';
import { v4 as uuidv4 } from 'uuid';
// postChatMessage と getTaskStatus を services/api からインポート
import { postChatMessage, getTaskStatus } from '../services/api'; 

/**
 * @typedef {Object} ChatMessage
 * @property {'user' | 'ai'} sender - メッセージの送信者 ('user' または 'ai').
 * @property {string} content - メッセージの内容.
 * @property {string} id - メッセージの一意なID.
 * @property {boolean} [isPending=false] - AIの応答がまだ保留中であるかを示す (true の場合).
 * @property {string} [taskId] - このメッセージがバックエンドタスクに関連付けられている場合のタスクID.
 */

/**
 * @typedef {Object} ChatState
 * @property {ChatMessage[]} messages - チャットメッセージの配列.
 * @property {string | null} sessionId - 現在のチャットセッションの一意なID.
 * @property {boolean} isSending - メッセージが現在送信中で、AIの応答を待っているかを示す.
 * @property {string | null} errorMessage - チャット操作からのエラーメッセージを格納する.
 */

/**
 * チャットセッションの状態を管理するPiniaストア.
 * メッセージ履歴、セッションIDの永続化、メッセージ送信を処理する.
 */
export const useChatStore = defineStore('chat', {
  /**
   * @returns {ChatState} チャットストアの初期状態.
   */
  state: () => ({
    messages: [],
    sessionId: null,
    isSending: false,
    errorMessage: null,
  }),

  actions: {
    /**
     * localStorageからチャットセッションIDを初期化するか、新しいIDを生成する.
     */
    initSession() {
      console.log('ChatStore: Initializing chat session.');
      try {
        let storedSessionId = localStorage.getItem('sessionId');
        if (!storedSessionId) {
          storedSessionId = uuidv4(); // セッションIDが見つからない場合は新しいUUIDを生成
          localStorage.setItem('sessionId', storedSessionId);
          console.log('ChatStore: New session ID generated and stored:', storedSessionId);
        }
        this.sessionId = storedSessionId;
        console.log('ChatStore: Chat session initialized with ID:', this.sessionId);
      } catch (error) {
        console.error('ChatStore: Error initializing session from localStorage:', error);
        this.sessionId = uuidv4(); // localStorageが失敗した場合のフォールバック
        console.log('ChatStore: Fallback to new session ID:', this.sessionId);
      }
    },

    /**
     * チャット履歴に新しいメッセージを追加する.
     * @param {ChatMessage} message - 追加するメッセージオブジェクト.
     */
    addMessage(message) {
      this.messages.push(message);
      console.log('ChatStore: Message added:', message.sender, message.content.substring(0, 30) + '...');
    },

    /**
     * ユーザーメッセージをバックエンドAPIに送信し、AIの応答を処理する.
     * @param {string} messageText - ユーザーメッセージのテキスト内容.
     * @param {string} sessionId - 現在のチャットセッションID.
     * @param {string} accessToken - 認証用アクセストークン.
     * @returns {Promise<void>} AIの応答が受信されたときに解決するPromise.
     */
    async sendMessage(messageText, sessionId, accessToken) {
      if (this.isSending) {
        console.warn('ChatStore: Message already sending, ignoring new request.');
        return;
      }
      if (!messageText.trim()) {
        this.errorMessage = 'Message cannot be empty.';
        return;
      }
      if (!sessionId) {
        this.errorMessage = 'Session ID is missing.';
        console.error('ChatStore: Session ID is missing for sendMessage.');
        return;
      }
      if (!accessToken) {
        this.errorMessage = 'Access token is missing. Please log in.';
        console.error('ChatStore: Access token is missing for sendMessage.');
        return;
      }

      this.isSending = true;
      this.errorMessage = null;
      console.log('ChatStore: Sending message to API...');

      // ユーザーのメッセージを履歴にすぐ追加
      const userMessageId = uuidv4();
      this.addMessage({ sender: 'user', content: messageText, id: userMessageId });

      // 保留中のAIメッセージのプレースホルダーを追加
      const aiMessageId = uuidv4();
      this.addMessage({ sender: 'ai', content: 'AIが思考中...', id: aiMessageId, isPending: true });

      let taskId = null;
      try {
        // 1. メッセージを送信し、task_id を取得
        const initialResponse = await postChatMessage({ message: messageText, session_id: sessionId }, accessToken);
        taskId = initialResponse.task_id;
        console.log('ChatStore: Message sent, received task_id:', taskId);

        // 2. task_id を使ってポーリングを開始
        const pollingInterval = 1000; // 1秒ごとにポーリング
        const maxPollingAttempts = 60; // 最大60秒待機 (調整可能)
        let attempts = 0;

        const pollTaskStatus = setInterval(async () => {
          attempts++;
          if (attempts > maxPollingAttempts) {
            clearInterval(pollTaskStatus);
            this.errorMessage = 'AI応答のタイムアウト。';
            console.error('ChatStore: Polling timed out for task:', taskId);
            this.updatePendingMessage(aiMessageId, 'エラー: AI応答がタイムアウトしました。');
            this.isSending = false;
            return;
          }

          try {
            const taskStatusResponse = await getTaskStatus(taskId, accessToken);
            console.log('ChatStore: Polling status for task', taskId, 'Status:', taskStatusResponse.status);
            
            // ★★★ ここにデバッグログを追加 ★★★
            if (taskStatusResponse.status === 'SUCCESS' || taskStatusResponse.status === 'FAILURE') {
              console.log('ChatStore: Received AI message content from API:', taskStatusResponse.ai_message);
              console.log('ChatStore: Received AI message detail (if any):', taskStatusResponse.detail);
            }

            if (taskStatusResponse.status === 'SUCCESS') {
              clearInterval(pollTaskStatus);
              this.updatePendingMessage(aiMessageId, taskStatusResponse.ai_message || 'AI応答なし。');
              console.log('ChatStore: AI response received successfully for task:', taskId);
              this.isSending = false;
            } else if (taskStatusResponse.status === 'FAILURE') {
              clearInterval(pollTaskStatus);
              this.errorMessage = `AI応答エラー: ${taskStatusResponse.detail || '不明なエラー'}`;
              console.error('ChatStore: AI response failed for task:', taskId, 'Detail:', taskStatusResponse.detail);
              this.updatePendingMessage(aiMessageId, `エラー: AI応答に失敗しました。${taskStatusResponse.detail || ''}`);
              this.isSending = false;
            }
            // PENDING の場合は何もしないで次のポーリングを待つ
          } catch (pollingError) {
            clearInterval(pollTaskStatus);
            this.errorMessage = `ポーリングエラー: ${pollingError.message || '不明なエラー'}`;
            console.error('ChatStore: Error during polling for task', taskId, 'Error:', pollingError);
            this.updatePendingMessage(aiMessageId, `エラー: ポーリング中に問題が発生しました。${pollingError.message || ''}`);
            this.isSending = false;
          }
        }, pollingInterval);

      } catch (error) {
        this.errorMessage = `メッセージ送信失敗: ${error.message || '不明なエラー'}`;
        console.error('ChatStore: Initial message send error:', error);
        this.updatePendingMessage(aiMessageId, `エラー: メッセージ送信に失敗しました。${error.message || ''}`);
        this.isSending = false;
      }
    },

    /**
     * Pending状態のAIメッセージを更新する.
     * @param {string} messageId - 更新するメッセージのID.
     * @param {string} newContent - 新しいメッセージ内容.
     */
    updatePendingMessage(messageId, newContent) {
      const messageIndex = this.messages.findIndex(msg => msg.id === messageId);
      if (messageIndex !== -1) {
        this.messages[messageIndex].content = newContent;
        this.messages[messageIndex].isPending = false;
      }
    },

    /**
     * 現在のチャットセッションのメッセージをクリアし、新しいセッションIDを生成する.
     */
    clearSession() {
      this.messages = [];
      this.sessionId = uuidv4();
      localStorage.setItem('sessionId', this.sessionId);
      console.log('ChatStore: Session cleared and new ID generated:', this.sessionId);
    }
  },
});
