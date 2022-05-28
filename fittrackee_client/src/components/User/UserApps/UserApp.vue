<template>
  <div id="oauth2-app" class="description-list">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t('oauth2.APP_DELETION_CONFIRMATION')"
      @confirmAction="deleteClient(client.id)"
      @cancelAction="updateDisplayModal(false)"
    />
    <div v-if="client && client.client_id">
      <dl>
        <dt>{{ $t('oauth2.APP.CLIENT_ID') }}:</dt>
        <dd>{{ client.client_id }}</dd>
        <dt>{{ capitalize($t('oauth2.APP.ISSUE_AT')) }}:</dt>
        <dd>
          {{
            format(
              getDateWithTZ(client.issued_at, authUser.timezone),
              'dd/MM/yyyy HH:mm'
            )
          }}
        </dd>
        <dt>{{ $t('oauth2.APP.NAME') }}:</dt>
        <dd>{{ client.name }}</dd>
        <dt>{{ $t('oauth2.APP.DESCRIPTION') }}:</dt>
        <dd :class="{ 'no-description': !client.client_description }">
          {{
            client.client_description
              ? client.client_description
              : $t('oauth2.NO_DESCRIPTION')
          }}
        </dd>
        <dt>{{ $t('oauth2.APP.URL') }}:</dt>
        <dd>{{ client.website }}</dd>
        <dt>{{ $t('oauth2.APP.REDIRECT_URL') }}:</dt>
        <dd>
          {{ client.redirect_uris.length > 0 ? client.redirect_uris[0] : '' }}
        </dd>
        <dt>{{ $t('oauth2.APP.SCOPE.LABEL') }}:</dt>
        <dd>{{ client.scope }}</dd>
      </dl>
      <div class="app-buttons">
        <button class="danger" @click="updateDisplayModal(true)">
          {{ $t('oauth2.DELETE_APP') }}
        </button>
        <button @click="$router.push('/profile/apps')">
          {{ $t('buttons.BACK') }}
        </button>
      </div>
    </div>
    <div v-else>
      <p class="no-app">{{ $t('oauth2.NO_APP') }}</p>
      <button @click="$router.push('/profile/apps')">
        {{ $t('buttons.BACK') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
  import { format } from 'date-fns'
  import {
    ComputedRef,
    Ref,
    capitalize,
    computed,
    onBeforeMount,
    toRefs,
    ref,
    onUnmounted,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
  import { IOAuth2Client } from '@/types/oauth'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDateWithTZ } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
  }
  const props = defineProps<Props>()

  const route = useRoute()
  const store = useStore()

  const { authUser } = toRefs(props)
  const client: ComputedRef<IOAuth2Client> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENT]
  )
  let displayModal: Ref<boolean> = ref(false)

  onBeforeMount(() => {
    loadClient()
  })

  function loadClient() {
    if (route.params.clientId && typeof route.params.clientId === 'string') {
      store.dispatch(OAUTH2_STORE.ACTIONS.GET_CLIENT, route.params.clientId)
    }
  }
  function deleteClient(clientId: number) {
    store.dispatch(OAUTH2_STORE.ACTIONS.DELETE_CLIENT, clientId)
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
  }
  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(OAUTH2_STORE.MUTATIONS.EMPTY_CLIENT)
  })
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  #oauth2-app {
    .app-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding;
    }
    .no-description {
      font-style: italic;
    }
    .no-app {
      font-style: italic;
      padding: $default-padding 0;
    }
  }
</style>
