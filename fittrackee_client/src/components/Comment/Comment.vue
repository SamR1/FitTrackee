<template>
  <div class="workout-comment" :id="comment.id">
    <UserPicture :user="comment.user" />
    <div class="comment-detail">
      <div class="comment-info">
        <Username :user="comment.user" />
        <div class="spacer" />
        <router-link
          class="comment-date"
          :to="`${
            comment.workout_id ? `/workouts/${comment.workout_id}` : ''
          }/comments/${comment.id}`"
          :title="
            formatDate(
              comment.created_at,
              displayOptions.timezone,
              displayOptions.dateFormat
            )
          "
          @click="$emit('commentLinkClicked')"
        >
          {{
            formatDistance(new Date(comment.created_at), new Date(), {
              addSuffix: true,
              locale,
            })
          }}
        </router-link>
        <div
          class="comment-edited"
          v-if="comment.modification_date"
          :title="
            formatDate(
              comment.modification_date,
              displayOptions.timezone,
              displayOptions.dateFormat
            )
          "
        >
          ({{ $t('common.EDITED') }})
        </div>
        <VisibilityIcon
          :visibility="comment.text_visibility"
          :is-comment="true"
        />
      </div>
      <template v-if="comment.text_html">
        <span
          v-if="!isCommentEdited()"
          class="comment-text"
          :class="{ highlight: highlighted }"
          v-html="linkifyAndClean(comment.text_html)"
        />
        <CommentEdition
          v-else
          :workout="workout"
          :comment="comment"
          :comments-loading="commentsLoading"
          :name="`text-${comment.id}`"
          :authUser="authUser"
        />
      </template>
      <div
        class="suspended info-box"
        v-if="comment.suspended && !comment.suspension"
      >
        <i class="fa fa-info-circle" aria-hidden="true" />
        {{ $t('workouts.COMMENTS.SUSPENDED_COMMENT_BY_ADMIN') }}
      </div>
      <CommentActionAppeal
        v-if="displayMakeAppeal && action && comment.suspended"
        :hide-suspension-appeal="hideSuspensionAppeal"
        :action="action"
        :comment="comment"
      />
      <div class="comment-actions" v-if="authUser.username && !forAdmin">
        <button
          v-if="!comment.suspended && !forNotification"
          class="transparent icon-button likes"
          @click="forNotification ? null : updateLike(comment)"
          :disabled="forNotification"
          :title="`${$t(`workouts.${comment.liked ? 'REMOVE_LIKE' : 'COMMENTS.LIKE_COMMENT'}`)} (${comment.likes_count} ${$t(
            'workouts.LIKES',
            comment.likes_count
          )})`"
        >
          <i
            class="fa"
            :class="{
              'fa-heart': comment.likes_count > 0,
              'fa-heart-o': comment.likes_count === 0,
              liked: comment.liked,
            }"
            aria-hidden="true"
          />
        </button>
        <router-link
          :to="getLikesUrl()"
          v-if="comment.likes_count > 0"
          class="likes-count"
        >
          {{ comment.likes_count }}
        </router-link>
        <button
          v-if="displayReportButton"
          class="transparent icon-button"
          @click="reportComment(comment)"
          :title="$t('workouts.COMMENTS.REPORT')"
        >
          <i class="fa fa-flag" aria-hidden="true" />
        </button>
        <button
          v-if="isCommentOwner(authUser, comment.user) && !forNotification"
          class="transparent icon-button"
          @click="() => displayCommentEdition('edit')"
          :title="$t('workouts.COMMENTS.EDIT')"
        >
          <i class="fa fa-edit" aria-hidden="true" />
        </button>
        <button
          v-if="isCommentOwner(authUser, comment.user) && !forNotification"
          class="transparent icon-button"
          @click="deleteComment(comment)"
          :title="$t('workouts.COMMENTS.DELETE')"
        >
          <i class="fa fa-trash" aria-hidden="true" />
        </button>
      </div>
      <div
        v-if="!authUser.username"
        class="comment-likes"
        :title="`${comment.likes_count} ${$t(
          'workouts.LIKES',
          comment.likes_count
        )}`"
      >
        <i
          class="fa"
          :class="{
            'fa-heart': comment.likes_count > 0,
            'fa-heart-o': comment.likes_count === 0,
          }"
          aria-hidden="true"
        />
        <router-link
          :to="getLikesUrl()"
          v-if="comment.likes_count > 0"
          class="likes-count"
        >
          {{ comment.likes_count }}
        </router-link>
      </div>
      <ReportForm
        v-if="isCommentReported()"
        :object-id="comment.id"
        object-type="comment"
      />
      <div
        v-if="reportStatus === `comment-${comment.id}-created`"
        class="report-submitted"
      >
        <div class="info-box">
          <span>
            <i class="fa fa-info-circle" aria-hidden="true" />
            {{ $t('common.REPORT_SUBMITTED') }}
          </span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { formatDistance } from 'date-fns'
  import { computed, toRefs, onUnmounted, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import CommentActionAppeal from '@/components/Comment/CommentActionAppeal.vue'
  import CommentEdition from '@/components/Comment/CommentEdition.vue'
  import ReportForm from '@/components/Common/ReportForm.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import useApp from '@/composables/useApp'
  import useAppeal from '@/composables/useAppeal'
  import { REPORTS_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type {
    IAuthUserProfile,
    IUserLightProfile,
    IUserProfile,
    IUserReportAction,
  } from '@/types/user'
  import type {
    IComment,
    ICurrentCommentEdition,
    IWorkout,
  } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'
  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    comment: IComment
    workout?: IWorkout | null
    authUser: IAuthUserProfile
    commentsLoading: string | null
    currentCommentEdition?: ICurrentCommentEdition | null
    forNotification?: boolean
    forAdmin?: boolean
    displayAppeal?: boolean
    hideSuspensionAppeal?: boolean
    action?: IUserReportAction | null
  }
  const props = withDefaults(defineProps<Props>(), {
    displayAppeal: false,
    currentCommentEdition: null,
    forAdmin: false,
    forNotification: false,
    workout: null,
    hideSuspensionAppeal: false,
    action: null,
  })
  const {
    action,
    authUser,
    comment,
    currentCommentEdition,
    forAdmin,
    forNotification,
    workout,
  } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { displayAppealForm } = useAppeal()
  const { displayOptions, locale } = useApp()

  const reportStatus: ComputedRef<string | null> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORT_STATUS]
  )
  const paramsCommentId: ComputedRef<string | string[] | null> = computed(
    () => route.params.commentId
  )
  const highlighted: ComputedRef<boolean> = computed(
    () =>
      comment.value.id === paramsCommentId.value ||
      ((currentCommentEdition.value?.type === 'delete' ||
        currentCommentEdition.value?.type === 'report') &&
        currentCommentEdition.value?.comment?.id === comment.value.id)
  )
  const displayMakeAppeal: ComputedRef<boolean> = computed(
    () =>
      comment.value.user.username === authUser?.value.username &&
      action.value?.action_type === 'comment_suspension' &&
      (!action.value.appeal ||
        action.value.appeal?.approved === false ||
        (action.value.appeal?.approved === null &&
          !action.value.appeal?.updated_at)) &&
      comment.value.suspended_at !== null &&
      comment.value.suspension !== undefined &&
      displayAppealForm.value !== comment.value.id
  )
  const displayReportButton: ComputedRef<boolean> = computed(
    () =>
      !forNotification.value &&
      !comment.value.suspended &&
      !isCommentOwner(authUser.value, comment.value.user) &&
      !isCommentReported() &&
      reportStatus.value !== `comment-${comment.value.id}-created`
  )

  function isCommentOwner(
    authUser: IAuthUserProfile | null,
    commentUser: IUserProfile | IUserLightProfile
  ) {
    return authUser && authUser.username === commentUser.username
  }
  function isCommentEdited() {
    return (
      currentCommentEdition.value?.type === 'edit' &&
      currentCommentEdition.value?.comment?.id === comment.value.id
    )
  }
  function isCommentReported() {
    return (
      currentCommentEdition.value?.type === 'report' &&
      currentCommentEdition.value?.comment?.id === comment.value.id
    )
  }
  function deleteComment(commentToDelete: IComment) {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {
      type: 'delete',
      comment: commentToDelete,
    })
  }
  function reportComment(commentToReport: IComment) {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {
      type: 'report',
      comment: commentToReport,
    })
    store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
  }
  function displayCommentEdition(actionType: string) {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {
      type: actionType,
      comment: comment.value,
    })
    setTimeout(() => {
      const textarea = document.getElementById(`text-${comment.value.id}`)
      if (textarea) {
        textarea.focus()
      }
    }, 100)
  }
  function updateLike(comment: IComment) {
    store.dispatch(
      comment.liked
        ? WORKOUTS_STORE.ACTIONS.UNDO_LIKE_COMMENT
        : WORKOUTS_STORE.ACTIONS.LIKE_COMMENT,
      comment
    )
  }
  function getLikesUrl() {
    let url = `/comments/${comment.value.id}/likes`
    if (comment.value.workout_id) {
      url = `/workouts/${comment.value.workout_id}${url}`
    }
    return url
  }

  watch(
    () => route.params.workoutId,
    () => {
      store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
    }
  )

  onUnmounted(() =>
    store.commit(REPORTS_STORE.MUTATIONS.SET_REPORT_STATUS, null)
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  .workout-comment {
    display: flex;
    background-color: var(--comment-background);
    padding: 10px 0;

    ::v-deep(.user-picture) {
      min-width: min-content;
      align-items: flex-start;
      background-color: var(--comment-background);
      img {
        height: 25px;
        width: 25px;
      }
      .no-picture {
        font-size: 1.5em;
      }
    }
    .comment-detail {
      display: flex;
      flex-direction: column;
      width: 100%;

      .comment-info,
      .comment-actions {
        display: flex;
        gap: $default-padding;
        flex-wrap: wrap;
        align-items: flex-end;
      }
      .comment-likes {
        display: flex;
        gap: $default-padding * 0.5;
        line-height: 15px;
      }

      .comment-info {
        .user-name {
          font-weight: bold;
          padding-left: $default-padding;
        }
        .spacer {
          flex-grow: 3;
        }
        .comment-date,
        .comment-edited {
          font-size: 0.85em;
          font-style: italic;
          white-space: nowrap;
        }
        .comment-date:hover {
          text-decoration: underline;
        }
        ::v-deep(.fa-users) {
          font-size: 0.8em;
        }
      }

      .appeal {
        margin-left: $default-padding;
      }

      .comment-actions,
      .comment-likes {
        justify-content: flex-end;
        .icon-button {
          line-height: 15px;
        }
        .fa-edit {
          margin-bottom: -3px;
        }
        .fa-heart,
        .fa-heart-o {
          font-size: 0.9em;
        }
        .fa-heart.liked {
          color: var(--like-color);
        }
      }
      .report-submitted {
        display: flex;
        .info-box {
          padding: $default-padding $default-padding * 2;
        }
      }

      .comment-text {
        padding: $default-padding;
        white-space: pre-wrap;
        &.highlight {
          border-radius: 5px;
          background-image: var(--comment-background-highlight);
        }
      }

      ::v-deep(.suspended) {
        margin-top: $default-padding;
      }

      .likes-count {
        margin-left: $default-padding * -0.5;
        font-size: 0.8em;
      }
    }
  }
</style>
