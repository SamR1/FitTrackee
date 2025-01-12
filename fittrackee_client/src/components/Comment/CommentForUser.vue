<template>
  <div class="notification-object" v-if="displayObjectName">
    {{ $t('workouts.COMMENTS.COMMENT') }}:
  </div>
  <div class="box comment-box">
    <Comment
      :comment="comment"
      :authUser="authUser"
      :display-appeal="false"
      :hide-suspension-appeal="displayObjectName"
      comments-loading="null"
      :for-notification="true"
      :action="action"
      @commentLinkClicked="$emit('commentLinkClicked')"
    />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import Comment from '@/components/Comment/Comment.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import type { IUserReportAction } from '@/types/user'
  import type { IComment } from '@/types/workouts'

  interface Props {
    comment: IComment
    displayObjectName: boolean
    action?: IUserReportAction | null
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
</style>
