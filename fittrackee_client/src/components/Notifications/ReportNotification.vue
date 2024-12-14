<template>
  <div class="report-notification">
    <div class="reported-workout" v-if="report.reported_workout">
      <WorkoutForUser
        :display-appeal="false"
        :display-object-name="true"
        :workout="report.reported_workout"
        :report-id="report.id"
      />
    </div>
    <div class="reported-comment" v-else-if="report.reported_comment">
      <CommentForUser
        :display-object-name="true"
        :comment="report.reported_comment"
      />
    </div>
    <div class="reported-user" v-else-if="report.reported_user">
      <UserPicture :user="report.reported_user" />
      <div class="user-name">
        <router-link :to="`/users/${report.reported_user.username}`">
          {{ report.reported_user.username }}
        </router-link>
      </div>
    </div>
    <div class="reported-user" v-else>
      <span class="deleted-object">
        {{ $t('admin.DELETED_USER') }}
      </span>
    </div>
    <div class="report-button">
      <button @click="$router.push(`/admin/reports/${report.id}`)">
        {{ $t('admin.APP_MODERATION.VIEW_REPORT') }} #{{ report.id }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import CommentForUser from '@/components/Comment/CommentForUser.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutForUser from '@/components/Workout/WorkoutForUser.vue'
  import type { IReportForModerator } from '@/types/reports'

  interface Props {
    report: IReportForModerator
  }
  const props = defineProps<Props>()
  const { report } = toRefs(props)
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';
  .report-notification {
    display: flex;
    justify-content: space-between;
    flex-wrap: wrap;

    .reported-user {
      display: flex;
      align-items: center;
      .user-picture {
        min-width: initial;
        padding: 0 $default-padding;
      }
    }
    .reported-comment,
    .reported-workout {
      width: 100%;
    }
    .report-button {
      display: flex;
      flex-direction: column;
      justify-content: center;
    }
  }
</style>
