<template>
  <div class="workout-comments">
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
            </div>
            <span class="comment-text" v-html="linkifyAndClean(comment.text)"/>
          </div>
        </div>
        <WorkoutAddComment :workout="workoutData.workout" />
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { Locale, formatDistance } from 'date-fns'
  import { ComputedRef, computed,  toRefs, withDefaults } from 'vue'

  import Username from '@/components/User/Username.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import WorkoutAddComment from "@/components/Workout/WorkoutDetail/WorkoutAddComment.vue"
  import { ROOT_STORE } from "@/store/constants"
  import { IDisplayOptions } from "@/types/application"
  import { IAuthUserProfile } from "@/types/user"
  import { IWorkoutData } from "@/types/workouts"
  import { useStore } from "@/use/useStore"
  import { formatDate } from "@/utils/dates"
  import { linkifyAndClean } from '@/utils/inputs'

  interface Props {
    workoutData: IWorkoutData
    user?: IAuthUserProfile | null
  }

  const props = withDefaults(defineProps<Props>(), {
    user: null,
  })
  const { workoutData } = toRefs(props)

  const store = useStore()
  const locale: ComputedRef<Locale> = computed(
    () => store.getters[ROOT_STORE.GETTERS.LOCALE]
  )
  const displayOptions: ComputedRef<IDisplayOptions> = computed(
    () => store.getters[ROOT_STORE.GETTERS.DISPLAY_OPTIONS]
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .workout-comments {
    margin-top: $default-margin*2;
    .workout-comment {
      display: flex;
      padding-bottom: $default-padding*2;

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
        }
        .comment-text {
          border-radius: 5px;
          margin: $default-margin 0;
          padding-left: $default-padding ;
        }
      }
    }
  }
</style>