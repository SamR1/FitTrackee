<template>
  <div id="user-stats">
    <StatCard
      icon="users"
      :value="appStatistics.users"
      :text="$t('admin.USER', appStatistics.users)"
    />
    <StatCard
      icon="tags"
      :value="appStatistics.sports"
      :text="$t('workouts.SPORT', appStatistics.sports)"
    />
    <StatCard
      icon="calendar"
      :value="appStatistics.workouts"
      :text="$t('workouts.WORKOUT', appStatistics.workouts)"
    />
    <StatCard
      icon="folder-open"
      :value="uploadDirSize.size"
      :text="uploadDirSize.suffix"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, toRefs } from 'vue'

  import StatCard from '@/components/Common/StatCard.vue'
  import type { IAppStatistics } from '@/types/application'
  import { getReadableFileSize } from '@/utils/files'

  interface Props {
    appStatistics: IAppStatistics
  }
  const props = defineProps<Props>()

  const { appStatistics } = toRefs(props)
  const uploadDirSize = computed(() =>
    getReadableFileSize(appStatistics.value.uploads_dir_size, false)
  )
</script>

<style lang="scss">
  #user-stats {
    display: flex;
    flex-wrap: wrap;
  }
</style>
