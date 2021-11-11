<template>
  <div
    class="sport-img"
    :style="{ fill: sportColors[sportLabel] }"
    :title="title ? title : $t(`sports.${sportLabel}.LABEL`)"
  >
    <CyclingSport v-if="sportLabel === 'Cycling (Sport)'" />
    <CyclingTransport v-if="sportLabel === 'Cycling (Transport)'" />
    <Hiking v-if="sportLabel === 'Hiking'" />
    <MountainBiking v-if="sportLabel === 'Mountain Biking'" />
    <MountainBikingElectric
      v-if="sportLabel === 'Mountain Biking (Electric)'"
    />
    <Rowing v-if="sportLabel === 'Rowing'" />
    <Running v-if="sportLabel === 'Running'" />
    <SkiingAlpine v-if="sportLabel === 'Skiing (Alpine)'" />
    <SkiingCrossCountry v-if="sportLabel === 'Skiing (Cross Country)'" />
    <Trail v-if="sportLabel === 'Trail'" />
    <Walking v-if="sportLabel === 'Walking'" />
  </div>
</template>

<script setup lang="ts">
  import { inject, toRefs, withDefaults } from 'vue'

  import CyclingSport from '@/components/Common/Images/SportImage/CyclingSport.vue'
  import CyclingTransport from '@/components/Common/Images/SportImage/CyclingTransport.vue'
  import Hiking from '@/components/Common/Images/SportImage/Hiking.vue'
  import MountainBiking from '@/components/Common/Images/SportImage/MountainBiking.vue'
  import MountainBikingElectric from '@/components/Common/Images/SportImage/MountainBikingElectric.vue'
  import Rowing from '@/components/Common/Images/SportImage/Rowing.vue'
  import Running from '@/components/Common/Images/SportImage/Running.vue'
  import SkiingAlpine from '@/components/Common/Images/SportImage/SkiingAlpine.vue'
  import SkiingCrossCountry from '@/components/Common/Images/SportImage/SkiingCrossCountry.vue'
  import Trail from '@/components/Common/Images/SportImage/Trail.vue'
  import Walking from '@/components/Common/Images/SportImage/Walking.vue'

  interface Props {
    sportLabel: string
    title?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    title: '',
  })

  const { sportLabel, title } = toRefs(props)
  const sportColors = inject('sportColors')
</script>
