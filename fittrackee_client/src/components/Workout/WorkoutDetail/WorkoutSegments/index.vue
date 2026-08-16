<template>
  <div id="workout-segments" :class="{ 'with-tabs': displayTabs }">
    <Card>
      <template #title v-if="displayTabs">
        <div
          class="title-tab transparent"
          :class="{ 'as-tab': displayTabs, active: tab === 'chart' }"
        >
          <button class="transparent capitalize" @click="tab = 'chart'">
            {{ $t('workouts.SEGMENT', 2) }}
          </button>
        </div>
        <div
          class="title-tab transparent"
          :class="{ 'as-tab': displayTabs, active: tab === 'sportsStats' }"
        >
          <button class="transparent capitalize" @click="tab = 'sportsStats'">
            {{ $t('workouts.SPORTS_STATS') }}
          </button>
        </div>
      </template>
      <template #title v-else>
        {{ $t('workouts.SEGMENT', 2) }}
      </template>

      <template #content>
        <WorkoutSegmentsList
          v-show="tab === 'chart'"
          :segments="segments"
          :useImperialUnits="useImperialUnits"
        />
        <template v-if="displayTabs">
          <WorkoutSegmentsSportsStats
            v-show="tab === 'sportsStats'"
            :authUser="authUser"
            :sports-stats="multiSportsStats"
            :cadenceUnit="cadenceUnit"
          />
        </template>
      </template>
    </Card>
  </div>
</template>

<script setup lang="ts">
  import { computed, ref, toRefs } from 'vue'
  import type { ComputedRef, Ref } from 'vue'

  import WorkoutSegmentsList from '@/components/Workout/WorkoutDetail/WorkoutSegments/WorkoutSegmentsList.vue'
  import WorkoutSegmentsSportsStats from '@/components/Workout/WorkoutDetail/WorkoutSegments/WorkoutSegmentsSportsStats.vue'
  import type { IAuthUserProfile } from '@/types/user.ts'
  import type {
    IMultiSportsStats,
    IWorkoutSegment,
    TCadenceUnit,
  } from '@/types/workouts'

  interface Props {
    authUser: IAuthUserProfile
    cadenceUnit: TCadenceUnit
    segments: IWorkoutSegment[]
    useImperialUnits: boolean
    multiSportsStats: Record<number, IMultiSportsStats>
  }
  const props = defineProps<Props>()
  const {
    authUser,
    cadenceUnit,
    multiSportsStats,
    segments,
    useImperialUnits,
  } = toRefs(props)

  const tab: Ref<'chart' | 'sportsStats'> = ref('chart')
  const displayTabs: ComputedRef<boolean> = computed(
    () => Object.keys(multiSportsStats.value).length > 0
  )
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workout-segments {
    &.with-tabs {
      ::v-deep(.card) {
        .card-title {
          padding: 0;
        }
      }
    }

    ::v-deep(.card) {
      .card-title {
        text-transform: capitalize;
        display: flex;

        .title-tab {
          height: 100%;
          padding: $default-padding * 0.25 0;

          button {
            padding: $default-padding * 0.65 $default-padding * 2;
          }

          &.as-tab {
            border-right: 1px solid var(--input-border-color);
            border-top-right-radius: 5px;
          }
          &.active {
            button {
              font-weight: bold;
            }
          }
        }
      }

      .card-content {
        padding-bottom: 0;
        padding-top: 0;
      }
    }
  }
</style>
