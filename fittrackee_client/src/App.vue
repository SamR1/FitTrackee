<template>
  <NavBar />
  <div v-if="appLoading" class="app-container">
    <div class="app-loading">
      <Loader />
    </div>
  </div>
  <div v-else class="app-container">
    <router-view v-if="appConfig" />
    <NoConfig v-else />
  </div>
  <Footer />
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent, onBeforeMount } from 'vue'

  import Loader from '@/components/Common/Loader.vue'
  import Footer from '@/components/Footer.vue'
  import NavBar from '@/components/NavBar.vue'
  import NoConfig from '@/components/NoConfig.vue'
  import { ROOT_STORE } from '@/store/constants'
  import { IAppConfig } from '@/store/modules/root/interfaces'
  import { useStore } from '@/use/useStore'

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
      onBeforeMount(() =>
        store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_CONFIG)
      )
      return {
        appConfig,
        appLoading,
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  .app-container {
    height: $app-height;

    .app-loading {
      display: flex;
      align-items: center;
      height: 100%;
    }
  }
</style>
