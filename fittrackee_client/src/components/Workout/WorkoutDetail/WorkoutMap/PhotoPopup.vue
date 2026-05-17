<template>
  <LPopup>
    <div
      class="map-photo"
      :title="media.description"
      @click="emit('displayMediaModal')"
    >
      <img :alt="media.description" :src="media.url" />
    </div>
  </LPopup>
</template>

<script lang="ts" setup>
  import { LPopup } from '@vue-leaflet/vue-leaflet'
  import { toRefs } from 'vue'

  import type { IMediaAttachment } from '@/types/workouts.ts'

  interface Props {
    media: IMediaAttachment
  }
  const props = defineProps<Props>()
  const { media } = toRefs(props)

  const emit = defineEmits<{
    displayMediaModal: []
  }>()
</script>

<style scoped lang="scss">
  .map-photo {
    cursor: pointer;
  }
</style>
