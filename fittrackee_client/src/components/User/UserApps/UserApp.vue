<template>
  <div id="oauth2-app" class="description-list">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t(messageToDisplay)"
      @confirmAction="confirmAction(client.id)"
      @cancelAction="updateDisplayModal(false)"
    />
    <div v-if="client && client.client_id">
      <div
        class="info-box success-message"
        v-if="afterCreation || revocationSuccessful"
      >
        {{
          $t(
            afterCreation
              ? 'oauth2.APP_CREATED_SUCCESSFULLY'
              : 'oauth2.TOKENS_REVOKED'
          )
        }}
      </div>
      <dl>
        <dt>{{ $t('oauth2.APP.CLIENT_ID') }}:</dt>
        <dd>{{ client.client_id }}</dd>
        <dt v-if="afterCreation && client.client_secret">
          {{ $t('oauth2.APP.CLIENT_SECRET') }}:
        </dt>
        <dd>{{ client.client_secret }}</dd>
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
        <dd class="client-scopes">
          <span
            class="client-scope"
            v-for="scope in client.scope.split(' ')"
            :key="scope"
          >
            <code>{{ scope }}</code>
          </span>
        </dd>
      </dl>
      <div class="app-buttons">
        <button class="danger" @click="updateMessageToDisplay(false)">
          {{ $t('oauth2.REVOKE_ALL_TOKENS') }}
        </button>
        <button class="danger" @click="updateMessageToDisplay(true)">
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
    withDefaults,
    watch,
  } from 'vue'
  import { useRoute } from 'vue-router'

  import { OAUTH2_STORE, ROOT_STORE } from '@/store/constants'
  import { IOAuth2Client } from '@/types/oauth'
  import { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { getDateWithTZ } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
    afterCreation?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    afterCreation: false,
  })
  const route = useRoute()
  const store = useStore()

  const { afterCreation, authUser } = toRefs(props)
  const client: ComputedRef<IOAuth2Client> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENT]
  )
  const revocationSuccessful: ComputedRef<boolean> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.REVOCATION_SUCCESSFUL]
  )
  let displayModal: Ref<boolean> = ref(false)
  let messageToDisplay: Ref<string | null> = ref(null)

  onBeforeMount(() => {
    loadClient()
  })

  function loadClient() {
    // after creation, client is already in store
    if (
      !afterCreation.value &&
      route.params.id &&
      typeof route.params.id === 'string'
    ) {
      store.dispatch(OAUTH2_STORE.ACTIONS.GET_CLIENT_BY_ID, +route.params.id)
    }
  }
  function updateMessageToDisplay(forDelete: boolean) {
    messageToDisplay.value = forDelete
      ? 'oauth2.APP_DELETION_CONFIRMATION'
      : 'oauth2.TOKENS_REVOCATION_CONFIRMATION'
    updateDisplayModal(true)
  }
  function updateDisplayModal(value: boolean) {
    displayModal.value = value
    if (!value) {
      messageToDisplay.value = null
    }
  }
  function confirmAction(clientId: number) {
    if (messageToDisplay.value === 'oauth2.APP_DELETION_CONFIRMATION') {
      store.dispatch(OAUTH2_STORE.ACTIONS.DELETE_CLIENT, clientId)
    } else {
      store.dispatch(OAUTH2_STORE.ACTIONS.REVOKE_ALL_TOKENS, clientId)
    }
  }
  onUnmounted(() => {
    store.commit(ROOT_STORE.MUTATIONS.EMPTY_ERROR_MESSAGES)
    store.commit(OAUTH2_STORE.MUTATIONS.EMPTY_CLIENT)
    store.commit(OAUTH2_STORE.MUTATIONS.SET_REVOCATION_SUCCESSFUL, false)
  })

  watch(
    () => revocationSuccessful.value,
    (newValue) => {
      if (newValue) {
        updateDisplayModal(false)
      }
    }
  )
</script>

<style scoped lang="scss">
  @import '~@/scss/vars.scss';
  #oauth2-app {
    .app-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding;
    }
    .client-scopes {
      display: flex;
      flex-wrap: wrap;
      .client-scope {
        padding-right: $default-padding * 1.5;
      }
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
