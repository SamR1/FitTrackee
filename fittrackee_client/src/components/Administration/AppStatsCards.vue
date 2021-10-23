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

<script lang="ts">
  import { PropType, defineComponent, computed } from 'vue'

  import StatCard from '@/components/Common/StatCard.vue'
  import { IAppStatistics } from '@/types/application'
  import { getReadableFileSize } from '@/utils/files'

  export default defineComponent({
    name: 'UserStatsCards',
    components: {
      StatCard,
    },
    props: {
      appStatistics: {
        type: Object as PropType<IAppStatistics>,
        default: () => {
          return {}
        },
      },
    },
    setup(props) {
      return {
        uploadDirSize: computed(() =>
          props.appStatistics.uploads_dir_size
            ? getReadableFileSize(props.appStatistics.uploads_dir_size, false)
            : { size: 0, suffix: 'bytes' }
        ),
        usersCount: computed(() =>
          props.appStatistics.users ? props.appStatistics.users : 0
        ),
        sportsCount: computed(() =>
          props.appStatistics.sports ? props.appStatistics.sports : 0
        ),
        workoutCount: computed(() =>
          props.appStatistics.workouts ? props.appStatistics.workouts : 0
        ),
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  #user-stats {
    display: flex;
    flex-wrap: wrap;
  }
</style>
