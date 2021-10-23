import { createApp } from 'vue'

import './registerServiceWorker'
import App from './App.vue'
import i18n from './i18n'
import router from './router'
import store from './store'

import { customComponents } from '@/custom-components'
import { clickOutsideDirective } from '@/directives'

const app = createApp(App)
  .use(i18n)
  .use(store)
  .use(router)
  .directive('click-outside', clickOutsideDirective)

customComponents.forEach((component) => {
  app.component(component.name, component)
})

app.mount('#app')
