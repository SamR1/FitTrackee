<template>
  <div class="notification-object" v-if="displayObjectName">
    {{ $t('workouts.COMMENTS.COMMENT') }}:
  </div>
  <div class="box comment-box">
    <Comment
      :comment="comment"
      :authUser="authUser"
      :display-appeal="false"
      comments-loading="null"
      :for-notification="true"
    />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import Comment from '@/components/Comment/Comment.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import type { IUserAdminAction } from '@/types/user'
  import type { IComment } from '@/types/workouts'

  interface Props {
    action: IUserAdminAction
    displayAppeal: boolean
    comment: IComment
    displayObjectName: boolean
  }
  const props = defineProps<Props>()
  const { comment, displayObjectName } = toRefs(props)

  const { authUser } = useAuthUser()
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';

  .notification-object {
    font-weight: bold;
    text-transform: capitalize;
  }
  .appeal-action {
    .appeal {
      padding: 0 $default-padding;
    }

    .appeal-button {
      padding: 0 $default-padding;
      font-size: 0.9em;
    }
  }
</style>
