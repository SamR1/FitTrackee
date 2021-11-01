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

<script lang="ts">
  import { PropType, computed, defineComponent } from 'vue'

  import { IUserProfile } from '@/types/user'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'UserPicture',
    props: {
      user: {
        type: Object as PropType<IUserProfile>,
        required: true,
      },
    },
    setup(props) {
      return {
        authUserPictureUrl: computed(() =>
          props.user.picture
            ? `${getApiUrl()}users/${props.user.username}/picture`
            : ''
        ),
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base.scss';

  .user-picture {
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 30%;
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
