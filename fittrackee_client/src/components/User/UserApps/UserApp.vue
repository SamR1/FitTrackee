<template>
  <div id="oauth2-app" class="description-list">
    <Modal
      v-if="displayModal"
      :title="$t('common.CONFIRMATION')"
      :message="$t(messageToDisplay)"
      @confirmAction="confirmAction(client.id)"
      @cancelAction="updateDisplayModal(false)"
      @keydown.esc="updateDisplayModal(false)"
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
        <dd>
          {{ client.client_id }}
          <i
            v-if="afterCreation && clipboardSupport"
            :class="`fa fa-${idCopied ? 'check' : 'copy'}`"
            aria-hidden="true"
            :title="$t('oauth2.COPY_TO_CLIPBOARD')"
            @click="copyIdToClipboard"
          >
          </i>
        </dd>
        <dt v-if="afterCreation && client.client_secret">
          {{ $t('oauth2.APP.CLIENT_SECRET') }}:
        </dt>
        <dd v-if="afterCreation && client.client_secret" class="app-secret">
          {{ client.client_secret }}
          <i
            v-if="clipboardSupport"
            :class="`fa fa-${secretCopied ? 'check' : 'copy'}`"
            aria-hidden="true"
            :title="$t('oauth2.COPY_TO_CLIPBOARD')"
            @click="copySecretToClipboard"
          >
          </i>
        </dd>
        <dt>{{ capitalize($t('oauth2.APP.ISSUE_AT')) }}:</dt>
        <dd>
          <time>
            {{
              formatDate(
                client.issued_at,
                authUser.timezone,
                authUser.date_format
              )
            }}
          </time>
        </dd>
        <dt>{{ $t('oauth2.APP.NAME') }}:</dt>
        <dd>{{ client.name }}</dd>
        <dt>{{ $t('oauth2.APP.DESCRIPTION') }}:</dt>
        <dd :class="{ 'no-description': !client.client_description }">
          {{
            client.client_description
              ? client.client_description
              : $t('common.NO_DESCRIPTION')
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
  import {
    capitalize,
    computed,
    onBeforeMount,
    toRefs,
    ref,
    onUnmounted,
    watch,
  } from 'vue'
  import type { ComputedRef, Ref } from 'vue'
  import { useRoute } from 'vue-router'

  import { OAUTH2_STORE } from '@/store/constants'
  import type { IOAuth2Client } from '@/types/oauth'
  import type { IAuthUserProfile } from '@/types/user'
  import { useStore } from '@/use/useStore'
  import { formatDate } from '@/utils/dates'

  interface Props {
    authUser: IAuthUserProfile
    afterCreation?: boolean
  }
  const props = withDefaults(defineProps<Props>(), {
    afterCreation: false,
  })
  const { afterCreation, authUser } = toRefs(props)

  const route = useRoute()
  const store = useStore()

  const displayModal: Ref<boolean> = ref(false)
  const messageToDisplay: Ref<string> = ref('')
  const idCopied: Ref<boolean> = ref(false)
  const secretCopied: Ref<boolean> = ref(false)
  const clipboardSupport: Ref<boolean> = ref(false)

  const client: ComputedRef<IOAuth2Client> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.CLIENT]
  )
  const revocationSuccessful: ComputedRef<boolean> = computed(
    () => store.getters[OAUTH2_STORE.GETTERS.REVOCATION_SUCCESSFUL]
  )

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
      messageToDisplay.value = ''
    }
  }
  function confirmAction(clientId: number) {
    if (messageToDisplay.value === 'oauth2.APP_DELETION_CONFIRMATION') {
      store.dispatch(OAUTH2_STORE.ACTIONS.DELETE_CLIENT, clientId)
    } else {
      store.dispatch(OAUTH2_STORE.ACTIONS.REVOKE_ALL_TOKENS, clientId)
    }
  }
  function copyIdToClipboard() {
    navigator.clipboard.writeText(client.value.client_id)
    idCopied.value = true
    secretCopied.value = false
    setTimeout(() => {
      idCopied.value = false
    }, 3000)
  }
  function copySecretToClipboard() {
    if (client.value.client_secret) {
      navigator.clipboard.writeText(client.value.client_secret)
      secretCopied.value = true
      idCopied.value = false
      setTimeout(() => {
        secretCopied.value = false
      }, 3000)
    }
  }

  watch(
    () => revocationSuccessful.value,
    (newValue) => {
      if (newValue) {
        updateDisplayModal(false)
      }
    }
  )

  onBeforeMount(() => {
    loadClient()
    if (navigator.clipboard) {
      clipboardSupport.value = true
    }
  })
  onUnmounted(() => {
    store.commit(OAUTH2_STORE.MUTATIONS.EMPTY_CLIENT)
    store.commit(OAUTH2_STORE.MUTATIONS.SET_REVOCATION_SUCCESSFUL, false)
  })
</script>

<style scoped lang="scss">
  @use '~@/scss/vars.scss' as *;
  #oauth2-app {
    .app-buttons {
      display: flex;
      flex-wrap: wrap;
      gap: $default-padding;
    }
    .app-secret {
      word-break: break-word;
    }
    .client-scopes {
      display: flex;
      flex-wrap: wrap;
      .client-scope {
        padding-right: $default-padding * 1.5;
      }
    }
    .fa-copy {
      font-size: 0.9em;
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
