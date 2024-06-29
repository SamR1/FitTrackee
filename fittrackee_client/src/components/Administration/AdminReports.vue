<template>
  <div id="admin-reports" class="admin-card">
    <Card>
      <template #title>{{ $t('admin.APP_MODERATION.TITLE') }}</template>
      <template #content>
        <button class="top-button" @click.prevent="$router.push('/admin')">
          {{ $t('admin.BACK_TO_ADMIN') }}
        </button>
        <FilterSelects
          :sort="sortList"
          :order_by="orderByList"
          :query="query"
          message="admin.APP_MODERATION.ORDER_BY"
          @updateSelect="reloadReports"
        >
          <template #additionalFilters>
            <label>
              {{ $t('common.TYPE') }}:
              <select
                name="object_type"
                id="object_type"
                :value="query.object_type"
                @change="reloadReportsOnTypeChange"
              >
                <option value=""></option>
                <option
                  v-for="objectType in Object.keys(objectTypes)"
                  :value="objectType"
                  :key="objectType"
                >
                  {{ $t(objectTypes[objectType]) }}
                </option>
              </select>
            </label>
            <label>
              {{ $t('admin.APP_MODERATION.STATUS') }}:
              <select
                name="resolved"
                id="resolved"
                :value="query.resolved"
                @change="reloadReportsOnResolvedChange"
              >
                <option value=""></option>
                <option value="true">
                  {{ $t('admin.APP_MODERATION.RESOLVED.TRUE') }}
                </option>
                <option value="false">
                  {{ $t('admin.APP_MODERATION.RESOLVED.FALSE') }}
                </option>
              </select>
            </label>
          </template>
        </FilterSelects>
        <div class="no-reports" v-if="reports.length === 0">
          {{ $t('admin.APP_MODERATION.NO_REPORTS_FOUND') }}
        </div>
        <div class="responsive-table" v-else>
          <table>
            <thead>
              <tr>
                <th class="left-text">
                  {{ $t('admin.APP_MODERATION.REPORTED_USER') }}
                </th>
                <th class="left-text">
                  {{ $t('admin.APP_MODERATION.REPORTED_OBJECT') }}
                </th>
                <th class="left-text">
                  {{ $t('admin.APP_MODERATION.REPORTED_BY') }}
                </th>
                <th class="left-text">
                  {{
                    capitalize($t('admin.APP_MODERATION.ORDER_BY.CREATED_AT'))
                  }}
                </th>
                <th class="left-text">
                  {{ $t('admin.APP_MODERATION.RESOLVED.TRUE') }}
                </th>
                <th class="left-text">
                  {{ capitalize($t('common.LAST_UPDATED_ON')) }}
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="report in reports" :key="report.created_at">
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.APP_MODERATION.REPORTED_USER') }}
                  </span>
                  <router-link
                    class="link-with-image"
                    :to="`/admin/users/${report.reported_user.username}`"
                    v-if="report.reported_user"
                  >
                    <UserPicture :user="report.reported_user" />
                    {{ report.reported_user.username }}
                  </router-link>
                  <span class="deleted-object" v-else>
                    {{ $t('admin.DELETED_USER') }}
                  </span>
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.APP_MODERATION.REPORTED_OBJECT') }}
                  </span>
                  <router-link :to="`/admin/reports/${report.id}`">
                    {{ $t(objectTypes[report.object_type]) }}
                    <span v-if="getReportedObjectContent(report)">
                      ({{ getReportedObjectContent(report) }})
                    </span>
                  </router-link>
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.APP_MODERATION.REPORTED_BY') }}
                  </span>
                  <router-link
                    v-if="report.reported_by"
                    class="link-with-image"
                    :to="`/admin/users/${report.reported_by.username}`"
                  >
                    <UserPicture :user="report.reported_by" />
                    {{ report.reported_by.username }}
                  </router-link>
                  <span class="deleted-object" v-else>
                    {{ $t('admin.DELETED_USER') }}
                  </span>
                </td>
                <td>
                  <span class="cell-heading">
                    {{
                      capitalize($t('admin.APP_MODERATION.ORDER_BY.CREATED_AT'))
                    }}
                  </span>
                  <time>
                    {{ getDate(report.created_at) }}
                  </time>
                </td>
                <td>
                  <span class="cell-heading">
                    {{ $t('admin.APP_MODERATION.RESOLVED.TRUE') }}
                  </span>
                  <i
                    :class="`fa fa${report.resolved ? '-check' : ''}-square-o`"
                    aria-hidden="true"
                  />
                </td>
                <td>
                  <span class="cell-heading">
                    {{ capitalize($t('common.LAST_UPDATED_ON')) }}
                  </span>
                  <time v-if="report.updated_at">
                    {{ getDate(report.updated_at) }}
                  </time>
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

<script setup lang="ts">
  import {
    capitalize,
    computed,
    reactive,
    watch,
    onBeforeMount,
    onUnmounted,
  } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute, useRouter } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import FilterSelects from '@/components/Common/FilterSelects.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import UserPicture from '@/components/User/UserPicture.vue'
  import { AUTH_USER_STORE, REPORTS_STORE, ROOT_STORE } from '@/store/constants'
  import type { IPagination, TPaginationPayload } from '@/types/api'
  import type { IEquipmentError } from '@/types/equipments'
  import type { IReport } from '@/types/reports'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getQuery, sortList } from '@/utils/api'
  import { formatDate } from '@/utils/dates'

  const store = useStore()
  const route = useRoute()
  const router = useRouter()

  const orderByList: string[] = ['created_at', 'updated_at']
  const objectTypes: Record<string, string> = {
    comment: 'workouts.COMMENTS.COMMENTS',
    user: 'user.USER',
    workout: 'workouts.WORKOUT',
  }
  const defaultOrderBy = 'created_at'
  let query: TPaginationPayload = reactive(
    getQuery(route.query, orderByList, defaultOrderBy)
  )
  const authUser: ComputedRef<IAuthUserProfile> = computed(
    () => store.getters[AUTH_USER_STORE.GETTERS.AUTH_USER_PROFILE]
  )
  const reports: ComputedRef<IReport[]> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[REPORTS_STORE.GETTERS.REPORTS_PAGINATION]
  )
  const errorMessages: ComputedRef<string | string[] | IEquipmentError | null> =
    computed(() => store.getters[ROOT_STORE.GETTERS.ERROR_MESSAGES])
  const maxTextLength = 20

  onBeforeMount(() => loadReports(query))

  function loadReports(queryParams: TPaginationPayload) {
    store.dispatch(REPORTS_STORE.ACTIONS.GET_REPORTS, queryParams)
  }
  function reloadReportsOnTypeChange(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.value) {
      query.object_type = target.value
    } else {
      delete query.object_type
    }
    router.push({ path: '/admin/reports', query })
  }
  function reloadReportsOnResolvedChange(event: Event) {
    const target = event.target as HTMLInputElement
    if (target.value) {
      query.resolved = target.value
    } else {
      delete query.resolved
    }
    router.push({ path: '/admin/reports', query })
  }
  function reloadReports(queryParam: string, queryValue: string) {
    query[queryParam] = queryValue
    if (queryParam === 'per_page') {
      query.page = 1
    }
    router.push({ path: '/admin/reports', query })
  }
  function getDate(dateToFormat: string) {
    return formatDate(
      dateToFormat,
      authUser.value.timezone,
      authUser.value.date_format
    )
  }
  function getReportedObjectContent(report: IReport): string {
    let text: string | undefined
    switch (report.object_type) {
      case 'workout':
        text = report.reported_workout?.title
        break
      case 'comment':
        // in reports, comment is always returned by the API
        text = report.reported_comment?.text || ''
        break
      default:
        text = ''
    }
    if (text) {
      return text.length > maxTextLength
        ? `${text.substring(0, maxTextLength - 1)}…`
        : text
    }
    return ''
  }

  onUnmounted(() => {
    store.dispatch(REPORTS_STORE.ACTIONS.EMPTY_REPORTS)
  })

  watch(
    () => route.query,
    (newQuery: LocationQuery) => {
      query = getQuery(newQuery, orderByList, defaultOrderBy, { query })

      loadReports(query)
    }
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';
  #admin-reports {
    .top-button {
      display: none;
    }

    .no-reports {
      display: flex;
      justify-content: center;
      padding: $default-padding * 2 0;
      font-weight: bold;
    }

    table {
      td {
        font-size: 1.1em;
      }
    }
    .left-text {
      text-align: left;
    }

    .link-with-image {
      display: flex;
      align-items: center;

      ::v-deep(.user-picture) {
        min-width: 40px;
        img {
          height: 30px;
          width: 30px;
        }
        .no-picture {
          font-size: 2em;
        }
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

      .link-with-image {
        justify-content: center;
      }
    }
  }
</style>
