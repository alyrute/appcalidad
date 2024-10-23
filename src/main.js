// src/main.js
import { createApp } from 'vue';
import App from './App.vue';
import router from './router/index.js';  // Asegúrate de la ruta correcta
import store from './stores/index.js';    // Asegúrate de la ruta correcta

createApp(App)
  .use(router)  // Usa el router
  .use(store)   // Usa Vuex
  .mount('#app');
