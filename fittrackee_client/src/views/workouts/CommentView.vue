<template>
  <div id="comments" class="view">
    <div class="container">
      <div class="comments-container">
        <div v-if="workoutData.comments.length > 0">
          <div class="box no-workout">
            {{ $t('workouts.NO_WORKOUT_AVAILABLE') }}
          </div>
          <Comments
            :workoutData="workoutData"
            :auth-user="authUser"
            :with-parent="true"
          />
          <div id="bottom" />
        </div>
        <div v-else>
          <NotFound v-if="!workoutData.commentsLoading" target="COMMENT" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, watch, onBeforeMount, onUnmounted } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'

  import Comments from '@/components/Comment/Comments.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import useAuthUser from '@/composables/useAuthUser'
  import { WORKOUTS_STORE } from '@/store/constants'
  import type { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const { authUser } = useAuthUser()

  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )

  watch(
    () => route.params.commentId,
    async (newCommentId) => {
      if (newCommentId) {
        store.dispatch(
          WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT,
          newCommentId as string
        )
      }
    }
  )

  onBeforeMount(() => {
    store.dispatch(
      WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT,
      route.params.commentId as string
    )
  })
  onUnmounted(() => {
    store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #comments {
    display: flex;
    .container {
      width: 100%;
      padding: 0;
      .comments-container {
        width: 100%;
      }
    }
  }
</style>
