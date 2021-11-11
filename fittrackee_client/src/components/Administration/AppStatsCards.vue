<template>
  <div id="user-stats">
    <StatCard
      icon="users"
      :value="usersCount"
      :text="$t('admin.USER', usersCount)"
    />
    <StatCard
      icon="tags"
      :value="sportsCount"
      :text="$t('workouts.SPORT', sportsCount)"
    />
    <StatCard
      icon="calendar"
      :value="workoutCount"
      :text="$t('workouts.WORKOUT', workoutCount)"
    />
    <StatCard
      icon="folder-open"
      :value="uploadDirSize.size"
      :text="uploadDirSize.suffix"
    />
  </div>
</template>

<script setup lang="ts">
  import { computed, withDefaults } from 'vue'

  import StatCard from '@/components/Common/StatCard.vue'
  import { IAppStatistics } from '@/types/application'
  import { getReadableFileSize } from '@/utils/files'

  interface Props {
    appStatistics?: IAppStatistics
  }
  const props = withDefaults(defineProps<Props>(), {
    appStatistics: () => ({} as IAppStatistics),
  })

  const uploadDirSize = computed(() =>
    props.appStatistics.uploads_dir_size
      ? getReadableFileSize(props.appStatistics.uploads_dir_size, false)
      : { size: 0, suffix: 'bytes' }
  )
  const usersCount = computed(() =>
    props.appStatistics.users ? props.appStatistics.users : 0
  )
  const sportsCount = computed(() =>
    props.appStatistics.sports ? props.appStatistics.sports : 0
  )
  const workoutCount = computed(() =>
    props.appStatistics.workouts ? props.appStatistics.workouts : 0
  )
</script>

<style lang="scss">
  @import '~@/scss/base';
  #user-stats {
    display: flex;
    flex-wrap: wrap;
  }
</style>
