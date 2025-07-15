// main.js

import { createApp } from 'vue'; // Vueアプリケーションを作成するための関数をインポート
import { createPinia } from 'pinia'; // Piniaストアを作成するための関数をインポート
import App from './App.vue'; // ルートコンポーネントであるApp.vueをインポート
import router from './router'; // Vue Routerのインスタンスをインポート (後で作成)

import './assets/main.css'; // Tailwind CSSのベースとなるCSSファイルをインポート (後で作成)

// Vueアプリケーションインスタンスを作成
const app = createApp(App);

// Piniaストアを使用するように設定
const pinia = createPinia();
app.use(pinia);

// Vue Routerを使用するように設定
app.use(router);

// アプリケーションをHTMLの#app要素にマウント
app.mount('#app');

console.log('Vue application mounted successfully!');
