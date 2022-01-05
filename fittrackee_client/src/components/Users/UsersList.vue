<template>
  <div class="users-list">
    <div class="container users-container">
      <div v-for="user in users" :key="user.username" class="user-box">
        <UserCard :authUser="authUser" :user="user" />
      </div>
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
    computed,
    onBeforeMount,
    onUnmounted,
    reactive,
    toRefs,
    watch,
  } from 'vue'
  import { LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import UserCard from '@/components/User/UserCard.vue'
  import { USERS_STORE } from '@/store/constants'
  import { IPagination, TPaginationPayload } from '@/types/api'
  import { IAuthUserProfile, IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getQuery } from '@/utils/api'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { authUser } = toRefs(props)
  const orderByList: string[] = ['created_at', 'username', 'workouts_count']
  const defaultOrderBy = 'created_at'
  let query: TPaginationPayload = reactive(
    getQuery(route.query, orderByList, defaultOrderBy)
  )
  const users: ComputedRef<IUserProfile[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
  )

  onBeforeMount(() => loadUsers(query))

  function loadUsers(queryParams: TPaginationPayload) {
    store.dispatch(USERS_STORE.ACTIONS.GET_USERS, queryParams)
  }

  onUnmounted(() => {
    store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
  })

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getQuery(newQuery, orderByList, defaultOrderBy, { query })
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
  }
</style>
