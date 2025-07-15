// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth'; // Authストアをインポート

// ルート定義
const routes = [
  {
    path: '/', // デフォルトルート
    redirect: '/login' // ログイン画面にリダイレクト
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('../views/AuthView.vue'), // AuthViewコンポーネントを遅延ロード
    meta: { requiresAuth: false } // 認証不要なルート
  },
  {
    path: '/chat',
    name: 'Chat',
    component: () => import('../views/ChatView.vue'), // ChatViewコンポーネントを遅延ロード
    meta: { requiresAuth: true } // 認証が必要なルート
  },
  // 存在しないルートへのフォールバック
  {
    path: '/:pathMatch(.*)*',
    name: 'NotFound',
    redirect: '/login' // 未知のパスはログイン画面にリダイレクト
  }
];

// ルーターインスタンスを作成
const router = createRouter({
  history: createWebHistory(), // HTML5 History APIを使用
  routes,
});

// グローバルナビゲーションガード
// ルート遷移前に実行され、認証状態をチェックします
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore(); // Piniaストアはここでも使用可能

  // ルートのメタ情報から認証が必要かチェック
  const requiresAuth = to.meta.requiresAuth;
  const isLoggedIn = authStore.isLoggedIn;

  console.log(`Router: Navigating to ${to.path}. Requires auth: ${requiresAuth}, Logged in: ${isLoggedIn}`);

  if (requiresAuth && !isLoggedIn) {
    // 認証が必要なルートに、ログインしていない状態でアクセスしようとした場合
    console.log('Router: Not logged in, redirecting to /login.');
    next('/login'); // ログイン画面へリダイレクト
  } else if ((to.path === '/login' || to.path === '/') && isLoggedIn) {
    // ログイン画面またはデフォルトルートに、ログイン済みでアクセスしようとした場合
    console.log('Router: Already logged in, redirecting to /chat.');
    next('/chat'); // チャット画面へリダイレクト
  } else {
    // それ以外の場合は、そのまま遷移を許可
    console.log('Router: Navigation allowed.');
    next();
  }
});

export default router;
