// services/api.js
import axios from 'axios';
import { useAuthStore } from '../stores/auth';

// 1. APIクライアントの作成と基本設定
const apiClient = axios.create({
  // 環境変数からAPIのベースURLを読み込むか、デフォルト値を設定
  // baseURL: import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000',
  baseURL: import.meta.env.VITE_API_BASE_URL || 'https://ibera.cps.akita-pu.ac.jp/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

// 2. リクエストインターセプター：全てのリクエストに自動でトークンを付与
apiClient.interceptors.request.use(
  (config) => {
    // リクエストを送信する直前にストアからトークンを取得
    const authStore = useAuthStore();
    if (authStore.accessToken) {
      config.headers['Authorization'] = `Bearer ${authStore.accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// 3. レスポンスインターセプター：APIからの応答をグローバルに監視
apiClient.interceptors.response.use(
  // 成功レスポンスはそのまま返す
  (response) => response,
  // エラーレスポンスをここで一括処理
  (error) => {
    // レスポンスを受け取った後にストアを取得
    const authStore = useAuthStore();

    // 認証エラー（401 Unauthorized）の場合
    if (error.response && error.response.status === 401) {
      // ログインしている状態でのみログアウト処理を実行
      if (authStore.isAuthenticated) {
        console.error('APIから401エラー。トークンが無効または期限切れです。');
        // Piniaストアのログアウトアクションを呼び出す
        authStore.logout();
      }
    }
    
    // 他のエラーは呼び出し元で処理できるよう、そのままスローする
    return Promise.reject(error);
  }
);

export default apiClient;