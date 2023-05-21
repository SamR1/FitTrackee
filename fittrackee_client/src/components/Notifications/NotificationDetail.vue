<template>
  <Card
    class="notification-card"
    :class="{ read: notification.marked_as_read }"
    v-if="notification.id"
  >
    <template #title>
      <div>
        <i
          :class="`fa-${notification.type === 'mention' ? 'at' : 'comment'}`"
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
        v-if="displayCommentCard(notification.type)"
        :comment="notification.comment"
        :authUser="authUser"
        comments-loading="null"
        :for-notification="true"
      />
      <RelationshipDetail
        v-else-if="displayRelationshipCard"
        :notification="notification"
        :authUser="authUser"
        @updatedUserRelationship="emitReload"
      />
      <WorkoutCard
        v-else
        :workout="notification.workout"
        :sport="sport"
        :user="notification.workout.user"
        :useImperialUnits="authUser.imperial_units"
        :dateFormat="dateFormat"
        :timezone="authUser.timezone"
      />
    </template>
  </Card>
</template>
<script lang="ts" setup>
  import { ComputedRef, computed, toRefs } from 'vue'

  import Comment from '@/components/Comment/Comment.vue'
  import RelationshipDetail from '@/components/Notifications/RelationshipDetail.vue'
  import WorkoutCard from '@/components/Workout/WorkoutCard.vue'
  import { ROOT_STORE, SPORTS_STORE } from '@/store/constants'
  import { INotification, TNotificationType } from '@/types/notifications'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
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
  const appLanguage: ComputedRef<string> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LANGUAGE]
  )
  const sport: ComputedRef<ISport> = computed(
    () =>
      sports.value.filter(
        (s) => s.id === notification.value.workout.sport_id
      )[0]
  )
  const dateFormat = computed(() =>
    getDateFormat(authUser.value.date_format, appLanguage.value)
  )
  const emit = defineEmits(['reload', 'updateReadStatus'])

  function emitReload() {
    emit('reload')
  }
  function updateReadStatus(notificationId, markedAsRead) {
    emit('updateReadStatus', { notificationId, markedAsRead })
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
      case 'workout_comment':
        return 'notifications.COMMENTED_YOUR_WORKOUT'
      case 'workout_like':
        return 'notifications.LIKED_YOUR_WORKOUT'
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
        .no-picture {
          color: var(--app-color-lighter);
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
