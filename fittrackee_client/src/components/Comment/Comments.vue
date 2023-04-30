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
        {{ $t('workouts.COMMENTS.LABEL', 0) }}
      </template>
      <template v-if="isLoading" #content>
        <Loader />
      </template>
      <template v-else #content>
        <Comment
          v-for="comment in workoutData.comments"
          :key="comment.id"
          :comment="comment"
          :workout="workoutData.workout"
          :authUser="authUser"
          :comments_loading="workoutData.comments_loading"
          @deleteComment="(c) => (commentToDelete = c)"
        />
        <div class="no-comments" v-if="workoutData.comments.length === 0">
          {{ $t('workouts.COMMENTS.NO_COMMENTS') }}
        </div>
        <div class="add-comment" v-if="displayAddComment">
          <WorkoutCommentEdition
            v-if="authUser.username"
            :workout="workoutData.workout"
            :comments_loading="workoutData.comments_loading"
            @closeEdition="displayAddComment = false"
          />
        </div>
        <div class="add-comment-button" v-else>
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
    computed,
    onMounted,
    ref,
    toRefs,
    watch,
  } from 'vue'

  import WorkoutCommentEdition from '@/components/Comment/CommentEdition.vue'
  import { WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IComment, IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  interface Props {
    workoutData: IWorkoutData
    authUser: IAuthUserProfile
  }

  const props = defineProps<Props>()
  const { workoutData } = toRefs(props)

  const store = useStore()
  const commentToDelete: Ref<IComment | null> = ref(null)
  const displayAddComment: Ref<boolean> = ref(false)
  const isLoading: ComputedRef<boolean> = computed(
    () => workoutData.value.comments_loading === 'all'
  )
  const isDeleting: ComputedRef<boolean> = computed(
    () => workoutData.value.comments_loading === 'delete'
  )

  onMounted(() =>
    store.commit(WORKOUTS_STORE.MUTATIONS.SET_COMMENT_LOADING, 'all')
  )

  function deleteComment(comment: IComment) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT, {
      workoutId: comment.workout_id,
      commentId: comment.id,
    })
  }
  function displayCommentTextArea() {
    displayAddComment.value = true
    setTimeout(() => {
      const textarea = document.getElementById('text')
      if (textarea) {
        textarea.focus()
      }
    }, 100)
  }

  watch(
    () => workoutData.value.comments,
    () => {
      commentToDelete.value = null
    }
  )
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
