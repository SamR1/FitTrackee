<template>
  <div
    class="sport-img"
    :style="{ fill: sportColors[sportLabel] }"
    :title="title ? title : t(`sports.${sportLabel}.LABEL`)"
  >
    <CyclingSport v-if="sportLabel === 'Cycling (Sport)'" />
    <CyclingTransport v-if="sportLabel === 'Cycling (Transport)'" />
    <Hiking v-if="sportLabel === 'Hiking'" />
    <MountainBiking v-if="sportLabel === 'Mountain Biking'" />
    <Running v-if="sportLabel === 'Running'" />
    <Walking v-if="sportLabel === 'Walking'" />
  </div>
</template>

<script lang="ts">
  import { defineComponent } from 'vue'
  import { useI18n } from 'vue-i18n'

  import CyclingSport from '@/components/Common/SportImage/CyclingSport.vue'
  import CyclingTransport from '@/components/Common/SportImage/CyclingTransport.vue'
  import Hiking from '@/components/Common/SportImage/Hiking.vue'
  import MountainBiking from '@/components/Common/SportImage/MountainBiking.vue'
  import Running from '@/components/Common/SportImage/Running.vue'
  import Walking from '@/components/Common/SportImage/Walking.vue'
  import { sportColors } from '@/utils/sports'

  export default defineComponent({
    name: 'SportImg',
    components: {
      CyclingSport,
      CyclingTransport,
      Hiking,
      MountainBiking,
      Running,
      Walking,
    },
    props: {
      sportLabel: {
        type: String,
        required: true,
      },
      title: {
        type: String,
        required: false,
      },
    },
    setup() {
      const { t } = useI18n()
      return { sportColors, t }
    },
  })
</script>
