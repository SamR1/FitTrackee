<template>
  <div
    id="workouts-global-map"
    v-if="appConfig.enable_geospatial_features && authUser.username"
    class="view"
  >
    <div class="container">
      <Card>
        <template #title>
          {{ capitalize($t('workouts.GLOBAL_MAP')) }}
        </template>
        <template #content>
          <div class="form-items-group">
            <div class="form-item">
              <label for="from"> {{ $t('workouts.FROM') }}: </label>
              <input
                id="from"
                :disabled="disableMap"
                name="from"
                type="date"
                v-model="params.from"
                @change="handleFilterChange"
              />
            </div>
            <div class="form-item">
              <label for="to"> {{ $t('workouts.TO') }}: </label>
              <input
                id="to"
                :disabled="disableMap"
                name="to"
                type="date"
                v-model="params.to"
                @change="handleFilterChange"
              />
            </div>
          </div>
          <WorkoutsMap
            v-if="userSports.length > 0"
            :translatedSports="translatedSports"
            :global-map="true"
            :user-has-workouts="userHasWorkouts"
          />
          <div v-else class="no-map">
            {{ $t('workouts.NO_WORKOUTS_TO_DISPLAY') }}.
            <router-link to="/workouts/add">
              {{ $t('workouts.UPLOAD_FIRST_WORKOUT') }}
            </router-link>
          </div>
          <SportsMenu
            v-if="userSports.length > 0"
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
              :disabled="
                mapLoading || selectedSportIds.length === 0 || disableButtons
              "
            >
              {{ $t('buttons.FILTER') }}
            </button>
            <button
              class="confirm"
              @click="onClearFilter"
              :disabled="disableMap || JSON.stringify(params) === '{}'"
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
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

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

  const mapLoading: ComputedRef<boolean> = computed(
    () => store.getters[WORKOUTS_STORE.GETTERS.MAP_LOADING]
  )
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
  const userHasWorkouts: ComputedRef<boolean> = computed(
    () => userSports.value.length > 0
  )
  const disableMap: ComputedRef<boolean> = computed(
    () => mapLoading.value || !userHasWorkouts.value
  )
  const params: Ref<TWorkoutsMapPayload> = ref(getWorkoutsMapQuery(route.query))
  const selectedSportIds: Ref<number[]> = ref(getSports(userSports.value))
  const disableButtons: Ref<boolean> = ref(true)

  function handleFilterChange(event: Event) {
    const name = (event.target as HTMLInputElement).name as TMapParamsKeys
    const value = (event.target as HTMLInputElement).value
    if (value === '') {
      delete params.value[name]
    } else {
      params.value[name] = value
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
      delete params.value.sport_ids
    } else {
      params.value.sport_ids = selectedSportIds.value.join(',')
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
  function push(query: TWorkoutsMapPayload) {
    disableButtons.value = true
    router.push({ path: '/workouts/map', query })
  }
  function onClearFilter() {
    selectedSportIds.value = getSports(userSports.value)
    delete params.value.sport_ids
    push({})
  }
  function onFilter() {
    push(params.value)
  }

  watch(
    () => route.query,
    async (newQuery) => {
      params.value = getWorkoutsMapQuery(newQuery)
      loadWorkouts(params.value)
    }
  )
  watch(
    () => params,
    async () => {
      disableButtons.value = false
    },
    {
      deep: true,
    }
  )
  watch(
    () => userSports.value,
    async () => {
      selectedSportIds.value = getSports(userSports.value)
    }
  )

  onBeforeMount(() => {
    // temporary redirection
    if (!appConfig.value.enable_geospatial_features) {
      router.push('/')
    }
    loadWorkouts(params.value)
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
        .no-map {
          margin: $default-margin * 4 0 $default-margin;
          height: 500px;
          width: 100%;
          line-height: 500px;
          filter: var(--no-map-filter);
          a {
            color: var(--app-color-light);
          }
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
