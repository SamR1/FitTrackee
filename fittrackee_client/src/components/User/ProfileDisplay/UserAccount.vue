<template>
  <div id="user-account" class="description-list">
    <div>
      <dl>
        <dt>{{ $t('user.EMAIL') }}:</dt>
        <dd>{{ user.email }}</dd>
      </dl>
    </div>
    <div class="profile-buttons">
      <button @click="$router.push('/profile/edit/account')">
        {{ $t('user.PROFILE.EDIT_ACCOUNT') }}
      </button>
      <button
        class="confirm"
        :disabled="!canRequestExport()"
        @click.prevent="requestExport"
      >
        {{ $t('buttons.REQUEST_DATA_EXPORT') }}
      </button>
    </div>
    <UserDataExport :user="user" />
  </div>
</template>

<script setup lang="ts">
  import { onMounted, toRefs } from 'vue'

  import UserDataExport from '@/components/User/UserDataExport.vue'
  import useUserDataExport from '@/composables/useUserDataExport.ts'
  import { AUTH_USER_STORE } from '@/store/constants.ts'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore.ts'

  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { user } = toRefs(props)

  const store = useStore()
  const { canRequestExport, requestExport } = useUserDataExport()

  onMounted(() => {
    if (props.user) {
      store.dispatch(AUTH_USER_STORE.ACTIONS.GET_REQUEST_DATA_EXPORT)
    }
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #user-account {
    #user-account-data {
      padding: 0 0 $default-padding;
    }
    .profile-buttons {
      margin-bottom: $default-margin;
    }
  }
</style>
