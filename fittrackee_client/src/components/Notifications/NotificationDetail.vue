<template>
  <Card
    class="notification-card"
    :class="{ read: notification.marked_as_read }"
    v-if="notification.id"
  >
    <template #title>
      <div>
        <i
          :class="`fa-${icon}`"
          class="fa notification-icon"
          aria-hidden="true"
        />
        <router-link :to="`/users/${notification.from.username}`">
          {{ notification.from.username }}
        </router-link>
        {{ $t(getUserAction(notification.type)) }}
      </div>
      <div>
        <button
          class="mark-action"
          :title="
            $t(
              `notifications.MARK_AS_${
                notification.marked_as_read ? 'UN' : ''
              }READ`
            )
          "
          @click="
            () =>
              updateReadStatus(notification.id, !notification.marked_as_read)
          "
        >
          <span class="hidden-content">
            {{
              $t(
                `notifications.MARK_AS_${
                  notification.marked_as_read ? 'UN' : ''
                }READ`
              )
            }}
          </span>
          <i
            class="fa"
            :class="`fa-eye${notification.marked_as_read ? '-slash' : ''}`"
            aria-hidden="true"
          />
        </button>
      </div>
    </template>
    <template #content>
      <Comment
        v-if="displayCommentCard(notification.type) && notification.comment"
        :comment="notification.comment"
        :authUser="authUser"
        comments-loading="null"
        :for-notification="true"
      />
      <RelationshipDetail
        v-else-if="displayRelationshipCard(notification.type)"
        :notification="notification"
        :authUser="authUser"
        @updatedUserRelationship="emitReload"
      />
      <ReportNotification
        v-else-if="
          ['report', 'suspension_appeal'].includes(notification.type) &&
          notification.report
        "
        :report="notification.report"
      />
      <WorkoutCard
        v-else-if="notification.workout && sport"
        :workout="notification.workout"
        :sport="sport"
        :user="notification.workout?.user"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
      />
    </template>
  </Card>
</template>
<script lang="ts" setup>
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import Comment from '@/components/Comment/Comment.vue'
  import RelationshipDetail from '@/components/Notifications/RelationshipDetail.vue'
  import ReportNotification from '@/components/Notifications/ReportNotification.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import { ROOT_STORE, SPORTS_STORE } from '@/store/constants'
  import type { TLanguage } from '@/types/locales'
  import type { INotification, TNotificationType } from '@/types/notifications'
  import type { ISport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDateFormat } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
    notification: INotification
  }

  const props = defineProps<Props>()
  const { authUser, notification } = toRefs(props)

  const store = useStore()

  const sports: ComputedRef<ISport[]> = computed(
    () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
  )
  const appLanguage: ComputedRef<TLanguage> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const sport: ComputedRef<ISport | null> = computed(() => getSport())
  const dateFormat = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const icon = computed(() => getIcon(notification.value.type))
  const emit = defineEmits(['reload', 'updateReadStatus'])

  function emitReload() {
    emit('reload')
  }
  function updateReadStatus(notificationId: number, markedAsRead: boolean) {
    emit('updateReadStatus', { notificationId, markedAsRead })
  }
  function getSport(): ISport | null {
    return notification.value.workout
      ? sports.value.filter(
          (s) => s.id === notification.value.workout?.sport_id
        )[0]
      : null
  }
  function displayCommentCard(notificationType: TNotificationType) {
    return [
      'comment_like',
      'comment_reply',
      'mention',
      'workout_comment',
    ].includes(notificationType)
  }
  function displayRelationshipCard(notificationType: TNotificationType) {
    return ['follow', 'follow_request'].includes(notificationType)
  }
  function getUserAction(notificationType: TNotificationType): string {
    switch (notificationType) {
      case 'comment_like':
        return 'notifications.LIKED_YOUR_COMMENT'
      case 'comment_reply':
        return 'notifications.REPLIED_YOUR_COMMENT'
      case 'follow':
        return 'user.RELATIONSHIPS.FOLLOWS_YOU'
      case 'follow_request':
        return 'notifications.SEND_FOLLOW_REQUEST_TO_YOU'
      case 'mention':
        return 'notifications.MENTIONED_YOU'
      case 'suspension_appeal':
        return 'notifications.APPEALED_SUSPENSION'
      case 'workout_comment':
        return 'notifications.COMMENTED_YOUR_WORKOUT'
      case 'workout_like':
        return 'notifications.LIKED_YOUR_WORKOUT'
      case 'report':
        return `notifications.REPORTED_USER_${
          notification.value.report?.object_type
            ? notification.value.report.object_type.toUpperCase()
            : ''
        }`
    }
  }
  function getIcon(notificationType: TNotificationType): string {
    switch (notificationType) {
      case 'mention':
        return 'at'
      case 'suspension_appeal':
      case 'report':
        return 'flag'
      default:
        return 'comment'
    }
  }
</script>

<style scoped lang="scss">
  @import '~@/scss/vars';

  .notification-card {
    ::v-deep(.card-title) {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      flex-wrap: wrap;

      .notification-icon {
        padding-right: 5px;
      }

      .mark-action {
        font-weight: initial;
        font-style: italic;
        border: none;
        box-shadow: none;
      }

      ::v-deep(.workout-card) {
        margin: 0;

        .box {
          margin: $default-margin 0;
        }
      }
    }

    &.read {
      color: var(--app-color-lighter);

      ::v-deep(.workout-comment),
      ::v-deep(.follow-request) {
        .user-picture {
          img {
            opacity: 0.5;
          }
          .no-picture {
            color: var(--app-color-lighter);
          }
        }
      }
      ::v-deep(.workout-comment) {
        .fa-heart {
          color: var(--app-color-lighter);
        }
      }
      ::v-deep(a) {
        color: var(--app-color-lighter);
      }

      .mark-action {
        color: var(--app-color-lighter);
        &:hover {
          background: var(--app-color-lighter);
          color: var(--button-confirm-bg-color);
        }
      }
    }
  }
</style>
