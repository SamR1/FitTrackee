<template>
  <div class="users-list">
    <UsersFilters @filterOnUsername="searchUsers" />
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
  </div>
</template>

<script setup lang="ts">
  import {
    ComputedRef,
    Ref,
    computed,
    onBeforeMount,
    onUnmounted,
    ref,
    toRefs,
    watch,
  } from 'vue'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import UsersFilters from '@/components/Users/UsersFilters.vue'
  import { USERS_STORE } from '@/store/constants'
  import { IPagination } from '@/types/api'
  import { IAuthUserProfile, IUserProfile, TUsersPayload } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getQuery } from '@/utils/api'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()
  const router = useRouter()

  const { authUser } = toRefs(props)
  const orderByList: string[] = ['created_at', 'username', 'workouts_count']
  const defaultOrderBy = 'created_at'
  let query: TUsersPayload = getUsersQuery(route.query)
  const users: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )
  const updatedUser: Ref<string | null> = ref(null)

  onBeforeMount(() => loadUsers(query))

  function loadUsers(queryParams: TUsersPayload) {
    queryParams.per_page = 9
    store.dispatch(USERS_STORE.ACTIONS.GET_USERS, queryParams)
  }
  function storeUser(username: string) {
    updatedUser.value = username
  }
  function searchUsers(username: Ref<string>) {
    if (username.value !== '') {
      query = { q: username.value }
    } else {
      const newQuery: LocationQuery = Object.assign({}, route.query)
      query = getUsersQuery(newQuery)
    }
    router.push({ path: '/users', query })
  }

  function getUsersQuery(newQuery: LocationQuery): TUsersPayload {
    query = getQuery(newQuery, orderByList, defaultOrderBy)
    if (newQuery.q) {
      // eslint-disable-next-line @typescript-eslint/ban-ts-comment
      // @ts-ignore
      query.q = newQuery.q
    }
    return query
  }

  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  })

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getUsersQuery(newQuery)
      loadUsers(query)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
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
