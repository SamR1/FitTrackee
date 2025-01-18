<template>
  <div id="oauth2-apps-list">
    <h1 class="apps-list">{{ $t('oauth2.APPS_LIST') }}</h1>
    <ul v-if="clients.length > 0">
      <li v-for="client in clients" :key="client.client_id">
        <router-link :to="{ name: 'UserApp', params: { id: client.id } }">
          {{ client.name }}
        </router-link>
        <span class="app-issued-at">
          {{ $t('oauth2.APP.ISSUE_AT') }}
          <time>
            {{
              formatDate(
                client.issued_at,
                authUser.timezone,
                authUser.date_format
              )
            }}
          </time>
        </span>
      </li>
    </ul>
    <div class="no-apps" v-else>{{ $t('oauth2.NO_APPS') }}</div>
    <Pagination
      v-if="clients.length > 0"
      :pagination="pagination"
      path="/profile/apps"
      :query="query"
    />
    <div class="app-list-buttons">
      <button
        v-if="!authUser.suspended_at"
        @click="$router.push('/profile/apps/new')"
      >
        {{ $t('oauth2.NEW_APP') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { computed, onBeforeMount, toRefs, watch } from 'vue'
  import type { ComputedRef } from 'vue'
  import { useRoute } from 'vue-router'
  import type { LocationQuery } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import { OAUTH2_STORE } from '@/store/constants'
  import type { IPagination } from '@/types/api'
  import type { IOAuth2Client, IOauth2ClientsPayload } from '@/types/oauth'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { defaultPage, getNumberQueryValue } from '@/utils/api'
  import { formatDate } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()
  const { authUser } = toRefs(props)

  const store = useStore()
  const route = useRoute()

  let query: IOauth2ClientsPayload = getClientsQuery(route.query)

  const clients: ComputedRef<IOAuth2Client[]> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENTS]
  )
  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENTS_PAGINATION]
  )

  function getClientsQuery(newQuery: LocationQuery): IOauth2ClientsPayload {
    const clientsQuery: IOauth2ClientsPayload = {}
    if (newQuery.page) {
      clientsQuery.page = getNumberQueryValue(newQuery.page, defaultPage)
    }
    return clientsQuery
  }
  function loadClients(payload: IOauth2ClientsPayload) {
    store.dispatch(OAUTH2_STORE.ACTIONS.GET_CLIENTS, payload)
  }

  watch(
    () => route.query,
    async (newQuery) => {
      query = getClientsQuery(newQuery)
      loadClients(query)
    }
  )

  onBeforeMount(() => {
    loadClients(query)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #oauth2-apps-list {
    padding: 0 0 $default-padding;
    ul {
      list-style: square;

      li {
        padding-bottom: $default-padding;
      }
    }

    .app-issued-at {
      font-size: 0.85em;
      font-style: italic;
      padding-left: $default-padding;
    }
    .apps-list {
      font-size: 1.05em;
      font-weight: bold;
    }
    .app-list-buttons {
      display: flex;
      gap: $default-padding;
    }
    .no-apps {
      font-style: italic;
      padding-bottom: $default-padding * 2;
    }
  }
</style>
