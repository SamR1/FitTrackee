<template>
  <div class="workout-visibility-levels" v-if="workoutObject.workoutVisibility">
    {{ $t('privacy.VISIBILITY') }}:
    <div class="visibility">
      <span v-if="workoutObject.with_gpx" class="workout-visibility">
        {{ $t('workouts.WORKOUT') }}
      </span>
      <i
        :class="`fa fa-${getPrivacyIcon(workoutObject.workoutVisibility)}`"
        aria-hidden="true"
        :title="$t(`privacy.LEVELS.${workoutObject.workoutVisibility}`)"
      />
      <span class="visibility-label">
        ({{
          $t(
            `privacy.LEVELS.${workoutObject.workoutVisibility}`
          )
        }})
      </span>
      <span v-if="workoutObject.with_gpx">-</span>
    </div>
    <div class="visibility" v-if="workoutObject.with_gpx">
      {{ $t('workouts.MAP') }}
      <i
        :class="`fa fa-${getPrivacyIcon(workoutObject.mapVisibility)}`"
        aria-hidden="true"
        :title="$t(`privacy.LEVELS.${workoutObject.mapVisibility}`)"
      />
      <span class="visibility-label">
        ({{
          $t(
            `privacy.LEVELS.${workoutObject.mapVisibility}`
          )
        }})
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import { TPrivacyLevels } from '@/types/user'
  import { IWorkoutObject } from '@/types/workouts'
  interface Props {
    workoutObject: IWorkoutObject
  }
  const props = defineProps<Props>()
  const { workoutObject } = toRefs(props)

  function getPrivacyIcon(privacyLevel: TPrivacyLevels): string {
    switch (privacyLevel) {
      case 'public':
        return 'globe'
      case 'followers_only':
        return 'users'
      default:
      case 'private':
        return 'lock'
    }
  }
</script>
<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  .workout-visibility-levels {
    display: flex;
    align-items: center;
    font-size: 0.9em;
    font-style: italic;

    .visibility {
      padding-left: $default-padding * 0.5;
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
