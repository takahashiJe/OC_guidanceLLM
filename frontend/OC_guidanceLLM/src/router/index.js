import { createRouter, createWebHistory } from 'vue-router';
import { useAuthStore } from '../stores/auth';
import AuthView from '../views/AuthView.vue';
import ChatView from '../views/ChatView.vue';

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: AuthView,
  },
  {
    path: '/chat',
    name: 'Chat',
    component: ChatView,
    // このルートは認証が必要であることを示すメタ情報
    meta: { requiresAuth: true },
  },
  {
    // アプリのルートパスにアクセスした場合、ログイン状態に応じてリダイレクト
    path: '/',
    redirect: () => {
      const authStore = useAuthStore();
      return authStore.isAuthenticated ? '/chat' : '/login';
    },
  },
  {
    // どのルートにも一致しない場合、ルートパスにリダイレクト
    path: '/:pathMatch(.*)*',
    redirect: '/',
  },
];

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
});

/**
 * グローバルナビゲーションガード
 * すべてのルート遷移の直前に実行される
 */
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore();

  const requiresAuth = to.meta.requiresAuth;

  // ★★★ ログイン状態のチェックを isAuthenticatd ゲッターに変更 ★★★
  const isAuthenticated = authStore.isAuthenticated;

  // ログインが必要なページに、未ログインでアクセスしようとした場合
  if (requiresAuth && !isAuthenticated) {
    console.log(`Router: 認証が必要なページ(${to.path})ですが、未ログインのため/loginへリダイレクトします。`);
    // /loginページにリダイレクト
    next('/login');
  }
  // ログインページに、ログイン済みの状態でアクセスしようとした場合
  else if (to.name === 'Login' && isAuthenticated) {
    console.log(`Router: ログイン済みのため、/chatへリダイレクトします。`);
    // /chatページにリダイレクト
    next('/chat');
  }
  // 上記以外の場合は、そのまま遷移を許可
  else {
    next();
  }
});

export default router;