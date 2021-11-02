<template>
  <div id="admin-users" class="admin-card">
    <Card>
      <template #title>{{ capitalize($t('admin.USER', 0)) }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <AdminUsersSelects
          :sort="sortList"
          :order_by="orderByList"
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
                  <router-link :to="`/users/${user.username}`">
                    {{ user.username }}
                  </router-link>
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
                  {{
                    format(
                      getDateWithTZ(user.created_at, authUser.timezone),
                      'dd/MM/yyyy HH:mm'
                    )
                  }}
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
  import { format } from 'date-fns'
  import {
    ComputedRef,
    computed,
    defineComponent,
    reactive,
    watch,
    capitalize,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import { LocationQuery, useRoute, useRouter } from 'vue-router'

  import AdminUsersSelects from '@/components/Administration/AdminUsersSelects.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { ROOT_STORE, USER_STORE, USERS_STORE } from '@/store/constants'
  import { IPagination, TPaginationPayload } from '@/types/api'
  import { IUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getQuery, sortList } from '@/utils/api'
  import { getDateWithTZ } from '@/utils/dates'

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

      const orderByList: string[] = [
        'admin',
        'created_at',
        'username',
        'workouts_count',
      ]
      const defaultOrderBy = 'created_at'
      let query: TPaginationPayload = reactive(
        getQuery(route.query, orderByList, defaultOrderBy)
      )

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
          query = getQuery(newQuery, orderByList, defaultOrderBy, { query })
          loadUsers(query)
        }
      )

      onUnmounted(() => {
        store.dispatch(USERS_STORE.ACTIONS.EMPTY_USERS)
      })

      return {
        authUser,
        errorMessages,
        orderByList,
        pagination,
        query,
        sortList,
        users,
        capitalize,
        format,
        getDateWithTZ,
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
