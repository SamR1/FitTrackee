<template>
  <div id="user-stats">
    <StatCard
      icon="calendar"
      :value="user.nb_workouts"
      :text="$t('workouts.WORKOUT', user.nb_workouts)"
    />
    <StatCard
      icon="road"
      :value="totalDistance"
      :text="distanceUnitTo === 'mi' ? 'miles' : distanceUnitTo"
    />
    <StatCard
      v-if="user.display_ascent"
      icon="location-arrow"
      :value="totalAscent"
      :text="ascentUnitTo === 'ft' ? 'feet' : ascentUnitTo"
    />
    <StatCard
      icon="clock-o"
      :value="totalDuration.days"
      :text="totalDuration.duration"
    />
    <StatCard
      v-if="!user.display_ascent"
      icon="tags"
      :value="user.nb_sports"
      :text="$t('workouts.SPORT', user.nb_sports)"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'

  import StatCard from '@/components/Common/StatCard.vue'
  import type { TUnit } from '@/types/units'
  import type { IAuthUserProfile } from '@/types/user'
  import { getDuration } from '@/utils/duration'
  import { convertDistance, units } from '@/utils/units'
  interface Props {
    user: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const { t } = useI18n()

  const { user } = toRefs(props)

  const totalDuration = computed(() =>
    getDuration(user.value.total_duration, t)
  )
  const distanceUnitFrom: TUnit = 'km'
  const distanceUnitTo: TUnit = user.value.imperial_units
    ? units[distanceUnitFrom].defaultTarget
    : distanceUnitFrom
  const totalDistance: ComputedRef<number> = computed(() =>
    user.value.imperial_units
      ? convertDistance(
          user.value.total_distance,
          distanceUnitFrom,
          distanceUnitTo,
          2
        )
      : parseFloat(user.value.total_distance.toFixed(2))
  )
  const ascentUnitFrom: TUnit = 'm'
  const ascentUnitTo: TUnit = user.value.imperial_units
    ? units[ascentUnitFrom].defaultTarget
    : ascentUnitFrom
  const totalAscent: ComputedRef<number> = computed(() =>
    user.value.imperial_units
      ? convertDistance(
          user.value.total_ascent,
          ascentUnitFrom,
          ascentUnitTo,
          2
        )
      : parseFloat(user.value.total_ascent.toFixed(2))
  )
</script>

<style lang="scss">
  #user-stats {
    display: flex;
    flex: 1 0 25%;
    justify-content: space-around;
    flex-wrap: wrap;
  }
</style>
