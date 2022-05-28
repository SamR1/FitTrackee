<template>
  <div id="oauth2-apps-list">
    <p class="apps-list">{{ $t('oauth2.APPS_LIST') }}</p>
    <ul v-if="clients.length > 0">
      <li v-for="client in clients" :key="client.client_id">
        <router-link :to="{ name: 'UserApp', params: { clientId: client.id } }">
          {{ client.name }}
        </router-link>
        <span class="app-issued-at">
          {{ $t('oauth2.APP.ISSUE_AT') }}
          {{
            format(
              getDateWithTZ(client.issued_at, authUser.timezone),
              'dd/MM/yyyy HH:mm'
            )
          }}
        </span>
      </li>
    </ul>
    <div class="no-apps" v-else>{{ $t('oauth2.NO_APPS') }}</div>
    <Pagination :pagination="pagination" path="/profile/apps" :query="query" />
    <div class="app-list-buttons">
      <button @click="$router.push('/profile/apps/new')">
        {{ $t('oauth2.NEW_APP') }}
      </button>
      <button @click="$router.push('/')">{{ $t('common.HOME') }}</button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import { ComputedRef, computed, onBeforeMount, toRefs, watch } from 'vue'
  import { LocationQuery, useRoute } from 'vue-router'

  import Pagination from '@/components/Common/Pagination.vue'
  import { OAUTH2_STORE } from '@/store/constants'
  import { IPagination } from '@/types/api'
  import { IOAuth2Client, IOauth2ClientsPayload } from '@/types/oauth'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { defaultPage, getNumberQueryValue } from '@/utils/api'
  import { getDateWithTZ } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const store = useStore()
  const route = useRoute()

  const { authUser } = toRefs(props)
  const clients: ComputedRef<IOAuth2Client[]> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENTS]
  )

  const pagination: ComputedRef<IPagination> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENTS_PAGINATION]
  )
  let query: IOauth2ClientsPayload = getClientsQuery(route.query)

  onBeforeMount(() => {
    loadClients(query)
  })

  function getClientsQuery(newQuery: LocationQuery): IOauth2ClientsPayload {
    let clientsQuery: IOauth2ClientsPayload = {}
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
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';

  #oauth2-apps-list {
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
    }
  }
</style>
