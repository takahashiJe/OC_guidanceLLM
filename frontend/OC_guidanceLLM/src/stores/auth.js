// stores/auth.js
import { defineStore } from 'pinia';
import { jwtDecode } from 'jwt-decode';
import apiClient from '../services/api'; // 作成したapiClientをインポート
import router from '../router';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    accessToken: localStorage.getItem('accessToken'),
    // ユーザー名はトークンから取得するか、ログイン時のレスポンスに含めるのが望ましい
    // ここではシンプルにするため、ログイン状態のみを管理
    isLoading: false,
    errorMessage: null,
    successMessage: null, 
  }),

  getters: {
    isAuthenticated: (state) => !!state.accessToken,
  },

  actions: {
    /**
     * ログイン処理
     */
    async login(credentials) {
      this.isLoading = true;
      this.errorMessage = null;
      try {
        const formData = new URLSearchParams();
        formData.append('username', credentials.username);
        formData.append('password', credentials.password);
        
        const response = await apiClient.post('/auth/login', formData, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        });

        const { access_token } = response.data;
        this.accessToken = access_token;
        localStorage.setItem('accessToken', access_token);
        
        // ログイン成功後、チャットページへリダイレクト
        router.push('/chat');

      } catch (error) {
        // ★★★ ここから修正 ★★★
        // 実際に発生したエラーオブジェクトをコンソールに出力
        console.error('ログイン処理で予期せぬエラーが発生しました:', error);

        // ユーザーには、より具体的なエラーメッセージを表示
        this.errorMessage = 'ログイン中に予期せぬエラーが発生しました。コンソールを確認してください。';
        // ★★★ ここまで修正 ★★★
        this.isLoading = false;
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * 新規登録処理
     */
    async register(details) {
      this.isLoading = true;
      this.errorMessage = null;
      this.successMessage = null;
      try {
        // 新規登録APIはJSON形式でデータを送信
        await apiClient.post('/auth/register', {
          username: details.username,
          password: details.password,
        });
        
        // 登録成功時のメッセージを設定
        this.successMessage = '新規登録が完了しました。ログインしてください。';

      } catch (err) {
        this.errorMessage = err.response?.data?.detail || 'このユーザー名は既に使用されているなど、登録に失敗しました。';
        throw new Error(this.errorMessage);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * ログアウト処理
     */
    logout() {
      this.accessToken = null;
      localStorage.removeItem('accessToken');
      localStorage.removeItem('sessionId'); // セッション情報もクリア
      // ログアウト後、ログインページへリダイレクト
      router.push('/login');
    },

    /**
     * ★★★ 新しく追加したアクション ★★★
     * トークンの有効性をクライアントサイドでチェックする。
     */
    checkTokenValidity() {
      if (!this.accessToken) {
        return;
      }

      try {
        const decodedToken = jwtDecode(this.accessToken);
        const currentTime = Date.now() / 1000;

        if (decodedToken.exp < currentTime) {
          console.log('クライアントサイドでトークンの期限切れを検知しました。');
          this.logout();
        }
      } catch (error) {
        console.error('トークンの解析に失敗しました。不正なトークンの可能性があります。', error);
        this.logout();
      }
    },
  },
});