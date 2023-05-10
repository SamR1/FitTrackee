<template>
  <div id="comments" class="view">
    <div class="container">
      <div class="comments-container">
        <div v-if="workoutData.comments.length > 0">
          <div class="box no-workout">
            {{ $t('workouts.NO_WORKOUTS', 1) }}
          </div>
          <Comments
            :workoutData="workoutData"
            :auth-user="authUser"
            :with-parent="true"
          />
          <div id="bottom" />
        </div>
        <div v-else>
          <NotFound v-if="!workoutData.comments_loading" target="COMMENT" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { ComputedRef, computed, watch, onBeforeMount, onUnmounted } from 'vue'
  import { useRoute } from 'vue-router'

  import Comments from '@/components/Comment/Comments.vue'
  import NotFound from '@/components/Common/NotFound.vue'
  import { AUTH_USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import { IAuthUserProfile } from '@/types/user'
  import { IWorkoutData } from '@/types/workouts'
  import { useStore } from '@/use/useStore'

  const route = useRoute()
  const store = useStore()

  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const workoutData: ComputedRef<IWorkoutData> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.WORKOUT_DATA]
  )

  onBeforeMount(() => {
    store.dispatch(
      WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT,
      route.params.commentId
    )
  })

  onUnmounted(() => {
    store.commit(WORKOUTS_STORE.MUTATIONS.EMPTY_WORKOUT)
  })

  watch(
    () => route.params.commentId,
    async (newCommentId) => {
      if (newCommentId) {
        store.dispatch(WORKOUTS_STORE.ACTIONS.GET_WORKOUT_COMMENT, {
          commentId: newCommentId,
        })
      }
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
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
