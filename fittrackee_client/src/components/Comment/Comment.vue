<template>
  <div class="workout-comment" :id="comment.id">
    <UserPicture :user="comment.user" />
    <div class="comment-detail">
      <div
        class="comment-info"
        :class="{ highlight: comment.id === paramsCommentId }"
      >
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
        <i
          class="fa fa-edit"
          v-if="isCommentOwner(authUser, comment.user) && !forNotification"
          aria-hidden="true"
          @click="() => displayCommentEdition(comment)"
        />
        <i
          class="fa fa-trash"
          v-if="isCommentOwner(authUser, comment.user) && !forNotification"
          aria-hidden="true"
          @click="deleteComment(comment)"
        />
        <span
          class="likes"
          :class="{ disabled: forNotification }"
          @click="forNotification ? null : updateLike(comment)"
        >
          <i class="fa" :class="`fa-heart${comment.liked ? '' : '-o'}`" />
          <span class="likes-count" v-if="comment.likes_count > 0">
            {{ comment.likes_count }}
          </span>
        </span>
        <i
          class="fa fa-comment-o"
          v-if="
            authUser.username &&
            comment.workout_id &&
            (!addReply || addReply !== comment) &&
            !forNotification
          "
          @click="() => displayReplyTextArea(comment)"
        />
      </div>
      <span
        v-if="commentToEdit !== comment"
        class="comment-text"
        :class="{ highlight: comment.id === paramsCommentId }"
        v-html="linkifyAndClean(comment.text_html)"
      />
      <WorkoutCommentEdition
        v-else
        :workout="workout"
        :comment="comment"
        :comments_loading="comments_loading"
        @closeEdition="() => (commentToEdit = null)"
      />
      <template v-if="!forNotification">
        <Comment
          v-for="reply in comment.replies"
          :key="reply.id"
          :comment="reply"
          :workout="workout"
          :authUser="authUser"
          :comments_loading="comments_loading"
          @deleteComment="deleteComment(reply)"
        />
        <WorkoutCommentEdition
          v-if="addReply === comment"
          class="add-comment-reply"
          :workout="workout"
          :reply-to="comment.id"
          :comments_loading="comments_loading"
          @closeEdition="() => (addReply = null)"
        />
      </template>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { ComputedRef, Ref, computed, ref, toRefs, withDefaults } from 'vue'
  import { useRoute } from 'vue-router'

  import WorkoutCommentEdition from '@/components/Comment/CommentEdition.vue'
  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { ROOT_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IDisplayOptions } from '@/types/application'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { IComment, IWorkout } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'
  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    comment: IComment
    workout?: IWorkout
    authUser: IAuthUserProfile
    comments_loading: string | null
    forNotification?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    forNotification: false,
    workout: null,
  })
  const { authUser, comment, workout } = toRefs(props)

  const emit = defineEmits(['deleteComment'])

  const store = useStore()
  const route = useRoute()

  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const commentToEdit: Ref<IComment | null> = ref(null)
  const addReply: Ref<IComment | null> = ref(null)
  const paramsCommentId: ComputedRef<string | null> = computed(
    () => route.params.commentId
  )

  function isCommentOwner(
    authUser: IAuthUserProfile | null,
    commentUser: IUserProfile
  ) {
    return authUser && authUser.username === commentUser.username
  }
  function deleteComment(comment: IComment) {
    emit('deleteComment', comment)
  }
  function focusOnTextArea(commentId: string) {
    setTimeout(() => {
      const textarea = document.getElementById(`text-${commentId}`)
      if (textarea) {
        textarea.focus()
      }
    }, 100)
  }
  function displayCommentEdition(comment: IComment) {
    commentToEdit.value = comment
    addReply.value = null
    focusOnTextArea(comment.id)
  }
  function displayReplyTextArea(comment: IComment) {
    commentToEdit.value = null
    addReply.value = comment
    focusOnTextArea(comment.id)
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
      .comment-info {
        display: flex;
        gap: $default-padding;
        flex-wrap: wrap;
        align-items: flex-end;
        padding-right: $default-padding * 0.5;
        &.highlight {
          border-top-left-radius: 5px;
          border-top-right-radius: 5px;
          background-color: var(--comment-background-highlight);
        }
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
        .fa-trash,
        .fa-comment-o,
        .fa-heart,
        .fa-heart-o {
          padding-bottom: 3px;
        }
        .fa-heart,
        .fa-heart-o {
          font-size: 0.9em;
        }
        .fa-heart {
          color: #ee2222;
        }
        .fa-edit {
          padding-bottom: 2px;
        }
        ::v-deep(.fa-users) {
          font-size: 0.8em;
        }
      }
      .comment-text {
        padding: $default-margin;
        &.highlight {
          border-bottom-left-radius: 5px;
          border-bottom-right-radius: 5px;
          background-color: var(--comment-background-highlight);
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
      .likes:hover {
        cursor: pointer;
        &.disabled {
          cursor: default;
        }
      }
    }
  }
</style>
