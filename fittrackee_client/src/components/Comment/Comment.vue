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
      <span
        v-if="!isCommentEdited()"
        class="comment-text"
        :class="{ highlight: highlighted }"
        v-html="linkifyAndClean(comment.text_html)"
      />
      <WorkoutCommentEdition
        v-else
        :workout="workout"
        :comment="comment"
        :comments-loading="commentsLoading"
        :name="`text-${comment.id}`"
        :authUser="authUser"
      />
      <div class="comment-actions">
        <button
          class="transparent icon-button likes"
          @click="forNotification ? null : updateLike(comment)"
          :disabled="forNotification"
          :title="`${$t('workouts.COMMENTS.LIKE')} (${comment.likes_count} ${$t(
            'workouts.COMMENTS.LIKES',
            comment.likes_count
          )})`"
        >
          <i
            class="fa"
            :class="{
              'fa-heart': comment.liked,
              'fa-heart-o': !comment.liked,
            }"
            aria-hidden="true"
          />
          <span
            class="likes-count"
            v-if="comment.likes_count > 0"
            aria-hidden="true"
          >
            {{ comment.likes_count }}
          </span>
        </button>
        <button
          v-if="displayCommentIcon()"
          class="transparent icon-button"
          @click="() => displayCommentEdition('add')"
          :title="$t('workouts.COMMENTS.ADD')"
        >
          <i class="fa fa-comment-o" aria-hidden="true" />
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
      <template v-if="!forNotification">
        <WorkoutCommentEdition
          v-if="isNewReply()"
          class="add-comment-reply"
          :workout="workout"
          :reply-to="comment.id"
          :comments-loading="commentsLoading"
          :name="`text-${comment.id}`"
          :authUser="authUser"
          :mentions="comment.mentions"
        />
        <Comment
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :workout="workout"
          :authUser="authUser"
          :comments-loading="commentsLoading"
          :current-comment-edition="currentCommentEdition"
          @deleteComment="deleteComment(reply)"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { ComputedRef, computed, toRefs, withDefaults } from 'vue'
  import { useRoute } from 'vue-router'

  import WorkoutCommentEdition from '@/components/Comment/CommentEdition.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IDisplayOptions } from '@/types/application'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { IComment, ICurrentCommentEdition, IWorkout } from '@/types/workouts'
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
  }

  const props = withDefaults(defineProps<Props>(), {
    currentCommentEdition: null,
    forNotification: false,
    workout: null,
  })
  const { authUser, comment, currentCommentEdition, forNotification, workout } =
    toRefs(props)

  const store = useStore()
  const route = useRoute()

  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const paramsCommentId: ComputedRef<string | string[] | null> = computed(
    () => route.params.commentId
  )
  const highlighted: ComputedRef<boolean> = computed(
    () =>
      comment.value.id === paramsCommentId.value ||
      (currentCommentEdition.value?.type === 'delete' &&
        currentCommentEdition.value?.comment?.id === comment.value.id)
  )

  function isCommentOwner(
    authUser: IAuthUserProfile | null,
    commentUser: IUserProfile
  ) {
    return authUser && authUser.username === commentUser.username
  }
  function isCommentEdited() {
    return (
      currentCommentEdition.value?.type === 'edit' &&
      currentCommentEdition.value?.comment?.id === comment.value.id
    )
  }
  function isNewReply() {
    return (
      currentCommentEdition.value?.type === 'add' &&
      currentCommentEdition.value?.comment?.id === comment.value.id
    )
  }
  function displayCommentIcon() {
    return (
      authUser.value.username &&
      comment.value.workout_id &&
      !forNotification.value
    )
  }
  function deleteComment(commentToDelete: IComment) {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {
      type: 'delete',
      comment: commentToDelete,
    })
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

      .comment-actions {
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
        .fa-heart {
          color: #ee2222;
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
      .add-comment-reply {
        margin: 0 0 40px;
      }
      .likes {
        .likes-count {
          padding-left: $default-padding * 0.3;
          font-size: 0.8em;
        }
      }
    }
  }
</style>
