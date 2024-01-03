<template>
  <div class="user-picture">
    <img
      v-if="authUserPictureUrl !== ''"
      class="profile-user-img"
      :alt="$t('user.USER_PICTURE')"
      :src="authUserPictureUrl"
    />
    <div v-else class="no-picture">
      <i class="fa fa-user-circle-o" aria-hidden="true" />
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed } from 'vue'

  import type { IUserProfile } from '@/types/user'
  import { getApiUrl } from '@/utils'
  import { getUserName } from '@/utils/user'

  interface Props {
    user: IUserProfile
  }
  const props = defineProps<Props>()

  const authUserPictureUrl = computed(() =>
    props.user.picture
      ? `${getApiUrl()}users/${getUserName(props.user)}/picture?${Date.now()}`
      : ''
  )
</script>

<style lang="scss">
  .user-picture {
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 30%;
    line-height: 1.2em;
    img {
      border-radius: 50%;
      height: 90px;
      width: 90px;
    }
    .no-picture {
      color: var(--app-a-color);
      font-size: 5.5em;
    }
  }
</style>
