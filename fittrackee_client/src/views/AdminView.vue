<template>
  <div id="admin" class="view">
    <div class="container" v-if="!authUserLoading">
      <router-view v-if="authUserHasModeratorRights" />
      <NotFound v-else />
      <div id="bottom" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { onBeforeMount } from 'vue'

  import NotFound from '@/components/Common/NotFound.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { ROOT_STORE } from '@/store/constants'
  import { useStore } from '@/use/useStore'

  const store = useStore()

  const { authUserHasModeratorRights, authUserLoading } = useAuthUser()

  onBeforeMount(() => {
    if (authUserHasModeratorRights.value) {
      store.dispatch(ROOT_STORE.ACTIONS.GET_APPLICATION_STATS)
    }
  })
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

            input {
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
                background-color: var(--admin-disabled-input-color);
                border-color: var(--admin-disabled-input-color);
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
