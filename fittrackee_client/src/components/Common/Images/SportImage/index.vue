<template>
  <div
    class="sport-img"
    :style="{ fill: color ? color : sportColors[sportLabel] }"
    :title="title ? title : $t(`sports.${sportLabel}.LABEL`)"
  >
    <Canoeing v-if="sportLabel === 'Canoeing'" />
    <CyclingSport v-if="sportLabel === 'Cycling (Sport)'" />
    <CyclingTrekking v-if="sportLabel === 'Cycling (Trekking)'" />
    <CyclingTransport v-if="sportLabel === 'Cycling (Transport)'" />
    <CyclingVirtual v-if="sportLabel === 'Cycling (Virtual)'" />
    <Hiking v-if="sportLabel === 'Hiking'" />
    <Kayaking v-if="sportLabel === 'Kayaking'" />
    <MountainBiking v-if="sportLabel === 'Mountain Biking'" />
    <MountainBikingElectric
      v-if="sportLabel === 'Mountain Biking (Electric)'"
    />
    <Mountaineering v-if="sportLabel === 'Mountaineering'" />
    <Paragliding v-if="sportLabel === 'Paragliding'" />
    <OpenWaterSwimming v-if="sportLabel === 'Open Water Swimming'" />
    <Rowing v-if="sportLabel === 'Rowing'" />
    <Running v-if="sportLabel === 'Running'" />
    <SkiingAlpine v-if="sportLabel === 'Skiing (Alpine)'" />
    <SkiingCrossCountry v-if="sportLabel === 'Skiing (Cross Country)'" />
    <Snowshoes v-if="sportLabel === 'Snowshoes'" />
    <Swimrun v-if="sportLabel === 'Swimrun'" />
    <Trail v-if="sportLabel === 'Trail'" />
    <Walking v-if="sportLabel === 'Walking'" />
  </div>
</template>

<script setup lang="ts">
  import { toRefs } from 'vue'

  import Canoeing from '@/components/Common/Images/SportImage/Canoeing.vue'
  import CyclingSport from '@/components/Common/Images/SportImage/CyclingSport.vue'
  import CyclingTransport from '@/components/Common/Images/SportImage/CyclingTransport.vue'
  import CyclingTrekking from '@/components/Common/Images/SportImage/CyclingTrekking.vue'
  import CyclingVirtual from '@/components/Common/Images/SportImage/CyclingVirtual.vue'
  import Hiking from '@/components/Common/Images/SportImage/Hiking.vue'
  import Kayaking from '@/components/Common/Images/SportImage/Kayaking.vue'
  import MountainBiking from '@/components/Common/Images/SportImage/MountainBiking.vue'
  import MountainBikingElectric from '@/components/Common/Images/SportImage/MountainBikingElectric.vue'
  import Mountaineering from '@/components/Common/Images/SportImage/Mountaineering.vue'
  import OpenWaterSwimming from '@/components/Common/Images/SportImage/OpenWaterSwimming.vue'
  import Paragliding from '@/components/Common/Images/SportImage/Paragliding.vue'
  import Rowing from '@/components/Common/Images/SportImage/Rowing.vue'
  import Running from '@/components/Common/Images/SportImage/Running.vue'
  import SkiingAlpine from '@/components/Common/Images/SportImage/SkiingAlpine.vue'
  import SkiingCrossCountry from '@/components/Common/Images/SportImage/SkiingCrossCountry.vue'
  import Snowshoes from '@/components/Common/Images/SportImage/Snowshoes.vue'
  import Swimrun from '@/components/Common/Images/SportImage/Swimrun.vue'
  import Trail from '@/components/Common/Images/SportImage/Trail.vue'
  import Walking from '@/components/Common/Images/SportImage/Walking.vue'
  import useSports from '@/composables/useSports'

  interface Props {
    sportLabel: string
    color: string | null
    title?: string
  }
  const props = withDefaults(defineProps<Props>(), {
    title: '',
  })
  const { color, sportLabel, title } = toRefs(props)

  const { sportColors } = useSports()
</script>
