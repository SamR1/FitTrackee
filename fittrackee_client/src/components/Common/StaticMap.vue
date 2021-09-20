<template>
  <div class="static-map">
    <img
      class="map-image"
      :src="`${getApiUrl()}workouts/map/${workout.map}?${Date.now()}`"
      alt="workout map"
    />
    <div class="map-attribution">
      <span class="map-attribution-text">©</span>
      <a
        class="map-attribution-text"
        href="http://www.openstreetmap.org/copyright"
        target="_blank"
        rel="noopener noreferrer"
      >
        OpenStreetMap
      </a>
    </div>
  </div>
</template>

<script lang="ts">
  import { defineComponent, PropType } from 'vue'

  import { IWorkout } from '@/types/workouts'
  import { getApiUrl } from '@/utils'

  export default defineComponent({
    name: 'StaticMap',
    props: {
      workout: {
        type: Object as PropType<IWorkout>,
        required: true,
      },
    },
    setup() {
      return { getApiUrl }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';

  .static-map {
    display: flex;
    position: relative;

    .map-image {
      height: 225px;
      width: 400px;
    }

    .map-attribution {
      top: 0;
      right: 0;
      font-size: 11px;
      position: absolute;
    }

    .map-attribution-text {
      background-color: rgba(255, 255, 255, 0.7);
    }
  }
</style>
