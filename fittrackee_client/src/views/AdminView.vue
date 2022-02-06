<template>
  <div id="admin" class="view">
    <div class="container" v-if="!userLoading">
      <router-view
        v-if="isAuthUserAmin"
        :appConfig="appConfig"
        :appStatistics="appStatistics"
      />
      <NotFound v-else />
      <div id="bottom" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, ComputedRef, onBeforeMount } from 'vue'

  import NotFound from '@/components/Common/NotFound.vue'
  import { AUTH_USER_STORE, ROOT_STORE } from '@/store/constants'
  import { TAppConfig, IAppStatistics } from '@/types/application'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  const appStatistics: ComputedRef<IAppStatistics> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_STATS]
  )
  const isAuthUserAmin: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.IS_ADMIN]
  )
  const userLoading: ComputedRef<boolean> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.USER_LOADING]
  )

  onBeforeMount(() => store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_STATS))
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #admin {
    .admin-card {
      width: 100%;

      ::v-deep(.card) {
        .admin-form {
          display: flex;
          flex-direction: column;

          label {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin: $default-margin 0;
            flex-wrap: wrap;

            input[type='text'],
            input[type='number'] {
              width: 50%;
              font-size: 0.9em;
              margin-right: $default-margin * 5;
              @media screen and (max-width: $medium-limit) {
                margin-right: 0;
              }
              @media screen and (max-width: $small-limit) {
                width: 100%;
              }

              &:disabled {
                -webkit-appearance: none;
                -moz-appearance: textfield;
                background-color: white;
                border-color: white;
                color: var(--app-color);
              }
            }
          }
          .form-buttons {
            display: flex;
            gap: $default-padding;
            margin-bottom: $default-margin;
          }
        }
      }
    }
  }
</style>
