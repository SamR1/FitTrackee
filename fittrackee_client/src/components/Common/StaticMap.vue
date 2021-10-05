<template>
  <div class="static-map" :class="{ 'display-hover': displayHover }">
    <img
      v-if="displayHover"
      :src="`${getApiUrl()}workouts/map/${workout.map}`"
      alt=""
    />
    <div
      v-else
      class="bg-map-image"
      :style="{
        backgroundImage: `url(${getApiUrl()}workouts/map/${workout.map})`,
      }"
    />
    <div class="map-attribution">
      <span class="map-attribution-text">©</span>
      <a
        class="map-attribution-text"
        href="https://www.openstreetmap.org/copyright"
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
      displayHover: {
        type: Boolean,
        default: false,
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

    &.display-hover {
      position: absolute;
      margin-left: 20px;
      margin-top: 3px;
      width: 400px;
      height: 225px;
      z-index: 100;
    }

    .bg-map-image {
      background-size: cover;
      background-position: center;
      opacity: 0.6;
      height: 200px;
      width: 100%;
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
