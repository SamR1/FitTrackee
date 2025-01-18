<template>
  <div class="report-notification">
    <div class="reported-workout" v-if="report.object_type === 'workout'">
      <WorkoutForUser
        v-if="report.reported_workout"
        :display-appeal="false"
        :display-object-name="true"
        :workout="report.reported_workout"
        :report-id="report.id"
      />
      <div class="deleted-object" v-else>
        {{ $t('admin.DELETED_WORKOUT') }}
      </div>
    </div>
    <div class="reported-comment" v-if="report.object_type === 'comment'">
      <CommentForUser
        v-if="report.reported_comment"
        :display-object-name="true"
        :comment="report.reported_comment"
      />
      <div class="deleted-object" v-else>
        {{ $t('admin.DELETED_COMMENT') }}
      </div>
    </div>
    <template v-if="report.object_type === 'user'">
      <div class="reported-user" v-if="report.reported_user">
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
    </template>
    <div class="report-button">
      <button @click="displayReport(report.id)">
        {{ $t('admin.APP_MODERATION.VIEW_REPORT') }} #{{ report.id }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'
  import { useRouter } from 'vue-router'

  import CommentForUser from '@/components/Comment/CommentForUser.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutForUser from '@/components/Workout/WorkoutForUser.vue'
  import type { IReportForModerator } from '@/types/reports'

  interface Props {
    report: IReportForModerator
  }
  const props = defineProps<Props>()
  const { report } = toRefs(props)

  const emit = defineEmits(['reportButtonClicked'])

  const router = useRouter()

  function displayReport(reportId: number) {
    router.push(`/admin/reports/${reportId}`)
    emit('reportButtonClicked')
  }
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
    .deleted-object {
      margin: 0 0 $default-margin;
    }
  }
</style>
