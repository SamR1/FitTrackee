<template>
  <LMarker
    v-if="markerCoordinates.latitude"
    :lat-lng="[markerCoordinates.latitude, markerCoordinates.longitude]"
  >
    <LIcon
      :icon-url="`/img/workouts/${isStart ? 'start' : 'finish'}.svg`"
      :iconSize="[15, 15]"
    />
  </LMarker>
</template>

<script lang="ts" setup>
  import { LIcon, LMarker } from '@vue-leaflet/vue-leaflet'
  import { toRefs } from 'vue'

  import type { TCoordinates } from '@/types/map'

  interface Props {
    markerCoordinates: TCoordinates
    isStart: boolean
  }
  const props = defineProps<Props>()
  const { isStart, markerCoordinates } = toRefs(props)
</script>
