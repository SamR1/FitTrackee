<template>
  <div class="workout-comments">
    <Modal
      v-if="commentToDelete"
      :title="$t('common.CONFIRMATION')"
      :message="$t('workouts.COMMENTS.DELETION_CONFIRMATION')"
      :loading="isDeleting"
      @confirmAction="deleteComment"
      @cancelAction="cancelDelete"
    />
    <Card>
      <template #title>
        {{ capitalize($t('workouts.COMMENTS.LABEL', 0)) }}
      </template>
      <template v-if="isLoading" #content>
        <Loader />
      </template>
      <template v-else #content>
        <Comment
          v-for="comment in comments"
          :key="comment.id"
          :comment="comment"
          :workout="workoutData.workout"
          :current-comment-edition="workoutData.currentCommentEdition"
          :authUser="authUser"
          comments-loading="workoutData.commentsLoading"
          :action="comment.suspension"
        />
        <div class="no-comments" v-if="workoutData.comments.length === 0">
          {{ $t('workouts.COMMENTS.NO_COMMENTS') }}
        </div>
        <div class="add-comment" v-if="displayAddComment">
          <CommentEdition
            v-if="authUser.username"
            :workout="workoutData.workout"
            comments-loading="workoutData.commentsLoading"
            :auth-user="authUser"
          />
        </div>
        <div
          class="add-comment-button"
          v-else-if="authUser.username && workoutData.workout.id"
        >
          <button @click.prevent="displayCommentTextArea">
            {{ $t('workouts.COMMENTS.ADD') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import {
    capitalize,
    computed,
    nextTick,
    onMounted,
    onUnmounted,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import CommentEdition from '@/components/Comment/CommentEdition.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import type { IAuthUserProfile } from '@/types/user'
  import type { IComment, IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    workoutData: IWorkoutData
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { workoutData } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const timer: Ref<number | undefined> = ref()

  const comments: ComputedRef<IComment[]> = computed(
    () => workoutData.value.comments
  )
  const commentToDelete: ComputedRef<boolean> = computed(
    () => workoutData.value.currentCommentEdition.type === 'delete'
  )
  const displayAddComment: ComputedRef<boolean> = computed(
    () => workoutData.value.currentCommentEdition.type === 'new'
  )
  const isLoading: ComputedRef<boolean> = computed(
    () => workoutData.value.commentsLoading === 'all'
  )
  const isDeleting: ComputedRef<boolean> = computed(
    () => workoutData.value.commentsLoading === 'delete'
  )
  const commentId: ComputedRef<string> = computed(
    () => route.params.commentId as string
  )

  function deleteComment() {
    const commentToDelete: IComment | undefined =
      workoutData.value.currentCommentEdition.comment
    if (commentToDelete) {
      store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT, {
        workoutId: commentToDelete.workout_id,
        commentId: commentToDelete.id,
      })
    }
  }
  function cancelDelete() {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {})
  }
  function displayCommentTextArea() {
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {
      type: 'new',
    })
    timer.value = setTimeout(() => {
      const textarea = document.getElementById('text')
      if (textarea) {
        textarea.focus()
        textarea.scrollIntoView({ behavior: 'smooth' })
      }
    }, 100)
  }
  function scrollToComment(commentId: string) {
    timer.value = setTimeout(() => {
      const comment = document.getElementById(commentId)
      if (comment) {
        comment.scrollIntoView({ behavior: 'smooth' })
      }
    }, 500)
  }

  watch(
    () => workoutData.value.comments,
    () => {
      store.commit(WORKOUTS_STORE.MUTATIONS.SET_CURRENT_COMMENT_EDITION, {})
    }
  )

  onMounted(() => {
    nextTick(() => {
      if (commentId.value) {
        scrollToComment(commentId.value)
      }
    })
  })
  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .workout-comments {
    padding-bottom: $default-padding * 2;
    .no-comments {
      font-style: italic;
    }
    .add-comment-button {
      margin: $default-margin 0;
    }
    .loader {
      border-width: 5px;
      height: 20px;
      margin-left: 50%;
      width: 20px;
    }

    .card-content {
      div:not(:nth-last-child(-n + 2)) {
        border-bottom: 1px solid var(--comment-border-color);
      }
    }
  }
</style>
