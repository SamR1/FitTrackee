<template>
  <div class="users-list">
    <UsersNameFilter @filterOnUsername="searchUsers" />
    <div class="container users-container" v-if="users.length > 0">
      <div v-for="user in users" :key="user.username" class="user-box">
        <UserCard
          :authUser="authUser"
          :user="user"
          :updatedUser="updatedUser"
          @updatedUserRelationship="storeUser"
        />
      </div>
    </div>
    <div class="no-users" v-else>
      {{ $t('user.NO_USERS_FOUND') }}
    </div>
    <Pagination
      v-if="pagination.page"
      path="/users"
      :pagination="pagination"
      :query="query"
    />
    <ErrorMessage :message="errorMessages" v-if="errorMessages" />
  </div>
</template>

<script setup lang="ts">
  import {
    computed,
    onBeforeMount,
    onUnmounted,
    reactive,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Reactive, Ref } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import UsersNameFilter from '@/components/Users/UsersNameFilter.vue'
  import useApp from '@/composables/useApp.ts'
  import useAuthUser from '@/composables/useAuthUser'
  import { USERS_STORE } from '@/store/constants'
  import type { IPagination, TPaginationPayload } from '@/types/api'
  import type {
    IAuthUserProfile,
    IUserProfile,
    TUsersPayload,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getQuery } from '@/utils/api'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const store = useStore()
  const route = useRoute()
  const router = useRouter()

  const { isAuthUserSuspended } = useAuthUser()
  const { errorMessages } = useApp()

  const orderByList: string[] = ['created_at', 'username', 'workouts_count']
  const defaultOrderBy = 'created_at'

  let query: Reactive<TPaginationPayload> = reactive(getUsersQuery(route.query))
  const updatedUser: Ref<string | null> = ref(null)

  const users: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  function loadUsers(queryParams: TUsersPayload) {
    if (!isAuthUserSuspended.value) {
      queryParams.per_page = 9
      store.dispatch(USERS_STORE.ACTIONS.GET_USERS, queryParams)
    }
  }
  function storeUser(username: string) {
    updatedUser.value = username
  }
  function searchUsers(username: Ref<string>) {
    if (username.value !== '') {
      query = getUsersQuery({ q: username.value })
    } else {
      const newQuery: LocationQuery = Object.assign({}, route.query)
      query = getUsersQuery(newQuery)
    }
    router.push({ path: '/users', query })
  }

  function getUsersQuery(newQuery: LocationQuery): TUsersPayload {
    const updateQuery = getQuery(newQuery, orderByList, defaultOrderBy)
    if (newQuery.q) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      updateQuery.q = newQuery.q
    }
    return updateQuery
  }

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getUsersQuery(newQuery)
      loadUsers(query)
    }
  )

  onBeforeMount(() => loadUsers(query))
  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  })
</script>

<style lang="scss" scoped>
  @use '~@/scss/vars.scss' as *;
  .users-list {
    display: flex;
    flex-direction: column;
    margin-bottom: 50px;
    width: 100%;

    .users-container {
      display: flex;
      align-content: flex-start;
      flex-wrap: wrap;
      padding: 0;
      width: 100%;

      .user-box {
        width: 33%;
        @media screen and (max-width: $medium-limit) {
          width: 50%;
        }
        @media screen and (max-width: $small-limit) {
          width: 100%;
        }
      }
    }

    .no-users {
      padding: $default-padding;
    }
  }
</style>
