<template>
  <div id="workouts" v-if="authUser.username">
    <div class="container workouts-container">
      <div class="filters-container">
        <WorkoutsFilters :sports="translatedSports" @filter="updateParams" />
      </div>
      <div class="list-container">
        <WorkoutsList
          :user="authUser"
          :params="params"
          :sports="translatedSports"
        />
      </div>
    </div>
  </div>
</template>

<script lang="ts">
  import { ComputedRef, Ref, computed, defineComponent, ref } from 'vue'
  import { useI18n } from 'vue-i18n'

  import WorkoutsFilters from '@/components/Workouts/WorkoutsFilters.vue'
  import WorkoutsList from '@/components/Workouts/WorkoutsList.vue'
  import { USER_STORE, SPORTS_STORE } from '@/store/constants'
  import { ISport, ITranslatedSport } from '@/types/sports'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  export default defineComponent({
    name: 'WorkoutsView',
    components: {
      WorkoutsFilters,
      WorkoutsList,
    },
    setup() {
      const { t } = useI18n()
      const store = useStore()
      const authUser: ComputedRef<IAuthUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const sports: ComputedRef<ISport[]> = computed(
        () => store.getters[SPORTS_STORE.GETTERS.SPORTS]
      )
      const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
        translateSports(sports.value, t)
      )
      const params: Ref<Record<string, string>> = ref({})

      function updateParams(filters: Record<string, string>) {
        params.value = filters
      }
      return { authUser, params, translatedSports, updateParams }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base';
  #workouts {
    height: 100%;

    .workouts-container {
      display: flex;
      flex-direction: row;
      @media screen and (max-width: $medium-limit) {
        flex-direction: column;
      }

      .filters-container,
      .list-container {
        display: flex;
        flex-direction: column;
      }

      .filters-container {
        width: 25%;
        @media screen and (max-width: $medium-limit) {
          width: 100%;
        }
      }

      .list-container {
        width: 75%;
        @media screen and (max-width: $medium-limit) {
          width: 100%;
        }
      }
    }
  }
</style>
