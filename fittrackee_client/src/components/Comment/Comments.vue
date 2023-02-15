<template>
  <div class="workout-comments">
    <Modal
      v-if="commentToDelete"
      :title="$t('common.CONFIRMATION')"
      :message="$t('workouts.COMMENTS.DELETION_CONFIRMATION')"
      @confirmAction="deleteComment(commentToDelete)"
      @cancelAction="() => commentToDelete = null"
    />
    <Card>
      <template #title>
        {{ $t('workouts.COMMENTS.LABEL', 0) }}
      </template>
      <template #content>
        <Comment
          v-for="comment in workoutData.comments"
          :key="comment.id"
          :comment="comment"
          :workout="workoutData.workout"
          :authUser="authUser"
          @deleteComment="(c) => commentToDelete = c"
        />
        <div class="no-comments" v-if="workoutData.comments.length === 0">
          {{ $t('workouts.COMMENTS.NO_COMMENTS')}}
        </div>
        <div class="add-comment" v-if="displayAddComment">
          <WorkoutCommentEdition
            v-if="authUser.username" :workout="workoutData.workout"
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
  import { Ref, ref, toRefs, watch } from "vue"

  import WorkoutCommentEdition from "@/components/Comment/CommentEdition.vue"
  import { WORKOUTS_STORE } from "@/store/constants"
  import { IAuthUserProfile } from "@/types/user"
  import { IComment, IWorkoutData } from "@/types/workouts"
  import { useStore } from "@/use/useStore"

  interface Props {
    workoutData: IWorkoutData
    authUser: IAuthUserProfile
  }

  const props = defineProps<Props>()
  const { workoutData } = toRefs(props)

  const store = useStore()
  const commentToDelete: Ref<IComment | null> = ref(null)
  const displayAddComment: Ref<boolean> = ref(false)

  function deleteComment(comment: IComment) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT, {
      workoutId: comment.workout_id,
      commentId: comment.id
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
  }
</style>