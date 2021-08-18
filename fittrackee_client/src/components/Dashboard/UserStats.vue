<template>
  <div id="user-stats">
    <UserStatCard
      icon="calendar"
      :value="user.nb_workouts"
      :text="t('workouts.WORKOUT', user.nb_workouts)"
    />
    <UserStatCard
      icon="road"
      :value="Number(user.total_distance).toFixed(2)"
      :text="t('workouts.KM')"
    />
    <UserStatCard
      icon="clock-o"
      :value="total_duration.days"
      :text="total_duration.duration"
    />
    <UserStatCard
      icon="tags"
      :value="user.nb_sports"
      :text="t('workouts.SPORT', user.nb_sports)"
    />
  </div>
</template>

<script lang="ts">
  import { ComputedRef, PropType, defineComponent, computed } from 'vue'
  import { useI18n } from 'vue-i18n'

  import { IAuthUserProfile } from '@/store/modules/user/interfaces'
  import UserStatCard from '@/components/Dashboard/UserStatCard.vue'

  export default defineComponent({
    name: 'UserStats',
    components: {
      UserStatCard,
    },
    props: {
      user: {
        type: Object as PropType<IAuthUserProfile>,
        required: true,
      },
    },
    setup(props) {
      const { t } = useI18n()
      const total_duration: ComputedRef<string> = computed(
        () => props.user.total_duration
      )

      function get_duration(total_duration: ComputedRef<string>) {
        const duration = total_duration.value.match(/day/g)
          ? total_duration.value.split(', ')[1]
          : total_duration.value
        return {
          days: total_duration.value.match(/day/g)
            ? `${total_duration.value.split(' ')[0]} ${
                total_duration.value.match(/days/g)
                  ? t('common.DAY', 2)
                  : t('common.DAY', 1)
              }`
            : `0 ${t('common.DAY', 2)},`,
          duration: `${duration.split(':')[0]}h ${duration.split(':')[1]}min`,
        }
      }

      return {
        t,
        total_duration: computed(() => get_duration(total_duration)),
      }
    },
  })
</script>

<style lang="scss">
  @import '~@/scss/base';
  #user-stats {
    display: flex;
    flex: 1 0 25%;
    justify-content: space-around;
    flex-wrap: wrap;
  }
</style>
