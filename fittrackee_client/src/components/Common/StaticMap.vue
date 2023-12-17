<template>
  <div class="static-map" :class="{ 'display-hover': displayHover }">
    <img v-if="displayHover" :src="imageUrl" alt="" />
    <div
      v-else
      class="bg-map-image"
      :style="{
        backgroundImage: `url(${imageUrl})`,
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

<script setup lang="ts">
  import { toRefs } from 'vue'

  import type { IWorkout } from '@/types/workouts'
  import { getApiUrl } from '@/utils'

  interface Props {
    workout: IWorkout
    displayHover?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    displayHover: false,
  })
  const { displayHover } = toRefs(props)
  const imageUrl = `${getApiUrl()}workouts/map/${props.workout.map}`
</script>

<style lang="scss">
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
      filter: var(--map-display-hover-filter);

      .map-attribution-text {
        color: var(--map-display-hover-attribution-text);
        background-color: var(--map-attribution-bg-color);
      }
    }

    .bg-map-image {
      background-size: cover;
      background-position: center;
      opacity: 0.6;
      height: 200px;
      width: 100%;
      filter: var(--map-filter);
    }

    .map-attribution {
      top: 0;
      right: 0;
      font-size: 11px;
      position: absolute;
    }

    .map-attribution-text {
      color: var(--map-attribution-text);
      background-color: var(--map-attribution-bg-color);
    }
  }
</style>
