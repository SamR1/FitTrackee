<template>
  <NavBar @menuInteraction="updateHideScrollBar" />
  <div v-if="appLoading" class="app-container">
    <div class="app-loading">
      <Loader />
    </div>
  </div>
  <div v-else class="app-container" :class="{ 'hide-scroll': hideScrollBar }">
    <router-view v-if="appConfig" />
    <NoConfig v-else />
  </div>
  <Footer />
</template>

<script lang="ts">
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
  import {
    ComputedRef,
    computed,
    defineComponent,
    ref,
    onBeforeMount,
  } from 'vue'

  import Loader from '@/components/Common/Loader.vue'
  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'
  import NoConfig from '@/components/NoConfig.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { IAppConfig } from '@/types/application'
  import { useStore } from '@/use/useStore'

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

  export default defineComponent({
    name: 'App',
    components: {
      Footer,
      Loader,
      NavBar,
      NoConfig,
    },
    setup() {
      const store = useStore()

      const appConfig: ComputedRef<IAppConfig> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
      )
      const appLoading: ComputedRef<boolean> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_LOADING]
      )
      const hideScrollBar = ref(false)

      function updateHideScrollBar(isMenuOpen: boolean) {
        hideScrollBar.value = isMenuOpen
      }

      onBeforeMount(() =>
        store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG)
      )

      return {
        appConfig,
        appLoading,
        hideScrollBar,
        updateHideScrollBar,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  .app-container {
    height: $app-height;

    &.hide-scroll {
      overflow: hidden;
    }

    .app-loading {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }
</style>
