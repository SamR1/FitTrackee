<template>
  <div class="workout-comments">
    <Modal
      v-if="commentToDelete"
      :title="$t('common.CONFIRMATION')"
      :message="$t('workouts.COMMENTS.DELETION_CONFIRMATION')"
      :loading="isDeleting"
      @confirmAction="deleteComment(commentToDelete)"
      @cancelAction="() => (commentToDelete = null)"
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
          :authUser="authUser"
          comments-loading="workoutData.commentsLoading"
          @deleteComment="(c) => (commentToDelete = c)"
        />
        <div class="no-comments" v-if="workoutData.comments.length === 0">
          {{ $t('workouts.COMMENTS.NO_COMMENTS') }}
        </div>
        <div class="add-comment" v-if="displayAddComment">
          <WorkoutCommentEdition
            v-if="authUser.username"
            :workout="workoutData.workout"
            comments-loading="workoutData.commentsLoading"
            @closeEdition="displayAddComment = false"
          />
        </div>
        <div class="add-comment-button" v-else-if="workoutData.workout.id">
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
    ComputedRef,
    Ref,
    capitalize,
    computed,
    nextTick,
    onMounted,
    onUnmounted,
    ref,
    toRefs,
    watch,
    withDefaults,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import WorkoutCommentEdition from '@/components/Comment/CommentEdition.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IComment, IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    workoutData: IWorkoutData
    authUser: IAuthUserProfile
    withParent?: boolean
  }

  const props = withDefaults(defineProps<Props>(), {
    withParent: false,
  })
  const { workoutData, withParent } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const comments: ComputedRef<IComment[]> = computed(() => getComments())
  const commentToDelete: Ref<IComment | null> = ref(null)
  const displayAddComment: Ref<boolean> = ref(false)
  const isLoading: ComputedRef<boolean> = computed(
    () => workoutData.value.commentsLoading === 'all'
  )
  const isDeleting: ComputedRef<boolean> = computed(
    () => workoutData.value.commentsLoading === 'delete'
  )
  const commentId: ComputedRef<string | null> = computed(
    () => route.params.commentId
  )
  const timer = ref<number | undefined>()

  onMounted(() => {
    nextTick(() => {
      if (commentId.value) {
        scrollToComment(commentId.value)
      }
    })
  })

  function getComments(): IComment[] {
    if (!withParent.value || !workoutData.value.comments[0].reply_to) {
      return workoutData.value.comments
    }
    const replyToComment = Object.assign(
      {},
      workoutData.value.comments[0].reply_to
    )
    replyToComment.replies = workoutData.value.comments
    return [replyToComment]
  }

  function deleteComment(comment: IComment) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT, {
      workoutId: comment.workout_id,
      commentId: comment.id,
    })
  }
  function displayCommentTextArea() {
    displayAddComment.value = true
    timer.value = setTimeout(() => {
      const textarea = document.getElementById('text')
      if (textarea) {
        textarea.focus()
      }
    }, 100)
  }
  function scrollToComment(commentId) {
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
      commentToDelete.value = null
    }
  )

  onUnmounted(() => {
    if (timer.value) {
      clearTimeout(timer.value)
    }
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

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
  }
</style>
