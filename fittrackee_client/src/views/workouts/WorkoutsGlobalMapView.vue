<template>
  <div
    id="workouts-global-map"
    v-if="appConfig.enable_geospatial_features && authUser.username"
    class="view"
  >
    <div class="container">
      <Card>
        <template #title>
          {{ capitalize($t('workouts.MAP')) }}
        </template>
        <template #content>
          <div class="form-items-group">
            <div class="form-item">
              <label for="from"> {{ $t('workouts.FROM') }}: </label>
              <input
                id="from"
                name="from"
                type="date"
                :disabled="mapLoading"
                :value="$route.query.from"
                @change="handleFilterChange"
              />
            </div>
            <div class="form-item">
              <label for="to"> {{ $t('workouts.TO') }}: </label>
              <input
                id="to"
                name="to"
                type="date"
                :value="$route.query.to"
                :disabled="mapLoading"
                @change="handleFilterChange"
              />
            </div>
          </div>
          <WorkoutsMap
            :translatedSports="translatedSports"
            :global-map="true"
          />
          <SportsMenu
            :selected-sport-ids="selectedSportIds"
            :user-sports="userSports"
            :disabled="mapLoading"
            @selectedSportIdsUpdate="updateSelectedSportIds"
          />
          <div class="buttons">
            <button
              type="submit"
              class="confirm"
              @click="onFilter"
              :disabled="mapLoading || selectedSportIds.length === 0"
            >
              {{ $t('buttons.FILTER') }}
            </button>
            <button
              class="confirm"
              @click="onClearFilter"
              :disabled="mapLoading"
            >
              {{ $t('buttons.CLEAR_FILTER') }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { capitalize, computed, onBeforeMount, ref, watch } from 'vue'
  import type { Ref, ComputedRef } from 'vue'
  import { useI18n } from 'vue-i18n'
  import { type LocationQuery, useRoute, useRouter } from 'vue-router'

  import SportsMenu from '@/components/Statistics/StatsSportsMenu.vue'
  import WorkoutsMap from '@/components/Workouts/WorkoutsMap.vue'
  import useApp from '@/composables/useApp.ts'
  import useSports from '@/composables/useSports.ts'
  import { AUTH_USER_STORE, WORKOUTS_STORE } from '@/store/constants'
  import type { ISport, ITranslatedSport } from '@/types/sports'
  import type { IAuthUserProfile } from '@/types/user'
  import type { TMapParamsKeys, TWorkoutsMapPayload } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore'
  import { translateSports } from '@/utils/sports'

  const store = useStore()
  const route = useRoute()
  const router = useRouter()
  const { t } = useI18n()

  const { appConfig } = useApp()
  const { sports } = useSports()

  const paramsKeys: TMapParamsKeys[] = ['to', 'from', 'sport_ids']

  let params: TWorkoutsMapPayload = getWorkoutsMapQuery(route.query)
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const userSports: ComputedRef<ISport[]> = computed(() =>
    sports.value.filter((sport) =>
      authUser.value.sports_list.includes(sport.id)
    )
  )
  const translatedSports: ComputedRef<ITranslatedSport[]> = computed(() =>
    translateSports(sports.value, t)
  )
  const selectedSportIds: Ref<number[]> = ref(getSports(userSports.value))
  const mapLoading: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.MAP_LOADING]
  )

  function handleFilterChange(event: Event) {
    const name = (event.target as HTMLInputElement).name as TMapParamsKeys
    const value = (event.target as HTMLInputElement).value
    if (value === '') {
      delete params[name]
    } else {
      params[name] = value
    }
  }
  function loadWorkouts(payload: TWorkoutsMapPayload) {
    store.dispatch(
      WORKOUTS_STORE.ACTIONS.GET_AUTH_USER_WORKOUTS_FOR_GLOBAl_MAP,
      payload
    )
  }
  function getSports(sports: ISport[]) {
    return sports.map((sport) => sport.id)
  }
  function updateSelectedSportIds(sportId: number) {
    if (selectedSportIds.value.includes(sportId)) {
      selectedSportIds.value = selectedSportIds.value.filter(
        (id) => id !== sportId
      )
    } else {
      selectedSportIds.value.push(sportId)
    }
    if (selectedSportIds.value.length === 0) {
      delete params.sport_ids
    } else {
      params.sport_ids = selectedSportIds.value.join(',')
    }
  }
  function getWorkoutsMapQuery(
    locationQuery: LocationQuery
  ): TWorkoutsMapPayload {
    const newQuery = {} as TWorkoutsMapPayload
    paramsKeys.forEach((key: TMapParamsKeys) => {
      if (typeof locationQuery[key] === 'string') {
        newQuery[key] = locationQuery[key]
      } else {
        delete newQuery[key]
      }
    })
    return newQuery
  }
  function onClearFilter() {
    router.push({ path: '/workouts/map', query: {} })
  }
  function onFilter() {
    router.push({ path: '/workouts/map', query: params })
  }

  watch(
    () => route.query,
    async (newQuery) => {
      loadWorkouts(getWorkoutsMapQuery(newQuery))
    }
  )

  onBeforeMount(() => {
    // temporary redirection
    if (!appConfig.value.enable_geospatial_features) {
      router.push('/')
    }
    loadWorkouts(params)
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  #workouts-global-map {
    .container {
      .card {
        width: 100%;
        .form-items-group {
          display: flex;
          gap: $default-padding;
          flex-wrap: wrap;
          width: 100%;
          .spacer {
            flex-grow: 3;
          }
        }

        #workouts-map {
          padding: 0;
        }

        .sports-menu {
          padding: 0;
        }

        .buttons {
          margin-top: $default-margin;
          display: flex;
          gap: $default-padding;
          flex-wrap: wrap;
        }
      }
    }
  }
</style>
