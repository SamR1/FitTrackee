import {
  Chart,
  BarElement,
  LineElement,
  PointElement,
  Legend,
  Title,
  Tooltip,
  Filler,
  BarController,
  CategoryScale,
  LineController,
  LinearScale,
} from 'chart.js'
import ChartDataLabels from 'chartjs-plugin-datalabels'
import { createApp } from 'vue'

import './registerServiceWorker'
import App from './App.vue'
import i18n from './i18n'
import router from './router'
import store from './store'

import { customComponents } from '@/custom-components'
import { clickOutsideDirective } from '@/directives'
import { sportColors } from '@/utils/sports'

Chart.register(
  BarElement,
  LineElement,
  PointElement,
  Legend,
  Title,
  Tooltip,
  Filler,
  BarController,
  CategoryScale,
  LineController,
  LinearScale,
  ChartDataLabels
)

const app = createApp(App)
  .provide('sportColors', sportColors)
  .use(i18n)
  .use(store)
  .use(router)
  .directive('click-outside', clickOutsideDirective)

customComponents.forEach((component) => {
  app.component(component.name, component)
})

app.mount('#app')
