<template>
  <div id="statistics">
    <div class="container" v-if="authUser.username">
      <Card>
        <template #title>{{ $t('statistics.STATISTICS') }}</template>
        <template #content>
          <Statistics :user="authUser" :sports="sports" />
        </template>
      </Card>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, computed, defineComponent } from 'vue'

  import Card from '@/components/Common/Card.vue'
  import Statistics from '@/components/Statistics/index.vue'
  import { USER_STORE, SPORTS_STORE } from '@/store/constants'
  import { ISport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'StatisticsView',
    components: {
      Card,
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
    display: flex;
    width: 100%;
    margin-bottom: 30px;
    .container {
      width: 100%;
      ::v-deep(.card) {
        width: 100%;
      }
    }
  }
</style>
