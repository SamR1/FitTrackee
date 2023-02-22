<template>
  <div class="workout-comment">
    <UserPicture :user="comment.user" />
    <div class="comment-detail">
      <div class="comment-info">
        <Username :user="comment.user"/>
        <div v-if="comment.user.is_remote" class="user-remote-fullname">
          {{ comment.user.fullname }}
        </div>
        <div class="spacer"/>
        <div
          class="comment-date"
          :title="formatDate(
            comment.created_at,
            displayOptions.timezone,
            displayOptions.dateFormat
          )"
        >
          {{
            formatDistance(new Date(comment.created_at), new Date(), {
              addSuffix: true,
              locale,
            })
          }}
        </div>
        <div
          class="comment-edited"
          v-if="comment.modification_date"
          :title="formatDate(
            comment.modification_date,
            displayOptions.timezone,
            displayOptions.dateFormat
          )"
        >
          ({{ $t('common.EDITED') }})
        </div>
        <VisibilityIcon
          :visibility="comment.text_visibility"
          :is-comment="true"
        />
        <i
          class="fa fa-edit"
          v-if="isCommentOwner(authUser, comment.user)"
          aria-hidden="true"
          @click="() => displayCommentEdition(comment)"
        />
        <i
          class="fa fa-trash"
          v-if="isCommentOwner(authUser, comment.user)"
          aria-hidden="true"
          @click="deleteComment(comment)"
        />
        <span class="likes" @click="updateLike(comment)">
          <i class="fa" :class="`fa-heart${comment.liked ? '' : '-o'}`"/>
          <span class="likes-count" v-if="comment.likes_count > 0">{{ comment.likes_count }}</span>
        </span>
        <i
          class="fa fa-comment-o"
          v-if="authUser.username && (!addReply || addReply !== comment)"
          @click="() => displayReplyTextArea(comment)"
        />
      </div>
      <span
        v-if="commentToEdit !== comment"
        class="comment-text"
        v-html="linkifyAndClean(comment.text_html)"
      />
      <WorkoutCommentEdition
        v-else
        :workout="workout"
        :comment="comment"
        :comments_loading="comments_loading"
        @closeEdition="() => commentToEdit = null"
      />
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
        @closeEdition="() => addReply = null"
      />
    </div>

  </div>
</template>

<script setup lang="ts">
  import { Locale, formatDistance } from "date-fns"
  import { ComputedRef, Ref, computed, ref, toRefs } from "vue"

  import WorkoutCommentEdition from "@/components/Comment/CommentEdition.vue"
  import Username from "@/components/User/Username.vue"
  import UserPicture from "@/components/User/UserPicture.vue"
  import { ROOT_STORE, WORKOUTS_STORE } from "@/store/constants"
  import { IDisplayOptions } from "@/types/application"
  import { IAuthUserProfile, IUserProfile } from "@/types/user"
  import { IComment, IWorkout } from "@/types/workouts"
  import { useStore } from "@/use/useStore"
  import { formatDate } from "@/utils/dates"
  import { linkifyAndClean } from "@/utils/inputs"
  import { getUserName } from "@/utils/user"

  interface Props {
    comment: IComment
    workout: IWorkout
    authUser: IAuthUserProfile
    comments_loading: string | null
  }

  const props = defineProps<Props>()
  const { authUser, comment, workout } = toRefs(props)

  const emit = defineEmits(['deleteComment'])

  const store = useStore()
  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const commentToEdit: Ref<IComment | null> = ref(null)
  const addReply: Ref<IComment | null> = ref(null)

  function isCommentOwner(authUser: IAuthUserProfile | null, commentUser: IUserProfile) {
    return authUser && getUserName(authUser) === getUserName(commentUser)
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
    ::v-deep(.user-picture) {
      min-width: min-content;
      align-items: flex-start;
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
        .user-name {
          font-weight: bold;
          padding-left: $default-padding;
        }
        .spacer {
          flex-grow: 3;
        }
        .comment-date, .user-remote-fullname, .comment-edited {
          font-size: 0.85em;
          font-style: italic;
          white-space: nowrap;
        }
        .fa-trash, .fa-comment-o, .fa-heart , .fa-heart-o {
          padding-bottom: 3px;
        }
        .fa-heart , .fa-heart-o {
          font-size: .9em;
        }
        .fa-heart {
          color: #ee2222;
        }
        .fa-edit{
          padding-bottom: 2px;
        }
        ::v-deep(.fa-users) {
          font-size: .8em;
        }
      }
      .comment-text {
        border-radius: 5px;
        margin: $default-margin 0;
        padding-left: $default-padding;
      }
      .add-comment-reply {
        margin: 0 0 40px;
      }
      .likes {
        .likes-count {
          padding-left: $default-padding *.3;
          font-size: 0.8em;
        }
      }
      .likes:hover {
        cursor: pointer;
      }
    }
  }
</style>