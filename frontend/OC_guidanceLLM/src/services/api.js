    // services/api.js
    import axios from 'axios';

    const API_BASE_URL = 'http://localhost:8000'; // 開発時はlocalhost:8000にマッピング

    /**
     * ユーザーログインAPIを呼び出します。
     * @param {Object} credentials - ユーザー名とパスワード
     * @returns {Promise<Object>} 成功時: { access_token: string }, 失敗時: エラー
     */
    export const loginUser = async (credentials) => {
      try {
        // ★★★ ここを修正: フォームデータ形式に変換 ★★★
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);

        const response = await axios.post(`${API_BASE_URL}/auth/login`, formData, {
          headers: {
            'Content-Type': 'application/x-www-form-urlencoded', // ★★★ Content-Typeを変更 ★★★
          },
        });
        return response.data; // access_tokenを含むデータを返す
      } catch (error) {
        console.error('API Service: Login failed', error.response || error);
        // エラーメッセージの整形を改善
        const errorMessage = error.response?.data?.detail 
                             ? (Array.isArray(error.response.data.detail) 
                                 ? error.response.data.detail.map(err => err.msg).join(', ') 
                                 : error.response.data.detail)
                             : 'ログインに失敗しました。';
        throw new Error(errorMessage);
      }
    };

    /**
     * ユーザー登録APIを呼び出します。
     * @param {Object} details - ユーザー名とパスワード
     * @returns {Promise<Object>} 成功時: 登録されたユーザー情報, 失敗時: エラー
     */
    export const registerUser = async (details) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/auth/register`, {
          username: details.username,
          password: details.password,
        }, {
          headers: {
            'Content-Type': 'application/json', // 登録は通常JSONなので変更しない
          },
        });
        return response.data; // 登録成功時のデータを返す
      } catch (error) {
        console.error('API Service: Registration failed', error.response || error);
        const errorMessage = error.response?.data?.detail 
                             ? (Array.isArray(error.response.data.detail) 
                                 ? error.response.data.detail.map(err => err.msg).join(', ') 
                                 : error.response.data.detail)
                             : '登録に失敗しました。';
        throw new Error(errorMessage);
      }
    };

    /**
     * チャットメッセージ送信APIを呼び出します。
     * @param {Object} chatData - メッセージとセッションID
     * @param {string} chatData.message - ユーザーメッセージ
     * @param {string} chatData.session_id - セッションID
     * @param {string} accessToken - 認証用アクセストークン
     * @returns {Promise<Object>} AIの応答
     */
    export const postChatMessage = async (chatData, accessToken) => {
      try {
        const response = await axios.post(`${API_BASE_URL}/chat`, chatData, {
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${accessToken}`, // 認証ヘッダーを追加
          },
        });
        return response.data; // AIの応答を返す
      } catch (error) {
        console.error('API Service: Chat message failed', error.response || error);
        const errorMessage = error.response?.data?.detail 
                             ? (Array.isArray(error.response.data.detail) 
                                 ? error.response.data.detail.map(err => err.msg).join(', ') 
                                 : error.response.data.detail)
                             : 'メッセージの送信に失敗しました。';
        throw new Error(errorMessage);
      }
    };
    
    /**
     * 指定されたタスクIDのステータスを取得します。
     * @param {string} taskId - 取得するタスクのID。
     * @param {string} accessToken - 認証用アクセストークン。
     * @returns {Promise<Object>} タスクのステータスと結果を含むレスポンス。
     */
    export const getTaskStatus = async (taskId, accessToken) => {
      try {
        // ★★★ ここを修正: URLを /chat/results/{taskId} に変更 ★★★
        const response = await axios.get(`${API_BASE_URL}/chat/results/${taskId}`, {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });
        return response.data;
      } catch (error) {
        console.error('API Service: Failed to get task status', error.response || error);
        throw new Error(error.response?.data?.detail || 'タスクステータスの取得に失敗しました。');
      }
    };