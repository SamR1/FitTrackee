<template>
  <div id="user-moderation">
    <h1>{{ $t('user.PROFILE.SANCTIONS_RECEIVED') }}</h1>
    <div id="user-sanctions" v-if="authUser.sanctions_count">
      <div v-if="sanctionsLoading">
        <Loader />
      </div>
      <template v-else>
        <ul class="last-sanctions">
          <li v-for="sanction in sanctions" :key="sanction.id">
            <div>
              <router-link :to="`/profile/moderation/sanctions/${sanction.id}`">
                {{
                  $t(`user.PROFILE.SANCTIONS.${sanction.action_type}`, {
                    date: formatDate(
                      sanction.created_at,
                      displayOptions.timezone,
                      displayOptions.dateFormat
                    ),
                  })
                }}
              </router-link>
              <span
                v-if="sanction.appeal"
                class="info-box appeal"
                :class="{
                  approved: getSanctionStatus(sanction.appeal) === 'APPROVED',
                  rejected: getSanctionStatus(sanction.appeal) === 'REJECTED',
                }"
              >
                <i
                  class="fa"
                  :class="{
                    'fa-info-circle':
                      getSanctionStatus(sanction.appeal) !== 'REJECTED',
                    'fa-times':
                      getSanctionStatus(sanction.appeal) === 'REJECTED',
                  }"
                  aria-hidden="true"
                />
                {{
                  $t(
                    `user.PROFILE.SANCTION_APPEAL.${getSanctionStatus(sanction.appeal)}`
                  )
                }}
              </span>
            </div>
          </li>
        </ul>
        <Pagination
          :pagination="sanctionsPagination"
          path="/profile/moderation"
          :query="query"
        />
      </template>
    </div>
    <div v-else>
      <p class="no-sanctions">{{ $t('user.PROFILE.NO_SANCTIONS') }}</p>
    </div>
    <div>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import {
    computed,
    onBeforeMount,
    onUnmounted,
    reactive,
    toRefs,
    watch,
  } from 'vue'
  import type { ComputedRef, Reactive } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Loader from '@/components/Common/Loader.vue'
  import Pagination from '@/components/Common/Pagination.vue'
  import useApp from '@/composables/useApp'
  import { USERS_STORE } from '@/store/constants'
  import type { IPagination, TPaginationPayload } from '@/types/api'
  import type { IReportAction } from '@/types/reports'
  import type {
    IReportActionAppeal,
    IUserProfile,
    TUsersPayload,
  } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { defaultPage, getNumberQueryValue } from '@/utils/api'
  import { formatDate } from '@/utils/dates'

  interface Props {
    authUser: IUserProfile
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const { displayOptions } = useApp()

  let query: Reactive<TPaginationPayload> = reactive(getQuery(route.query))
  const sanctions: ComputedRef<IReportAction[]> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_SANCTIONS]
  )
  const sanctionsLoading: ComputedRef<boolean> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_SANCTIONS_LOADING]
  )
  const sanctionsPagination: ComputedRef<IPagination> = computed(
    () => store.getters[USERS_STORE.GETTERS.USER_SANCTIONS_PAGINATION]
  )

  function getQuery(newQuery: LocationQuery): TUsersPayload {
    const sanctionsQuery: TPaginationPayload = {}
    if (newQuery.page) {
      sanctionsQuery.page = getNumberQueryValue(newQuery.page, defaultPage)
    }
    return sanctionsQuery
  }
  function getSanctionStatus(
    appeal: IReportActionAppeal
  ): 'APPROVED' | 'IN_PROGRESS' | 'REJECTED' {
    if (appeal.updated_at) {
      switch (appeal.approved) {
        case true:
          return 'APPROVED'
        case false:
          return 'REJECTED'
        default:
          return 'IN_PROGRESS'
      }
    }
    return 'IN_PROGRESS'
  }
  function loadSanctions(payload: TUsersPayload) {
    store.dispatch(USERS_STORE.ACTIONS.GET_USER_SANCTIONS, {
      username: authUser.value.username,
      ...payload,
    })
  }

  watch(
    () => route.query,
    async (newQuery) => {
      query = getQuery(newQuery)
      loadSanctions(query)
    }
  )

  onBeforeMount(() => loadSanctions({}))
  onUnmounted(() =>
    store.commit(USERS_STORE.MUTATIONS.UPDATE_USER_SANCTIONS, [])
  )
</script>

<style lang="scss" scoped>
  @import '~@/scss/vars.scss';

  #user-moderation {
    padding: $default-padding 0;
    h1 {
      font-size: 1.05em;
      font-weight: bold;
    }
    #user-reports {
      dl {
        margin-bottom: 0;
      }
    }

    #user-sanctions {
      ul {
        list-style: square;
        li {
          margin-left: $default-margin;
          padding: $default-padding * 0.5;
          div {
            display: flex;
            flex-wrap: wrap;
            gap: $default-padding * 0.5;
          }
        }
      }
      .appeal {
        margin-top: -2px;
        padding: $default-padding * 0.5 $default-padding;
        &.approved {
          background: var(--success-background-color);
          color: var(--success-color);
        }
        &.rejected {
          background: var(--error-background-color);
          color: var(--error-color);
        }
      }
    }
    .no-sanctions {
      font-style: italic;
    }
  }
</style>
