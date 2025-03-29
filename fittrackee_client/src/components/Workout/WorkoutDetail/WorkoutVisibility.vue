<template>
  <div class="workout-visibility-levels" v-if="workoutObject.workoutVisibility">
    {{ $t('visibility_levels.VISIBILITY') }}:
    <div class="visibility">
      <span v-if="workoutObject.with_analysis" class="workout-visibility">
        {{ $t('workouts.WORKOUT') }}
      </span>
      <i
        :class="`fa fa-${getVisibilityIcon(workoutObject.workoutVisibility)}`"
        aria-hidden="true"
        :title="
          $t(`visibility_levels.LEVELS.${workoutObject.workoutVisibility}`)
        "
      />
      <span class="visibility-label">
        ({{
          $t(
            `visibility_levels.LEVELS.${getVisibilityLevelForLabel(
              workoutObject.workoutVisibility,
              appConfig.federation_enabled
            )}`
          )
        }})
      </span>
    </div>
    <div class="visibility" v-if="workoutObject.with_analysis">
      <span v-if="workoutObject.with_analysis" class="workout-visibility">
        {{ $t('workouts.ANALYSIS') }}
      </span>
      <i
        :class="`fa fa-${getVisibilityIcon(workoutObject.analysisVisibility)}`"
        aria-hidden="true"
        :title="
          $t(`visibility_levels.LEVELS.${workoutObject.analysisVisibility}`)
        "
      />
      <span class="visibility-label">
        ({{
          $t(`visibility_levels.LEVELS.${workoutObject.analysisVisibility}`)
        }})
      </span>
    </div>
    <div class="visibility" v-if="workoutObject.with_gpx">
      {{ $t('workouts.MAP') }}
      <i
        :class="`fa fa-${getVisibilityIcon(workoutObject.mapVisibility)}`"
        aria-hidden="true"
        :title="$t(`visibility_levels.LEVELS.${workoutObject.mapVisibility}`)"
      />
      <span class="visibility-label">
        ({{
          $t(
            `visibility_levels.LEVELS.${getVisibilityLevelForLabel(
              workoutObject.mapVisibility,
              appConfig.federation_enabled
            )}`
          )
        }})
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'

  import { ROOT_STORE } from '@/store/constants'
  import type { TAppConfig } from '@/types/application'
  import type { TVisibilityLevels } from '@/types/user'
  import type { IWorkoutObject } from '@/types/workouts'
  import { useStore } from '@/use/useStore'
  import { getVisibilityLevelForLabel } from '@/utils/visibility_levels'
  interface Props {
    workoutObject: IWorkoutObject
  }
  const props = defineProps<Props>()
  const { workoutObject } = toRefs(props)

  const store = useStore()

  const appConfig: ComputedRef<TAppConfig> = computed(
    () => store.getters[ROOT_STORE.GETTERS.APP_CONFIG]
  )
  function getVisibilityIcon(
    visibilityLevel: TVisibilityLevels | null | undefined
  ): string {
    switch (visibilityLevel) {
      case 'public':
        return 'globe'
      case 'followers_and_remote_only':
      case 'followers_only':
        return 'users'
      default:
      case 'private':
        return 'lock'
    }
  }
</script>
<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;

  .workout-visibility-levels {
    display: flex;
    align-items: center;
    font-size: 0.9em;
    font-style: italic;

    .visibility {
      padding-left: $default-padding * 0.5;
      &:not(:first-child)::before {
        content: '- ';
      }

      .workout-visibility {
        padding-right: $default-padding * 0.5;
      }
      .visibility-label {
        color: var(--text-visibilty);
        text-transform: lowercase;
      }
      @media screen and (max-width: $x-small-limit) {
        .visibility-label {
          display: none;
        }
      }
    }
  }
</style>
