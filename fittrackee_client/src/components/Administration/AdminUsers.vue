<template>
  <div id="admin-users" class="admin-card">
    <Card>
      <template #title>{{ capitalize($t('admin.USER', 0)) }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
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
                <td></td>
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
    watch,
    capitalize,
    onBeforeMount,
  } from 'vue'
  import { useRoute, LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import { ROOT_STORE, USER_STORE, USERS_STORE } from '@/store/constants'
  import { IPagination, IPaginationPayload } from '@/types/api'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'

  export default defineComponent({
    name: 'AdminUsers',
    components: {
      Pagination,
    },
    setup() {
      const store = useStore()
      const route = useRoute()

      const orders: string[] = ['asc', 'desc']
      const order_types: string[] = [
        'admin',
        'created_at',
        'username',
        'workouts_count',
      ]
      let query: IPaginationPayload = getQuery(route.query)

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

      function loadUsers(queryParams: IPaginationPayload) {
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
        return order && typeof order === 'string' && orders.includes(order)
          ? order
          : 'asc'
      }
      function getOrderBy(order_by: string | (string | null)[] | null): string {
        return order_by &&
          typeof order_by === 'string' &&
          order_types.includes(order_by)
          ? order_by
          : 'created_at'
      }
      function getQuery(query: LocationQuery): IPaginationPayload {
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

      onBeforeMount(() => loadUsers(query))

      watch(
        () => route.query,
        (newQuery) => {
          query = getQuery(newQuery)
          loadUsers(getQuery(newQuery))
        }
      )

      return {
        authUser,
        errorMessages,
        pagination,
        query,
        users,
        capitalize,
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

    @media screen and (max-width: $small-limit) {
      .top-button {
        display: block;
        margin-bottom: $default-margin * 2;
      }
    }
  }
</style>
