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
        <div
          v-for="comment in workoutData.comments"
          :key="comment.id"
          class="workout-comment"
        >
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
              <VisibilityIcon :visibility="comment.text_visibility" />
              <i
                class="fa fa-trash"
                v-if="isCommentOwner(authUser, comment.user)"
                aria-hidden="true"
                @click="() => commentToDelete = comment"
              />
            </div>
            <span class="comment-text" v-html="linkifyAndClean(comment.text)"/>
          </div>
        </div>
        <div class="no-comments" v-if="workoutData.comments.length === 0">
          {{ $t('workouts.COMMENTS.NO_COMMENTS')}}
        </div>
        <WorkoutAddComment :workout="workoutData.workout" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { ComputedRef, Ref, computed, ref, toRefs, watch } from 'vue'

  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutAddComment from "@/components/Workout/WorkoutDetail/WorkoutAddComment.vue"
  import { ROOT_STORE, WORKOUTS_STORE } from "@/store/constants"
  import { IDisplayOptions } from "@/types/application"
  import { IAuthUserProfile, IUserProfile } from "@/types/user"
  import { IComment, IWorkoutData } from "@/types/workouts"
  import { useStore } from "@/use/useStore"
  import { formatDate } from "@/utils/dates"
  import { linkifyAndClean } from '@/utils/inputs'
  import { getUserName } from "@/utils/user"

  interface Props {
    workoutData: IWorkoutData
    authUser?: IAuthUserProfile | null
  }

  const props = withDefaults(defineProps<Props>(), {
    authUser: null,
  })
  const { workoutData } = toRefs(props)

  const store = useStore()
  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
  const commentToDelete: Ref<IComment | null> = ref(null)

  function isCommentOwner(authUser: IAuthUserProfile | null, commentUser: IUserProfile) {
    return authUser && getUserName(authUser) === getUserName(commentUser)
  }

  function deleteComment(comment: IComment) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.DELETE_WORKOUT_COMMENT, {
      workoutId: comment.workout_id,
      commentId: comment.id
    })
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
          .comment-date, .user-remote-fullname {
            font-size: 0.85em;
            font-style: italic;
            white-space: nowrap;
          }
          .fa-trash {
            padding-bottom: 3px;
          }

          ::v-deep(.fa-users) {
            font-size: .8em;
          }
        }
        .comment-text {
          border-radius: 5px;
          margin: $default-margin 0;
          padding-left: $default-padding ;
        }
      }
    }

    .no-comments {
      font-style: italic;
    }
  }
</style>