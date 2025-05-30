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
        <router-link
          :to="`/users/${notification.from.username}`"
          v-if="
            notification.from &&
            !['user_data_export', 'workouts_archive_upload'].includes(
              notification.type
            )
          "
        >
          {{ notification.from.username }}
        </router-link>
        {{ $t(getUserAction(notification.type)) }}
      </div>
      <div class="notification-data-button">
        <div class="notification-date">
          {{
            formatDistance(new Date(notification.created_at), new Date(), {
              addSuffix: true,
              locale,
            })
          }}
        </div>
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
      <div v-if="notification.report_action?.reason">
        <span class="notification-reason">
          {{ $t('admin.APP_MODERATION.REASON') }}:
        </span>
        {{ notification.report_action.reason }}
      </div>
      <template v-if="displayCommentNotification()">
        <CommentForUser
          v-if="notification.comment"
          :display-object-name="notification.type.startsWith('user_warning')"
          :comment="notification.comment"
          :action="notification.report_action"
          @commentLinkClicked="markAsReadOnClick(notification)"
        />
        <div class="deleted-object" v-else>
          {{ $t('admin.DELETED_COMMENT') }}
        </div>
      </template>
      <RelationshipDetail
        v-else-if="displayRelationshipCard(notification.type)"
        :notification="notification"
        :authUser="authUser"
        @updatedUserRelationship="emitReload"
        @userLinkClicked="markAsReadOnClick(notification)"
      />
      <ReportNotification
        v-else-if="
          ['report', 'suspension_appeal', 'user_warning_appeal'].includes(
            notification.type
          ) && notification.report
        "
        :report="notification.report"
        @reportButtonClicked="markAsReadOnClick(notification)"
      />
      <template v-else-if="displayWorkoutNotification()">
        <WorkoutForUser
          v-if="notification.workout"
          :action="notification.report_action"
          :display-appeal="notification.type !== 'user_warning'"
          :display-object-name="notification.type.startsWith('user_warning')"
          :workout="notification.workout"
          @workoutLinkClicked="markAsReadOnClick(notification)"
        />
        <div class="deleted-object" v-else>
          {{ $t('admin.DELETED_WORKOUT') }}
        </div>
      </template>
      <div
        class="auth-user"
        v-if="
          notification.report_action?.action_type === 'user_warning_lifting' &&
          !('comment' in notification) &&
          !('workout' in notification)
        "
      >
        <UserPicture :user="authUser" />
        <div class="user-name">
          <router-link :to="`/users/${authUser.username}`">
            {{ authUser.username }}
          </router-link>
        </div>
      </div>
      <div v-if="displayAppeal()">
        <div
          class="info-box appeal-in-progress"
          v-if="notification.report_action?.appeal?.approved === null"
        >
          <span>
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t(`user.APPEAL_IN_PROGRESS`) }}
          </span>
        </div>
        <router-link
          v-else-if="
            !notification.report_action?.appeal &&
            notification.report_action?.id
          "
          class="appeal-link"
          :to="`profile/moderation/sanctions/${notification.report_action.id}`"
          @click="markAsReadOnClick(notification)"
        >
          {{ $t('user.APPEAL') }}
        </router-link>
      </div>
      <div v-if="notification.type === 'user_data_export'">
        <button @click="$router.push('/profile/edit/account')">
          {{ $t('user.EXPORT_REQUEST.DOWNLOAD_ARCHIVE') }}
        </button>
      </div>
      <div
        v-if="notification.type === 'workouts_archive_upload'"
        class="description-list archive-file-name"
      >
        <dl v-if="notification.task?.original_file_name">
          <dt>{{ $t('user.PROFILE.ARCHIVE_UPLOADS.ARCHIVE') }}:</dt>
          <dd>{{ notification.task?.original_file_name }}</dd>
        </dl>
        <button
          @click="
            $router.push(
              `/profile/archive-uploads/${notification.task?.id}?fromNotifications=true`
            )
          "
        >
          {{ $t('buttons.SEE_DETAIL') }}
        </button>
      </div>
    </template>
  </Card>
</template>
<script lang="ts" setup>
  import { formatDistance } from 'date-fns'
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import CommentForUser from '@/components/Comment/CommentForUser.vue'
  import RelationshipDetail from '@/components/Notifications/RelationshipDetail.vue'
  import ReportNotification from '@/components/Notifications/ReportNotification.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutForUser from '@/components/Workout/WorkoutForUser.vue'
  import useApp from '@/composables/useApp'
  import type { INotification, TNotificationType } from '@/types/notifications'
  import type { IAuthUserProfile } from '@/types/user'

  interface Props {
    authUser: IAuthUserProfile
    notification: INotification
  }
  const props = defineProps<Props>()
  const { authUser, notification } = toRefs(props)

  const emit = defineEmits(['reload', 'updateReadStatus'])

  const { locale } = useApp()

  const icon: ComputedRef<string> = computed(() =>
    getIcon(notification.value.type)
  )

  function emitReload() {
    emit('reload')
  }
  function updateReadStatus(notificationId: number, markedAsRead: boolean) {
    emit('updateReadStatus', { notificationId, markedAsRead })
  }
  function markAsReadOnClick(notification: INotification) {
    if (!notification.marked_as_read) {
      updateReadStatus(notification.id, true)
    }
  }
  function displayCommentNotification(): boolean {
    return (
      [
        'comment_like',
        'comment_suspension',
        'comment_unsuspension',
        'mention',
        'user_warning',
        'user_warning_lifting',
        'workout_comment',
      ].includes(notification.value.type) && 'comment' in notification.value
    )
  }
  function displayWorkoutNotification(): boolean {
    return (
      [
        'workout_like',
        'workout_suspension',
        'workout_unsuspension',
        'user_warning',
        'user_warning_lifting',
        'workout_comment',
      ].includes(notification.value.type) && 'workout' in notification.value
    )
  }
  function displayRelationshipCard(notificationType: TNotificationType) {
    return [
      'account_creation',
      'follow',
      'follow_request',
      'follow_request_approved',
    ].includes(notificationType)
  }
  function displayAppeal() {
    if (
      !notification.value.report_action ||
      notification.value.report_action.action_type !== 'user_warning'
    ) {
      return false
    }
    return !(
      ('workout' in notification.value &&
        notification.value.workout === null) ||
      ('comment' in notification.value && notification.value.comment === null)
    )
  }
  function getUserAction(notificationType: TNotificationType): string {
    switch (notificationType) {
      case 'account_creation':
        return 'notifications.SIGN_UP'
      case 'comment_like':
        return 'notifications.LIKED_YOUR_COMMENT'
      case 'comment_suspension':
        return 'notifications.YOUR_COMMENT_HAS_BEEN_SUSPENDED'
      case 'comment_unsuspension':
        return 'notifications.YOUR_COMMENT_HAS_BEEN_UNSUSPENDED'
      case 'follow':
        return 'user.RELATIONSHIPS.FOLLOWS_YOU'
      case 'follow_request':
        return 'notifications.SEND_FOLLOW_REQUEST_TO_YOU'
      case 'follow_request_approved':
        return 'notifications.ACCEPTED_FOLLOW_REQUEST'
      case 'mention':
        return 'notifications.MENTIONED_YOU'
      case 'suspension_appeal':
        return 'notifications.APPEALED_SUSPENSION'
      case 'user_data_export':
        return 'notifications.YOUR_DATA_EXPORT_IS_READY'
      case 'user_warning':
        return 'notifications.YOU_RECEIVED_A_WARNING'
      case 'user_warning_appeal':
        return 'notifications.APPEALED_USER_WARNING'
      case 'user_warning_lifting':
        return 'notifications.YOUR_WARNING_HAS_BEEN_LIFTED'
      case 'workouts_archive_upload':
        return 'notifications.YOUR_ARCHIVE_HAS_BEEN_PROCESSED'
      case 'workout_comment':
        return 'notifications.COMMENTED_YOUR_WORKOUT'
      case 'workout_like':
        return 'notifications.LIKED_YOUR_WORKOUT'
      case 'workout_suspension':
        return 'notifications.YOUR_WORKOUT_HAS_BEEN_SUSPENDED'
      case 'workout_unsuspension':
        return 'notifications.YOUR_WORKOUT_HAS_BEEN_UNSUSPENDED'
      case 'report':
        return `notifications.REPORTED_USER_${
          notification.value.report?.object_type
            ? notification.value.report.object_type.toUpperCase()
            : ''
        }`
      default:
        return ''
    }
  }
  function getIcon(notificationType: TNotificationType): string {
    switch (notificationType) {
      case 'account_creation':
        return 'user'
      case 'follow':
      case 'follow_request':
      case 'follow_request_approved':
        return 'user-plus'
      case 'mention':
        return 'at'
      case 'comment_suspension':
      case 'comment_unsuspension':
      case 'report':
      case 'suspension_appeal':
      case 'user_warning':
      case 'user_warning_appeal':
      case 'user_warning_lifting':
      case 'workout_suspension':
      case 'workout_unsuspension':
        return 'flag'
      case 'comment_like':
      case 'workout_like':
        return 'heart'
      case 'workout_comment':
        return 'comment'
      default:
        return 'bell'
    }
  }
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .notification-card {
    ::v-deep(.card-title) {
      display: flex;
      flex-direction: row;
      justify-content: space-between;
      flex-wrap: wrap;
      align-items: center;

      .notification-icon {
        padding-right: 5px;
      }

      .mark-action {
        font-weight: initial;
        font-style: italic;
        border: none;
        box-shadow: none;
      }

      .notification-data-button {
        display: flex;
        gap: $default-padding * 0.5;
        align-items: center;

        .notification-date {
          font-size: 0.85em;
          font-style: italic;
          font-weight: normal;
          white-space: nowrap;
        }
      }
    }

    ::v-deep(.box) {
      margin: $default-margin 0;
    }

    .auth-user {
      display: flex;
      align-items: center;
      .user-picture {
        min-width: initial;
        padding: 0 $default-padding;
        img {
          height: 60px;
          width: 60px;
        }
        .no-picture {
          font-size: 3.8em;
        }
      }
    }

    .notification-reason {
      font-weight: bold;
      text-transform: capitalize;
    }

    .comment-box {
      padding: $default-padding * 0.5 $default-padding;
    }

    .info-box.suspended {
      padding: 30px;
    }

    .appeal-link {
      margin-left: $default-margin;
    }

    ::v-deep(.suspended.info-box) {
      font-size: 0.9em;
    }
    ::v-deep(.workout-card) {
      .suspended.info-box {
        margin-bottom: $default-margin;
      }
    }

    &.read {
      color: var(--app-color-lighter);
      ::v-deep(.user-picture) {
        img {
          opacity: 0.5;
        }
        .no-picture {
          color: var(--app-color-lighter);
        }
      }
      ::v-deep(.workout-comment) {
        .fa-heart {
          color: var(--app-color-lighter);
        }
      }
      ::v-deep(a:not(.appeal-link)) {
        color: var(--app-color-lighter);
      }

      ::v-deep(.sport-img) {
        opacity: 0.5;
      }

      ::v-deep(.suspended.info-box),
      ::v-deep(.appeal-rejected) {
        opacity: 0.5;
      }

      .mark-action {
        color: var(--app-color-lighter);
        &:hover {
          background: var(--app-color-lighter);
          color: var(--button-confirm-bg-color);
        }
      }
    }

    .appeal-in-progress {
      margin-top: $default-margin * 0.5;
    }

    .archive-file-name dl {
      margin: 0 0 $default-padding * 0.5;
    }
  }
</style>
