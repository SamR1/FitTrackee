<template>
  <div id="likes" class="view">
    <div class="center-card">
      <Card>
        <template #title>{{ capitalize($t(`workouts.LIKES`, 0)) }}</template>
        <template #content>
          <div v-if="users.length > 0">
            <div class="users">
              <UserCard
                v-for="user in users"
                :key="user.username"
                :authUser="authUser"
                :user="user"
                :updatedUser="updatedUser"
                @updatedUserRelationship="storeUser"
              />
            </div>
            <Pagination
              :path="`/${objectType}s/${objectId}/likes`"
              :pagination="pagination"
              :query="query"
            />
          </div>
          <div v-else class="no-likes">{{ $t('workouts.NO_LIKES') }}</div>
          <ErrorMessage
            v-if="errorMessages"
            :message="errorMessages"
            :no-margin="true"
          />
          <div>
            <button
              @click="
                $router.push(
                  commentWorkoutId
                    ? `/workouts/${commentWorkoutId}/comments/${objectId}`
                    : `/${objectType}s/${objectId}`
                )
              "
            >
              {{ $t(`workouts.BACK_TO_${objectType.toUpperCase()}`) }}
            </button>
          </div>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    capitalize,
    computed,
    onBeforeMount,
    onUnmounted,
    reactive,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { Reactive, Ref, ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Card from '@/components/Common/Card.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import useApp from '@/composables/useApp.ts'
  import useAuthUser from '@/composables/useAuthUser.ts'
  import { USERS_STORE, WORKOUTS_STORE } from '@/store/constants.ts'
  import type { IPagination, TPaginationPayload } from '@/types/api.ts'
  import type { IUserLightProfile } from '@/types/user.ts'
  import type { ILikesPayload } from '@/types/workouts.ts'
  import { useStore } from '@/use/useStore.ts'
  import { defaultPage, getNumberQueryValue } from '@/utils/api.ts'

  interface Props {
    objectType: 'comment' | 'workout'
  }
  const props = defineProps<Props>()
  const { objectType } = toRefs(props)

  const store = useStore()
  const route = useRoute()

  const { authUser } = useAuthUser()
  const { errorMessages } = useApp()

  const updatedUser: Ref<string | null> = ref(null)

  const users: ComputedRef<IUserLightProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )
  const objectId: ComputedRef<string> = computed(
    () =>
      (objectType.value === 'workout'
        ? route.params.workoutId
        : route.params.commentId) as string
  )
  const commentWorkoutId: ComputedRef<string | null> = computed(() =>
    route.params.workoutId ? (route.params.workoutId as string) : null
  )
  const query: Reactive<TPaginationPayload> = reactive(getQuery(route.query))
  const payload: ComputedRef<ILikesPayload> = computed(() => ({
    objectType: objectType.value,
    objectId: objectId.value,
    page: 1,
  }))
  function storeUser(username: string) {
    updatedUser.value = username
  }

  function getQuery(locationQuery: LocationQuery) {
    const newQuery = {} as TPaginationPayload
    newQuery.page = getNumberQueryValue(locationQuery.page, defaultPage)
    return newQuery
  }
  function getLikes(payload: ILikesPayload) {
    store.dispatch(WORKOUTS_STORE.ACTIONS.GET_LIKES, payload)
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery, oldQuery: LocationQuery) => {
      if (newQuery.page !== oldQuery.page) {
        query.page = getQuery(newQuery).page
        payload.value.page = newQuery.page ? +newQuery.page : 1
        getLikes(payload.value)
      }
    }
  )

  onBeforeMount(() => getLikes(payload.value))
  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  #likes {
    ::v-deep(.card-content) {
      padding: $default-padding;
      .no-likes {
        font-style: italic;
        padding: 0 0 $default-padding $default-padding * 0.5;
      }

      .users {
        display: flex;
        align-content: flex-start;
        flex-wrap: wrap;
        .box {
          margin: $default-margin * 0.5;
          width: 44%;
          @media screen and (max-width: $small-limit) {
            width: 100%;
          }
        }
      }
    }
  }
</style>
