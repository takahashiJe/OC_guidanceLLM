// stores/auth.js
import { defineStore } from 'pinia';
import { loginUser, registerUser } from '../services/api'; 

/**
 * @typedef {Object} UserInfo
 * @property {string} username - The username of the logged-in user.
 * // Add other user properties as needed (e.g., email, id)
 */

/**
 * @typedef {Object} AuthState
 * @property {boolean} isLoggedIn - Indicates if the user is currently logged in.
 * @property {string | null} accessToken - The JWT access token received from the backend.
 * @property {UserInfo | null} user - Information about the logged-in user.
 * @property {boolean} isLoading - Indicates if an authentication operation is in progress.
 * @property {string | null} errorMessage - Stores any error message from authentication operations.
 */

/**
 * Auth store for managing user authentication state.
 * Handles login, logout, and token persistence in localStorage.
 */
export const useAuthStore = defineStore('auth', {
  /**
   * @returns {AuthState} The initial state of the authentication store.
   */
  state: () => ({
    isLoggedIn: false,
    accessToken: null,
    user: null,
    isLoading: false,
    errorMessage: null,
  }),

  actions: {
    /**
     * Initializes the authentication state by checking for an existing token in localStorage.
     * If a token is found, sets the user as logged in.
     */
    initAuth() {
      console.log('AuthStore: Initializing authentication state.');
      try {
        const token = localStorage.getItem('accessToken');
        if (token) {
          this.accessToken = token;
          this.isLoggedIn = true;
          // In a real application, you would typically decode the token
          // or make an API call to get user info based on the token.
          // For now, we'll set a dummy user.
          this.user = { username: 'authenticated_user' }; 
          console.log('AuthStore: Found access token in localStorage. User is logged in.');
        } else {
          console.log('AuthStore: No access token found in localStorage.');
        }
      } catch (error) {
        console.error('AuthStore: Error initializing auth from localStorage:', error);
        this.clearAuth(); // Clear any corrupted state
      }
    },

    /**
     * Attempts to log in the user with provided credentials.
     * @param {Object} credentials - User login credentials.
     * @param {string} credentials.username - The user's username.
     * @param {string} credentials.password - The user's password.
     * @returns {Promise<void>} A promise that resolves when login is attempted.
     */
    async login(credentials) {
      this.isLoading = true;
      this.errorMessage = null;
      console.log('AuthStore: Attempting login for user:', credentials.username);

      try {
        // ★★★ ダミーAPI呼び出しを実際のAPI呼び出しに置き換え ★★★
        const response = await loginUser(credentials); 
        
        const { access_token } = response; // レスポンスからアクセストークンを取得

        localStorage.setItem('accessToken', access_token);
        this.accessToken = access_token;
        this.isLoggedIn = true;
        // 実際のユーザー情報をレスポンスから取得できる場合は設定
        this.user = { username: credentials.username }; // 仮のユーザー情報
        console.log('AuthStore: Login successful!');
        // リダイレクトはApp.vueのウォッチャーが処理
      } catch (error) {
        this.errorMessage = error.message; // APIサービスからスローされたエラーメッセージ
        console.error('AuthStore: Login API error:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Attempts to register a new user with provided details.
     * @param {Object} details - User registration details.
     * @param {string} details.username - The desired username.
     * @param {string} details.password - The desired password.
     * @returns {Promise<void>} A promise that resolves when registration is attempted.
     */
    async register(details) {
      this.isLoading = true;
      this.errorMessage = null;
      console.log('AuthStore: Attempting registration for user:', details.username);

      try {
        // ★★★ ダミーAPI呼び出しを実際のAPI呼び出しに置き換え ★★★
        const response = await registerUser(details); 

        // 登録成功後、通常は自動ログインさせるか、ログイン画面にリダイレクト
        // 今回は登録後自動ログインさせる
        const { access_token } = response; // 登録APIがトークンを返す場合
        if (access_token) {
          localStorage.setItem('accessToken', access_token);
          this.accessToken = access_token;
          this.isLoggedIn = true;
          this.user = { username: details.username };
          console.log('AuthStore: Registration successful and logged in!');
        } else {
          // 登録APIがトークンを返さない場合、ログイン画面へリダイレクト
          // router.push('/login'); // Vue Routerをインポートして使用
          this.errorMessage = 'Registration successful, please log in.';
          console.log('AuthStore: Registration successful, no auto-login token.');
        }
      } catch (error) {
        this.errorMessage = error.message; // APIサービスからスローされたエラーメッセージ
        console.error('AuthStore: Registration API error:', error);
      } finally {
        this.isLoading = false;
      }
    },

    /**
     * Logs out the current user by clearing the access token from localStorage.
     */
    logout() {
      console.log('AuthStore: Logging out user.');
      this.clearAuth();
      // Router redirection is handled by App.vue watcher
    },

    /**
     * Clears all authentication-related state and localStorage items.
     */
    clearAuth() {
      localStorage.removeItem('accessToken');
      // Also clear chat session ID on logout to start fresh conversation
      localStorage.removeItem('sessionId'); 
      this.isLoggedIn = false;
      this.accessToken = null;
      this.user = null;
      this.errorMessage = null;
      console.log('AuthStore: Authentication state cleared.');
    }
  },
});
