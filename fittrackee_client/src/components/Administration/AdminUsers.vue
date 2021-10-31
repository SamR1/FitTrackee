<template>
  <div id="admin-users" class="admin-card">
    <Card>
      <template #title>{{ capitalize($t('admin.USER', 0)) }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <AdminUsersSelects
          :sort="sort"
          :order_by="order_by"
          :query="query"
          @updateSelect="reloadUsers"
        />
        <div class="responsive-table">
          <table>
            <thead>
              <tr>
                <th>#</th>
                <th class="left-text">{{ $t('user.USERNAME') }}</th>
                <th class="left-text">{{ $t('user.EMAIL') }}</th>
                <th class="left-text">
                  {{ $t('user.PROFILE.REGISTRATION_DATE') }}
                </th>
                <th>
                  {{ capitalize($t('workouts.WORKOUT', 0)) }}
                </th>
                <th>{{ $t('user.ADMIN') }}</th>
                <th>{{ $t('admin.ACTION') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="user in users" :key="user.username">
                <td>
                  <span class="cell-heading">
                    {{ $t('user.PROFILE.PICTURE') }}
                  </span>
                  <UserPicture :user="user" />
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('user.USERNAME') }}
                  </span>
                  {{ user.username }}
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('user.EMAIL') }}
                  </span>
                  {{ user.email }}
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('user.PROFILE.REGISTRATION_DATE') }}
                  </span>
                  {{ user.created_at }}
                </td>
                <td class="center-text">
                  <span class="cell-heading">
                    {{ capitalize($t('workouts.WORKOUT', 0)) }}
                  </span>
                  {{ user.nb_workouts }}
                </td>
                <td class="center-text">
                  <span class="cell-heading">
                    {{ $t('user.ADMIN') }}
                  </span>
                  <i
                    :class="`fa fa${user.admin ? '-check' : ''}-square-o`"
                    aria-hidden="true"
                  />
                </td>
                <td class="center-text">
                  <span class="cell-heading">
                    {{ $t('admin.ACTION') }}
                  </span>
                  <button
                    :class="{ danger: user.admin }"
                    :disabled="user.username === authUser.username"
                    @click="updateUser(user.username, !user.admin)"
                  >
                    {{
                      $t(
                        `admin.USERS.TABLE.${
                          user.admin ? 'REMOVE' : 'ADD'
                        }_ADMIN_RIGHTS`
                      )
                    }}
                  </button>
                </td>
              </tr>
            </tbody>
          </table>
          <Pagination
            v-if="pagination.page"
            path="/admin/users"
            :pagination="pagination"
            :query="query"
          />
          <ErrorMessage :message="errorMessages" v-if="errorMessages" />
          <button @click.prevent="$router.push('/admin')">
            {{ $t('admin.BACK_TO_ADMIN') }}
          </button>
        </div>
      </template>
    </Card>
  </div>
</template>

<script lang="ts">
  import {
    ComputedRef,
    computed,
    defineComponent,
    reactive,
    watch,
    capitalize,
    onBeforeMount,
  } from 'vue'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import AdminUsersSelects from '@/components/Administration/AdminUsersSelects.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { ROOT_STORE, USER_STORE, USERS_STORE } from '@/store/constants'
  import { IPagination, TPaginationPayload } from '@/types/api'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'AdminUsers',
    components: {
      AdminUsersSelects,
      Pagination,
      UserPicture,
    },
    setup() {
      const store = useStore()
      const route = useRoute()
      const router = useRouter()

      const sort: string[] = ['asc', 'desc']
      const order_by: string[] = [
        'admin',
        'created_at',
        'username',
        'workouts_count',
      ]
      let query: TPaginationPayload = reactive(getQuery(route.query))

      const authUser: ComputedRef<IUserProfile> = computed(
        () => store.getters[USER_STORE.GETTERS.AUTH_USER_PROFILE]
      )
      const users: ComputedRef<IUserProfile[]> = computed(
        () => store.getters[USERS_STORE.GETTERS.USERS]
      )
      const pagination: ComputedRef<IPagination> = computed(
        () => store.getters[USERS_STORE.GETTERS.USERS_PAGINATION]
      )
      const errorMessages: ComputedRef<string | string[] | null> = computed(
        () => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES]
      )

      function loadUsers(queryParams: TPaginationPayload) {
        store.dispatch(USERS_STORE.ACTIONS.GET_USERS, queryParams)
      }
      function getPage(page: string | (string | null)[] | null): number {
        return page && typeof page === 'string' && +page > 0 ? +page : 1
      }
      function getPerPage(perPage: string | (string | null)[] | null): number {
        return perPage && typeof perPage === 'string' && +perPage > 0
          ? +perPage
          : 10
      }
      function getOrder(order: string | (string | null)[] | null): string {
        return order && typeof order === 'string' && sort.includes(order)
          ? order
          : 'asc'
      }
      function getOrderBy(order: string | (string | null)[] | null): string {
        return order && typeof order === 'string' && order_by.includes(order)
          ? order
          : 'created_at'
      }
      function getQuery(query: LocationQuery): TPaginationPayload {
        return {
          page: getPage(query.page),
          per_page: getPerPage(query.per_page),
          order: getOrder(query.order),
          order_by: getOrderBy(query.order_by),
        }
      }
      function updateUser(username: string, admin: boolean) {
        store.dispatch(USERS_STORE.ACTIONS.UPDATE_USER, {
          username,
          admin,
        })
      }
      function reloadUsers(queryParam: string, queryValue: string) {
        query[queryParam] = queryValue
        if (queryParam === 'per_page') {
          query.page = 1
        }
        router.push({ path: '/admin/users', query })
      }

      onBeforeMount(() => loadUsers(query))

      watch(
        () => route.query,
        (newQuery: LocationQuery) => {
          query.page = getPage(newQuery.page)
          query.per_page = getPerPage(newQuery.per_page)
          query.order = getOrder(newQuery.order)
          query.order_by = getOrderBy(newQuery.order_by)
          loadUsers(query)
        }
      )

      return {
        authUser,
        errorMessages,
        pagination,
        order_by,
        query,
        sort,
        users,
        capitalize,
        reloadUsers,
        updateUser,
      }
    },
  })
</script>

<style lang="scss" scoped>
  @import '~@/scss/base.scss';
  #admin-users {
    .top-button {
      display: none;
    }
    table {
      td {
        font-size: 1.1em;
      }
    }
    .left-text {
      text-align: left;
    }
    ::v-deep(.user-picture) {
      img {
        height: 30px;
        width: 30px;
      }
      .no-picture {
        font-size: 2em;
      }
    }

    @media screen and (max-width: $small-limit) {
      .top-button {
        display: block;
        margin-bottom: $default-margin * 2;
      }
      .pagination-center {
        margin-top: -3 * $default-margin;
      }
    }
  }
</style>
