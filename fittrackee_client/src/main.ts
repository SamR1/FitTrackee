import { createApp } from 'vue'

import './registerServiceWorker'
import App from './App.vue'
import i18n from './i18n'
import router from './router'
import store from './store'

createApp(App).use(i18n).use(store).use(router).mount('#app')
