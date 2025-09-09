<template>
  <LMarker
    v-if="markerCoordinates.latitude"
    :lat-lng="[markerCoordinates.latitude, markerCoordinates.longitude]"
  >
    <LIcon :iconSize="[30, 30]" className="sport-icon">
      <SportImage :sport-label="sport" :color="color" :shadow="true" />
    </LIcon>
    <slot></slot>
  </LMarker>
</template>

<script lang="ts" setup>
  import { LIcon, LMarker } from '@vue-leaflet/vue-leaflet'
  import { toRefs } from 'vue'

  import type { TCoordinates } from '@/types/map'

  interface Props {
    markerCoordinates: TCoordinates
    sport: string
    color: string | null
  }
  const props = defineProps<Props>()
  const { markerCoordinates, sport, color } = toRefs(props)
</script>
