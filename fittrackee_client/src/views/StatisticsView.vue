<template>
  <div id="statistics">
    <div class="container" v-if="authUser.username">
      <Statistics :user="authUser" :sports="sports" />
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent } from 'vue'

  import Statistics from '@/components/Statistics/index.vue'
  import { USER_STORE, SPORTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'StatisticsView',
    components: {
      Statistics,
    },
    setup() {
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports: ComputedRef<ISport[]> = computed(() =>
        store.getters[SPORTS_STORE.GETTERS.SPORTS].filter((sport) =>
          authUser.value.sports_list.includes(sport.id)
        )
      )
      return { authUser, sports }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #statistics {
    height: 100%;
  }
</style>
