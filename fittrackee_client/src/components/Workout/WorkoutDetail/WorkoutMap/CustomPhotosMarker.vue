<template>
  <LMarker
    v-if="markerCoordinates?.latitude && markerCoordinates?.longitude"
    :lat-lng="[markerCoordinates.latitude, markerCoordinates.longitude]"
  >
    <LIcon :iconSize="[30, 30]" icon-url="/img/workouts/camera.svg" />
    <slot></slot>
  </LMarker>
</template>

<script lang="ts" setup>
  import { LIcon, LMarker } from '@vue-leaflet/vue-leaflet'
  import { toRefs } from 'vue'

  import type { TCoordinates } from '@/types/map'

  interface Props {
    markerCoordinates: TCoordinates | null
  }
  const props = defineProps<Props>()
  const { markerCoordinates } = toRefs(props)
</script>
