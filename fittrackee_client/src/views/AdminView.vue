<template>
  <div id="admin">
    <div class="container" v-if="!userLoading">
      <AdministrationMenu
        v-if="isAuthUserAmin"
        :appStatistics="appStatistics"
      />
      <NotFound v-else />
    </div>
  </div>
</template>

<script lang="ts">
  import { computed, ComputedRef, defineComponent, onBeforeMount } from 'vue'

  import AdministrationMenu from '@/components/Administration/AdminMenu.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import { ROOT_STORE, USER_STORE } from '@/store/constants'
  import { IAppStatistics } from '@/types/application'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'Admin',
    components: {
      AdministrationMenu,
      NotFound,
    },
    setup() {
      const store = useStore()

      onBeforeMount(() =>
        store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_STATS)
      )

      const appLoading: ComputedRef<boolean> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_LOADING]
      )
      const appStatistics: ComputedRef<IAppStatistics> = computed(
        () => store.getters[ROOT_STORE.GETTERS.APP_STATS]
      )
      const isAuthUserAmin: ComputedRef<boolean> = computed(
        () => store.getters[USER_STORE.GETTERS.IS_ADMIN]
      )
      const userLoading: ComputedRef<boolean> = computed(
        () => store.getters[USER_STORE.GETTERS.USER_LOADING]
      )

      return { appLoading, appStatistics, isAuthUserAmin, userLoading }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
</style>
