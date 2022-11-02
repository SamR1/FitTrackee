<template>
  <div
    class="sport-img"
    :style="{ fill: color ? color : sportColors[sportLabel] }"
    :title="title ? title : $t(`sports.${sportLabel}.LABEL`)"
  >
    <CyclingSport v-if="sportLabel === 'Cycling (Sport)'" />
    <CyclingTransport v-if="sportLabel === 'Cycling (Transport)'" />
    <CyclingVirtual v-if="sportLabel === 'Cycling (Virtual)'" />
    <Hiking v-if="sportLabel === 'Hiking'" />
    <MountainBiking v-if="sportLabel === 'Mountain Biking'" />
    <MountainBikingElectric
      v-if="sportLabel === 'Mountain Biking (Electric)'"
    />
    <Rowing v-if="sportLabel === 'Rowing'" />
    <Running v-if="sportLabel === 'Running'" />
    <SkiingAlpine v-if="sportLabel === 'Skiing (Alpine)'" />
    <SkiingCrossCountry v-if="sportLabel === 'Skiing (Cross Country)'" />
    <Snowshoes v-if="sportLabel === 'Snowshoes'" />
    <Trail v-if="sportLabel === 'Trail'" />
    <Walking v-if="sportLabel === 'Walking'" />
  </div>
</template>

<script setup lang="ts">
  import { inject, toRefs, withDefaults } from 'vue'

  import CyclingSport from '@/components/Common/Images/SportImage/CyclingSport.vue'
  import CyclingTransport from '@/components/Common/Images/SportImage/CyclingTransport.vue'
  import CyclingVirtual from '@/components/Common/Images/SportImage/CyclingVirtual.vue'
  import Hiking from '@/components/Common/Images/SportImage/Hiking.vue'
  import MountainBiking from '@/components/Common/Images/SportImage/MountainBiking.vue'
  import MountainBikingElectric from '@/components/Common/Images/SportImage/MountainBikingElectric.vue'
  import Rowing from '@/components/Common/Images/SportImage/Rowing.vue'
  import Running from '@/components/Common/Images/SportImage/Running.vue'
  import SkiingAlpine from '@/components/Common/Images/SportImage/SkiingAlpine.vue'
  import SkiingCrossCountry from '@/components/Common/Images/SportImage/SkiingCrossCountry.vue'
  import Snowshoes from '@/components/Common/Images/SportImage/Snowshoes.vue'
  import Trail from '@/components/Common/Images/SportImage/Trail.vue'
  import Walking from '@/components/Common/Images/SportImage/Walking.vue'

  interface Props {
    sportLabel: string
    color: string | null
    title?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    title: '',
  })

  const { color, sportLabel, title } = toRefs(props)
  const sportColors = inject('sportColors')
</script>
